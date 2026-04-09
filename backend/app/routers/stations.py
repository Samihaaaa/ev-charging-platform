from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal
from .. import models, schemas
from ..core.db_compat import table_has_column

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
    station_data = station.dict()
    # Backward-compatible: ignore `price_inr` if the DB doesn't have it yet.
    if not table_has_column("stations", "price_inr"):
        station_data.pop("price_inr", None)

    new_station = models.ChargingStation(**station_data)

    db.add(new_station)
    db.commit()
    db.refresh(new_station)

    return new_station


# GET ALL STATIONS
@router.get("/")
def get_stations(db: Session = Depends(get_db)):
    """
    Get all EV charging stations from the database.
    Returns a list of stations with all required fields for the frontend.
    """
    try:
        # Backward-compatible: older DBs may not have `price_inr`.
        has_price_column = table_has_column("stations", "price_inr")
        
        if has_price_column:
            stations = db.query(models.ChargingStation).all()
        else:
            # Fallback for older databases without price_inr
            rows = (
                db.query(
                    models.ChargingStation.id,
                    models.ChargingStation.name,
                    models.ChargingStation.latitude,
                    models.ChargingStation.longitude,
                    models.ChargingStation.charger_type,
                    models.ChargingStation.power_kw,
                )
                .all()
            )
            
            stations = [
                {
                    "id": r.id,
                    "name": r.name,
                    "latitude": r.latitude,
                    "longitude": r.longitude,
                    "charger_type": r.charger_type,
                    "power_kw": r.power_kw,
                    "price_inr": 0,  # Default price for older DBs
                }
                for r in rows
            ]
        
        # Ensure we always return a list
        if not stations:
            print("No stations found in database")
            return []
        
        print(f"Returning {len(stations)} stations")
        return stations
        
    except Exception as e:
        print(f"Error fetching stations: {e}")
        # Return empty list on error to prevent frontend crashes
        return []


# AVAILABLE SLOTS
@router.get("/{station_id}/available-slots")
def available_slots(station_id: int, db: Session = Depends(get_db)):
    has_price = table_has_column("stations", "price_inr")
    if has_price:
        station = (
            db.query(models.ChargingStation)
            .filter(models.ChargingStation.id == station_id)
            .first()
        )
        if not station:
            raise HTTPException(status_code=404, detail="Station not found")
        price_inr = station.price_inr or 0
    else:
        station_row = (
            db.query(models.ChargingStation.id)
            .filter(models.ChargingStation.id == station_id)
            .first()
        )
        if not station_row:
            raise HTTPException(status_code=404, detail="Station not found")
        price_inr = 0

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

    if table_has_column("bookings", "status"):
        # Only block slots for confirmed/paid bookings (exclude cancelled)
        confirmed_bookings = (
            db.query(models.Booking.time_slot)
            .filter(
                models.Booking.station_id == station_id,
                models.Booking.status.in_(["confirmed", "paid"]),  # Include both confirmed and paid
            )
            .all()
        )
        print(f"Active bookings for station {station_id} (confirmed/paid only): {len(confirmed_bookings)}")
        booked = confirmed_bookings
    else:
        # For older DBs without status, assume all bookings are active
        booked = (
            db.query(models.Booking.time_slot)
            .filter(models.Booking.station_id == station_id)
            .all()
        )
        print(f"All bookings for station {station_id} (legacy DB): {len(booked)}")

    booked = [slot[0] for slot in booked]
    print(f"Booked slots for station {station_id}: {booked}")

    available = [slot for slot in all_slots if slot not in booked]

    return {
        "station_id": station_id,
        "price_inr": price_inr,
        "all_slots": all_slots,
        "available_slots": available,
    }