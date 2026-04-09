from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Any, Dict, Optional

import stripe

from .. import models, schemas
from ..auth import get_current_user
from ..core.config import (
    STRIPE_CURRENCY,
    STRIPE_SECRET_KEY,
    STRIPE_WEBHOOK_SECRET,
    FRONTEND_SUCCESS_URL,
    FRONTEND_CANCEL_URL,
    USE_MOCK_PAYMENT,
)
from ..database import SessionLocal
from ..services.stripe_service import get_stripe_client
from ..core.db_compat import table_has_column

router = APIRouter(prefix="/payments", tags=["Payments"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/checkout-session")
def create_checkout_session(
    payload: schemas.CheckoutSessionCreate,
    db: Session = Depends(get_db),
):
    """
    Simulate payment checkout session without authentication.
    Always succeeds and creates a booking.
    """
    try:
        # ALWAYS use user_id = 1 for consistency in demo mode
        user = db.query(models.User).filter(models.User.id == 1).first()
        if not user:
            # Create a default user with ID = 1 for demo
            user = models.User(id=1, email="demo@example.com", password="demo")
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"Created demo user with ID: {user.id}")
        else:
            print(f"Using existing demo user with ID: {user.id}")

        has_booking_status = table_has_column("bookings", "status")
        has_amount_cents = table_has_column("bookings", "amount_cents")
        has_currency = table_has_column("bookings", "currency")
        has_price_inr = table_has_column("stations", "price_inr")

        # SLOT LOCKING: Check if slot is already booked
        existing_query = (
            db.query(models.Booking.id)
            .filter(
                models.Booking.station_id == payload.station_id,
                models.Booking.time_slot == payload.time_slot,
            )
        )
        if has_booking_status:
            existing_query = existing_query.filter(models.Booking.status.in_(["confirmed", "paid"]))

        existing = existing_query.first()
        if existing:
            return {
                "status": "error",
                "error": "Slot already booked"
            }

        # Get station price (use price_inr if available, otherwise default)
        if has_price_inr:
            station_row = (
                db.query(models.ChargingStation.id, models.ChargingStation.price_inr)
                .filter(models.ChargingStation.id == payload.station_id)
                .first()
            )
            if not station_row:
                raise HTTPException(status_code=404, detail="Station not found")
            station_price = station_row.price_inr or 500  # Default to 500 INR
        else:
            station_row = (
                db.query(models.ChargingStation.id)
                .filter(models.ChargingStation.id == payload.station_id)
                .first()
            )
            if not station_row:
                raise HTTPException(status_code=404, detail="Station not found")
            station_price = 500  # Default price

        # BOOKING CREATION: Create booking with confirmed status
        booking_data: dict = {
            "user_id": 1,  # ALWAYS use user_id = 1 for consistency
            "station_id": payload.station_id,
            "time_slot": payload.time_slot,
        }
        if has_booking_status:
            booking_data["status"] = "confirmed"
        if has_amount_cents:
            booking_data["amount_cents"] = station_price * 100  # Convert to cents
        if has_currency:
            booking_data["currency"] = "inr"

        print(f"Creating booking with user_id: {booking_data['user_id']}, station_id: {booking_data['station_id']}, slot: {booking_data['time_slot']}")

        new_booking = models.Booking(**booking_data)
        db.add(new_booking)
        db.commit()
        db.refresh(new_booking)
        
        print(f"Booking created successfully with ID: {new_booking.id}, status: {getattr(new_booking, 'status', 'unknown')}")

        # SIMULATED PAYMENT SUCCESS
        return {
            "status": "success",
            "payment_status": "paid",
            "booking_status": "confirmed",
            "booking_id": new_booking.id,
            "payment_id": f"mock_payment_{new_booking.id}",
            "amount": station_price,
            "currency": "INR"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stripe-webhook")
async def stripe_webhook(request: Request):
    if not STRIPE_WEBHOOK_SECRET:
        raise HTTPException(status_code=500, detail="STRIPE_WEBHOOK_SECRET is not configured")

    payload: bytes = await request.body()
    sig_header = request.headers.get("stripe-signature")
    if not sig_header:
        raise HTTPException(status_code=400, detail="Missing stripe signature")

    try:
        event: Dict[str, Any] = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=STRIPE_WEBHOOK_SECRET,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid webhook signature: {str(e)}")

    # Create a DB session per request (simple + consistent with the rest of the app).
    db: Session = SessionLocal()
    try:
        event_type = event.get("type")
        data_object = event.get("data", {}).get("object", {})

        def get_booking_id_from_metadata() -> Optional[int]:
            metadata = data_object.get("metadata") or {}
            booking_id = metadata.get("booking_id")
            if booking_id is None:
                return None
            try:
                return int(booking_id)
            except ValueError:
                return None

        booking_id = get_booking_id_from_metadata()
        if not booking_id:
            return {"received": True}

        booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
        if not booking:
            return {"received": True}

        if event_type == "checkout.session.completed":
            # Only confirm bookings that are still pending.
            if booking.status == "pending":
                payment_intent_id = data_object.get("payment_intent")
                booking.status = "paid"
                booking.payment_intent_id = payment_intent_id
                booking.checkout_session_id = data_object.get("id") or booking.checkout_session_id
                db.commit()

        elif event_type in ("checkout.session.async_payment_failed", "checkout.session.expired"):
            if booking.status in ("pending", "paid"):
                booking.status = "cancelled"
                db.commit()

        return {"received": True}
    finally:
        db.close()

