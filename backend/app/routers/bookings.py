from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import SessionLocal
from ..auth import get_current_user
from ..core.config import STRIPE_SECRET_KEY
from ..services.stripe_service import get_stripe_client
from ..core.db_compat import table_has_column

router = APIRouter(prefix="/bookings", tags=["Bookings"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# CREATE BOOKING
@router.post("/")
def create_booking(
    booking: schemas.BookingCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    # In monetized mode, the UI should create a Stripe Checkout session first.
    if STRIPE_SECRET_KEY:
        raise HTTPException(
            status_code=400,
            detail="Use POST /payments/checkout-session for paid bookings",
        )

    user = db.query(models.User).filter(models.User.email == current_user).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    has_booking_status = table_has_column("bookings", "status")
    has_amount_cents = table_has_column("bookings", "amount_cents")
    has_currency = table_has_column("bookings", "currency")
    has_price_cents = table_has_column("stations", "price_cents")

    # Conflict check: if `bookings.status` exists, only treat pending/paid as blocking.
    existing_query = (
        db.query(models.Booking.id)
        .filter(
            models.Booking.station_id == booking.station_id,
            models.Booking.time_slot == booking.time_slot,
        )
    )
    if has_booking_status:
        existing_query = existing_query.filter(models.Booking.status.in_(["pending", "paid"]))

    existing = existing_query.first()
    if existing:
        raise HTTPException(status_code=400, detail="This charging slot is already booked")

    # Station price for monetization (if configured in DB).
    if has_price_cents:
        station_row = (
            db.query(models.ChargingStation.id, models.ChargingStation.price_cents)
            .filter(models.ChargingStation.id == booking.station_id)
            .first()
        )
        if not station_row:
            raise HTTPException(status_code=404, detail="Station not found")
        station_price_cents = station_row.price_cents or 0
    else:
        station_row = (
            db.query(models.ChargingStation.id)
            .filter(models.ChargingStation.id == booking.station_id)
            .first()
        )
        if not station_row:
            raise HTTPException(status_code=404, detail="Station not found")
        station_price_cents = 0

    # Dev/free fallback: mark as paid immediately when Stripe isn't configured.
    booking_data: dict = {
        "user_id": user.id,
        "station_id": booking.station_id,
        "time_slot": booking.time_slot,
    }
    if has_booking_status:
        booking_data["status"] = "paid"
    if has_amount_cents:
        booking_data["amount_cents"] = station_price_cents
    if has_currency:
        booking_data["currency"] = "usd"

    new_booking = models.Booking(**booking_data)
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    return new_booking


# GET BOOKINGS WITH USER EMAIL
@router.get("/")
def get_bookings(db: Session = Depends(get_db)):
    has_booking_status = table_has_column("bookings", "status")

    # Select only columns that are guaranteed to exist in older DBs.
    if has_booking_status:
        rows = (
            db.query(
                models.Booking.id,
                models.User.email,
                models.Booking.station_id,
                models.Booking.time_slot,
                models.Booking.status,
            )
            .join(models.User, models.Booking.user_id == models.User.id)
            .all()
        )
        return [
            {
                "booking_id": r.id,
                "user_email": r.email,
                "station_id": r.station_id,
                "time_slot": r.time_slot,
                "status": r.status,
            }
            for r in rows
        ]

    rows = (
        db.query(
            models.Booking.id,
            models.User.email,
            models.Booking.station_id,
            models.Booking.time_slot,
        )
        .join(models.User, models.Booking.user_id == models.User.id)
        .all()
    )
    return [
        {
            "booking_id": r.id,
            "user_email": r.email,
            "station_id": r.station_id,
            "time_slot": r.time_slot,
            "status": "paid",  # legacy DBs don't track status; treat as paid for display
        }
        for r in rows
    ]


# MY BOOKINGS (with authentication)
@router.get("/my-bookings")
def my_bookings(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):

    user = db.query(models.User).filter(
        models.User.email == current_user
    ).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    has_booking_status = table_has_column("bookings", "status")

    if has_booking_status:
        rows = (
            db.query(
                models.Booking.id,
                models.Booking.station_id,
                models.Booking.time_slot,
                models.Booking.status,
            )
            .filter(
                models.Booking.user_id == user.id,
                models.Booking.status.in_(["pending", "paid"]),
            )
            .all()
        )
        return [
            {
                "id": r.id,
                "station_id": r.station_id,
                "time_slot": r.time_slot,
                "status": r.status,
            }
            for r in rows
        ]

    rows = (
        db.query(
            models.Booking.id,
            models.Booking.station_id,
            models.Booking.time_slot,
        )
        .filter(models.Booking.user_id == user.id)
        .all()
    )
    return [
        {
            "id": r.id,
            "station_id": r.station_id,
            "time_slot": r.time_slot,
            "status": "paid",
        }
        for r in rows
    ]


# MY BOOKINGS (demo - without authentication)
@router.get("/my-bookings/demo")
def my_bookings_demo(db: Session = Depends(get_db)):
    """
    Get bookings for demo user without authentication.
    Returns confirmed bookings with station names.
    """
    try:
        # ALWAYS use user_id = 1 for consistency
        user_id = 1
        print(f"Fetching bookings for user_id: {user_id}")
        
        # Ensure user exists
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            # Create demo user with ID = 1 if none exists
            user = models.User(id=user_id, email="demo@example.com", password="demo")
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"Created demo user with ID: {user.id}")

        has_booking_status = table_has_column("bookings", "status")

        if has_booking_status:
            # Query bookings with station names for user_id = 1
            rows = (
                db.query(
                    models.Booking.id,
                    models.Booking.station_id,
                    models.Booking.time_slot,
                    models.Booking.status,
                    models.ChargingStation.name,
                )
                .join(models.ChargingStation, models.Booking.station_id == models.ChargingStation.id)
                .filter(
                    models.Booking.user_id == user_id,
                    models.Booking.status == "confirmed",  # Only confirmed bookings
                )
                .all()
            )
            
            print(f"Found {len(rows)} confirmed bookings for user_id: {user_id}")
            
            bookings = [
                {
                    "id": r.id,
                    "station_id": r.station_id,
                    "station_name": r.name,  # Include station name
                    "time_slot": r.time_slot,
                    "status": r.status,
                }
                for r in rows
            ]
            
            print(f"Returning bookings: {bookings}")
            return bookings
        else:
            # Legacy DB without status
            rows = (
                db.query(
                    models.Booking.id,
                    models.Booking.station_id,
                    models.Booking.time_slot,
                    models.ChargingStation.name,
                )
                .join(models.ChargingStation, models.Booking.station_id == models.ChargingStation.id)
                .filter(models.Booking.user_id == user_id)
                .all()
            )
            
            print(f"Found {len(rows)} bookings for user_id: {user_id} (legacy DB)")
            
            bookings = [
                {
                    "id": r.id,
                    "station_id": r.station_id,
                    "station_name": r.name,  # Include station name
                    "time_slot": r.time_slot,
                    "status": "confirmed",  # Default to confirmed for legacy
                }
                for r in rows
            ]
            
            print(f"Returning legacy bookings: {bookings}")
            return bookings

    except Exception as e:
        print(f"Error fetching demo bookings: {e}")
        import traceback
        traceback.print_exc()
        return []  # Return empty list on error


# CANCEL BOOKING (with authentication)
@router.delete("/{booking_id}")
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):

    user = db.query(models.User).filter(
        models.User.email == current_user
    ).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    has_booking_status = table_has_column("bookings", "status")
    has_payment_intent = table_has_column("bookings", "payment_intent_id")

    if has_booking_status:
        if has_payment_intent:
            booking_row = (
                db.query(
                    models.Booking.id,
                    models.Booking.user_id,
                    models.Booking.status,
                    models.Booking.payment_intent_id,
                )
                .filter(models.Booking.id == booking_id)
                .first()
            )
        else:
            booking_row = (
                db.query(
                    models.Booking.id,
                    models.Booking.user_id,
                    models.Booking.status,
                )
                .filter(models.Booking.id == booking_id)
                .first()
            )
    else:
        booking_row = (
            db.query(
                models.Booking.id,
                models.Booking.user_id,
            )
            .filter(models.Booking.id == booking_id)
            .first()
        )

    if not booking_row:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking_row.user_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to cancel this booking"
        )

    if has_booking_status:
        # If the booking is already paid, attempt refund when Stripe is configured.
        if (
            booking_row.status == "paid"
            and has_payment_intent
            and booking_row.payment_intent_id
            and STRIPE_SECRET_KEY
        ):
            stripe_client = get_stripe_client()
            stripe_client.refunds.create(payment_intent=booking_row.payment_intent_id)

        db.query(models.Booking).filter(models.Booking.id == booking_id).update(
            {"status": "cancelled"}
        )
        db.commit()
    else:
        # Legacy DBs don't track status/payment. For compatibility, just delete.
        db.query(models.Booking).filter(models.Booking.id == booking_id).delete()
        db.commit()

    return {"message": "Booking cancelled successfully"}


