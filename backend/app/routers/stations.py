from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import SessionLocal
from .. import models, schemas

router = APIRouter(prefix="/stations", tags=["Stations"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# CREATE STATION
@router.post("/")
def create_station(station: schemas.StationCreate, db: Session = Depends(get_db)):

    new_station = models.ChargingStation(**station.dict())

    db.add(new_station)
    db.commit()
    db.refresh(new_station)

    return new_station


# GET ALL STATIONS
@router.get("/")
def get_stations(db: Session = Depends(get_db)):

    stations = db.query(models.ChargingStation).all()

    return stations


# AVAILABLE SLOTS
@router.get("/{station_id}/available-slots")
def available_slots(station_id: int, db: Session = Depends(get_db)):

    all_slots = [
        "9am-10am",
        "10am-11am",
        "11am-12pm",
        "12pm-1pm",
        "1pm-2pm",
        "2pm-3pm",
        "3pm-4pm",
        "4pm-5pm",
        "5pm-6pm"
    ]

    booked = db.query(models.Booking.time_slot).filter(
        models.Booking.station_id == station_id
    ).all()

    booked = [slot[0] for slot in booked]

    available = [slot for slot in all_slots if slot not in booked]

    return {
        "station_id": station_id,
        "available_slots": available
    }