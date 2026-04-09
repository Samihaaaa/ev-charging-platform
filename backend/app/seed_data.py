"""
Database seeding module for EV charging stations.
Automatically seeds the database with realistic Bangalore EV charging stations when empty.
"""

import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from .database import SessionLocal
from . import models

# Get logger without configuring at module level to avoid import conflicts
logger = logging.getLogger(__name__)

def get_bangalore_ev_stations() -> List[Dict[str, Any]]:
    """
    Returns a list of realistic Bangalore EV charging stations with proper coordinates.
    All coordinates are verified to be within Bangalore metropolitan area.
    """
    return [
        {
            "name": "MG Road Charger",
            "latitude": 12.975,
            "longitude": 77.605,
            "charger_type": "DC Fast",
            "power_kw": 150,
            "price_inr": 800
        },
        {
            "name": "Indiranagar Charging Point",
            "latitude": 12.9784,
            "longitude": 77.6408,
            "charger_type": "AC",
            "power_kw": 22,
            "price_inr": 400
        },
        {
            "name": "Whitefield Supercharger",
            "latitude": 12.9698,
            "longitude": 77.7499,
            "charger_type": "DC Fast",
            "power_kw": 250,
            "price_inr": 1200
        },
        {
            "name": "Electronic City Station",
            "latitude": 12.8452,
            "longitude": 77.6602,
            "charger_type": "AC",
            "power_kw": 22,
            "price_inr": 350
        },
        {
            "name": "Koramangala EV Hub",
            "latitude": 12.9352,
            "longitude": 77.6245,
            "charger_type": "DC Fast",
            "power_kw": 120,
            "price_inr": 900
        },
        {
            "name": "Yelahanka Charging Point",
            "latitude": 13.1007,
            "longitude": 77.5963,
            "charger_type": "AC",
            "power_kw": 11,
            "price_inr": 300
        },
        {
            "name": "Jayanagar Eco Station",
            "latitude": 12.9250,
            "longitude": 77.5938,
            "charger_type": "DC Fast",
            "power_kw": 60,
            "price_inr": 700
        },
        {
            "name": "HSR Layout Supercharger",
            "latitude": 12.9121,
            "longitude": 77.6446,
            "charger_type": "DC Fast",
            "power_kw": 200,
            "price_inr": 1000
        },
        {
            "name": "Malleshwaram Hub",
            "latitude": 13.0031,
            "longitude": 77.5700,
            "charger_type": "AC",
            "power_kw": 22,
            "price_inr": 450
        },
        {
            "name": "Marathahalli Fast Charge",
            "latitude": 12.9569,
            "longitude": 77.7011,
            "charger_type": "DC Fast",
            "power_kw": 150,
            "price_inr": 850
        },
        {
            "name": "Bannerghatta Road Station",
            "latitude": 12.8764,
            "longitude": 77.5953,
            "charger_type": "AC",
            "power_kw": 22,
            "price_inr": 380
        },
        {
            "name": "Domlur Charging Center",
            "latitude": 12.9634,
            "longitude": 77.6371,
            "charger_type": "DC Fast",
            "power_kw": 100,
            "price_inr": 750
        }
    ]

def seed_stations(db: Session = None) -> bool:
    """
    Seeds the database with Bangalore EV charging stations if the stations table is empty.
    
    Args:
        db: Database session. If None, creates a new session.
        
    Returns:
        bool: True if seeding was successful or not needed, False if there was an error.
    """
    should_close_db = False
    if db is None:
        try:
            db = SessionLocal()
            should_close_db = True
        except Exception as e:
            print(f"Failed to create database session: {e}")
            return False
    
    try:
        # Check if ChargingStation model exists and is accessible
        if not hasattr(models, 'ChargingStation'):
            print("ChargingStation model not found in models module")
            return False
        
        # Check if stations table is empty
        try:
            station_count = db.query(models.ChargingStation).count()
        except Exception as e:
            print(f"Failed to query stations table: {e}")
            # Try to create table first
            try:
                from .database import Base, engine
                Base.metadata.create_all(bind=engine)
                station_count = db.query(models.ChargingStation).count()
            except Exception as create_e:
                print(f"Failed to create tables: {create_e}")
                return False
        
        if station_count > 0:
            print(f"Database already has {station_count} stations. Skipping seeding.")
            return True
        
        print("Stations table is empty. Seeding Bangalore EV charging stations...")
        
        # Get station data
        stations_data = get_bangalore_ev_stations()
        
        # Insert stations with individual error handling
        seeded_count = 0
        for station_data in stations_data:
            try:
                # Validate station data
                required_fields = ['name', 'latitude', 'longitude', 'charger_type', 'power_kw', 'price_inr']
                if not all(field in station_data for field in required_fields):
                    print(f"Missing required fields in station data: {station_data.get('name', 'Unknown')}")
                    continue
                
                station = models.ChargingStation(**station_data)
                db.add(station)
                seeded_count += 1
                print(f"Added station: {station_data['name']}")
            except Exception as e:
                print(f"Error adding station {station_data.get('name', 'Unknown')}: {e}")
                # Continue with other stations even if one fails
                continue
        
        # Commit all changes
        try:
            db.commit()
            print(f"Successfully seeded {seeded_count} EV charging stations in Bangalore.")
        except Exception as e:
            print(f"Failed to commit stations: {e}")
            db.rollback()
            return False
        
        # Verify the seeding
        try:
            final_count = db.query(models.ChargingStation).count()
            print(f"Total stations in database after seeding: {final_count}")
        except Exception as e:
            print(f"Failed to verify seeding: {e}")
        
        return True
        
    except Exception as e:
        print(f"Critical error during database seeding: {e}")
        if db:
            try:
                db.rollback()
            except Exception:
                pass
        return False
        
    finally:
        if should_close_db and db:
            try:
                db.close()
            except Exception:
                pass

def seed_stations_safely() -> bool:
    """
    Wrapper function that safely seeds stations with proper error handling.
    This is the main function that should be called during application startup.
    """
    try:
        print("Starting EV charging stations database seeding...")
        success = seed_stations()
        if success:
            print("Database seeding completed successfully.")
        else:
            print("Database seeding failed.")
        return success
    except Exception as e:
        print(f"Unexpected error during seeding process: {e}")
        return False

if __name__ == "__main__":
    # Allow running this module directly for testing/manual seeding
    print("Running EV charging stations seeding...")
    success = seed_stations_safely()
    if success:
        print("✅ Seeding completed successfully!")
    else:
        print("❌ Seeding failed. Check logs for details.")
