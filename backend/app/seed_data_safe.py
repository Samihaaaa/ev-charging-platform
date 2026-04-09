"""
Safe database seeding module for EV charging stations.
This version is designed to never crash the application startup.
"""

from typing import List, Dict, Any, Optional

def get_bangalore_ev_stations() -> List[Dict[str, Any]]:
    """
    Returns a list of realistic Bangalore EV charging stations.
    All data is validated and safe for database insertion.
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
        }
    ]

def validate_station_data(station_data: Dict[str, Any]) -> bool:
    """
    Validate station data before database insertion.
    Returns True if data is valid, False otherwise.
    """
    required_fields = ['name', 'latitude', 'longitude', 'charger_type', 'power_kw', 'price_inr']
    
    # Check all required fields exist
    for field in required_fields:
        if field not in station_data:
            return False
    
    # Validate data types and ranges
    try:
        name = str(station_data['name'])
        if not name or len(name) > 100:
            return False
        
        latitude = float(station_data['latitude'])
        if not (-90 <= latitude <= 90):
            return False
        
        longitude = float(station_data['longitude'])
        if not (-180 <= longitude <= 180):
            return False
        
        charger_type = str(station_data['charger_type'])
        if charger_type not in ['AC', 'DC Fast']:
            return False
        
        power_kw = int(station_data['power_kw'])
        if not (1 <= power_kw <= 500):
            return False
        
        price_inr = int(station_data['price_inr'])
        if not (0 <= price_inr <= 5000):
            return False
        
        return True
        
    except (ValueError, TypeError):
        return False

def seed_stations_safely() -> bool:
    """
    Ultra-safe seeding function that will never crash the application.
    Returns True if seeding was successful or not needed, False if there was an error.
    """
    try:
        print("Starting safe EV charging stations seeding...")
        
        # Import database components with error handling
        try:
            from .database import SessionLocal
            from . import models
        except ImportError as e:
            print(f"Database import failed: {e}")
            return False
        
        # Check if ChargingStation model exists
        if not hasattr(models, 'ChargingStation'):
            print("ChargingStation model not found")
            return False
        
        # Create database session
        db = None
        try:
            db = SessionLocal()
        except Exception as e:
            print(f"Failed to create database session: {e}")
            return False
        
        try:
            # Check if stations table exists and is empty
            try:
                station_count = db.query(models.ChargingStation).count()
                if station_count > 0:
                    print(f"Database already has {station_count} stations. Skipping seeding.")
                    return True
            except Exception as e:
                print(f"Failed to query stations table: {e}")
                # Try to create table first
                try:
                    from .database import Base, engine
                    Base.metadata.create_all(bind=engine)
                    station_count = db.query(models.ChargingStation).count()
                    if station_count > 0:
                        print(f"Database already has {station_count} stations. Skipping seeding.")
                        return True
                except Exception as create_e:
                    print(f"Failed to create tables: {create_e}")
                    return False
            
            print("Stations table is empty. Seeding Bangalore EV charging stations...")
            
            # Get and validate station data
            stations_data = get_bangalore_ev_stations()
            valid_stations = []
            
            for station_data in stations_data:
                if validate_station_data(station_data):
                    valid_stations.append(station_data)
                else:
                    print(f"Invalid station data: {station_data.get('name', 'Unknown')}")
            
            if not valid_stations:
                print("No valid station data to seed")
                return False
            
            # Insert stations one by one for maximum safety
            seeded_count = 0
            for station_data in valid_stations:
                try:
                    station = models.ChargingStation(**station_data)
                    db.add(station)
                    db.flush()  # Validate without committing
                    seeded_count += 1
                    print(f"Added station: {station_data['name']}")
                except Exception as e:
                    print(f"Error adding station {station_data.get('name', 'Unknown')}: {e}")
                    db.rollback()
                    continue
            
            # Commit all changes
            try:
                db.commit()
                print(f"Successfully seeded {seeded_count} EV charging stations.")
                return True
            except Exception as e:
                print(f"Failed to commit stations: {e}")
                db.rollback()
                return False
                
        finally:
            if db:
                try:
                    db.close()
                except Exception:
                    pass
        
    except Exception as e:
        print(f"Unexpected error during seeding: {e}")
        return False

if __name__ == "__main__":
    # Allow running this module directly for testing
    print("Running safe EV charging stations seeding...")
    success = seed_stations_safely()
    if success:
        print("Seeding completed successfully!")
    else:
        print("Seeding failed.")
