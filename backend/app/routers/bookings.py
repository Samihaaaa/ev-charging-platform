from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import SessionLocal
from ..auth import get_current_user

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

    user = db.query(models.User).filter(
        models.User.email == current_user
    ).first()

    existing = db.query(models.Booking).filter(
        models.Booking.station_id == booking.station_id,
        models.Booking.time_slot == booking.time_slot
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="This charging slot is already booked"
        )

    new_booking = models.Booking(
        user_id=user.id,
        station_id=booking.station_id,
        time_slot=booking.time_slot
    )

    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    return new_booking


# GET BOOKINGS WITH USER EMAIL
@router.get("/")
def get_bookings(db: Session = Depends(get_db)):

    bookings = db.query(models.Booking, models.User).join(
        models.User,
        models.Booking.user_id == models.User.id
    ).all()

    result = []

    for booking, user in bookings:
        result.append({
            "booking_id": booking.id,
            "user_email": user.email,
            "station_id": booking.station_id,
            "time_slot": booking.time_slot
        })

    return result


# MY BOOKINGS
@router.get("/my-bookings")
def my_bookings(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):

    user = db.query(models.User).filter(
        models.User.email == current_user
    ).first()

    bookings = db.query(models.Booking).filter(
        models.Booking.user_id == user.id
    ).all()

    return bookings


# CANCEL BOOKING
@router.delete("/{booking_id}")
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):

    user = db.query(models.User).filter(
        models.User.email == current_user
    ).first()

    booking = db.query(models.Booking).filter(
        models.Booking.id == booking_id
    ).first()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.user_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to cancel this booking"
        )

    db.delete(booking)
    db.commit()

    return {"message": "Booking cancelled successfully"}