# CANCEL BOOKING (strict implementation)
@router.delete("/bookings/{booking_id}")
def cancel_booking(booking_id: int, db: Session = Depends(get_db)):
    print("Received booking_id:", booking_id)
    print("Cancel endpoint called - no authentication required for demo mode")

    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()

    if not booking:
        print("Booking NOT FOUND")
        raise HTTPException(status_code=404, detail="Booking not found")

    booking.status = "cancelled"
    booking.payment_status = "refunded"

    db.commit()
    db.refresh(booking)

    print("Booking cancelled:", booking.id, "status:", booking.status, "payment_status:", booking.payment_status)

    return {"message": "Booking cancelled successfully", "payment_status": "refunded"}


# CANCEL BOOKING (alternative endpoint - without authentication)
@router.delete("/{booking_id}/cancel")
def cancel_booking_demo(
    booking_id: int,
    db: Session = Depends(get_db),
):
    """
    Cancel booking without authentication for demo purposes.
    Sets status to 'cancelled' to free the slot.
    """
    has_booking_status = table_has_column("bookings", "status")

    if has_booking_status:
        booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        # Update status to cancelled to free the slot
        booking.status = "cancelled"
        db.commit()
        
        return {
            "status": "success",
            "message": "Booking cancelled successfully",
            "booking_id": booking_id,
            "slot_freed": booking.time_slot
        }
    else:
        # For legacy DBs without status, delete the booking
        booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        time_slot = booking.time_slot
        db.delete(booking)
        db.commit()
        
        return {
            "status": "success", 
            "message": "Booking cancelled successfully",
            "booking_id": booking_id,
            "slot_freed": time_slot
        }