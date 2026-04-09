"""
Test script to verify EV charging stations seeding functionality.
This can be run to test the seeding system independently.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine, Base
from app import models
from app.seed_data import seed_stations_safely, get_bangalore_ev_stations

def test_seeding():
    """Test the seeding functionality end-to-end."""
    print("🧪 Testing EV charging stations seeding...")
    
    # Create tables
    print("📋 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    # Clear existing data for testing
    print("🗑️  Clearing existing stations for test...")
    with SessionLocal() as db:
        db.query(models.ChargingStation).delete()
        db.commit()
    
    # Test seeding
    print("🌱 Running seeding...")
    success = seed_stations_safely()
    
    if not success:
        print("❌ Seeding failed!")
        return False
    
    # Verify results
    print("🔍 Verifying seeded data...")
    with SessionLocal() as db:
        stations = db.query(models.ChargingStation).all()
        print(f"✅ Found {len(stations)} stations in database")
        
        # Check specific stations
        expected_stations = get_bangalore_ev_stations()
        station_names = [station.name for station in stations]
        
        for expected in expected_stations[:3]:  # Check first 3 stations
            if expected["name"] in station_names:
                print(f"✅ Found station: {expected['name']}")
            else:
                print(f"❌ Missing station: {expected['name']}")
                return False
        
        # Print sample station data
        if stations:
            sample = stations[0]
            print(f"\n📊 Sample station data:")
            print(f"   Name: {sample.name}")
            print(f"   Location: ({sample.latitude}, {sample.longitude})")
            print(f"   Type: {sample.charger_type}")
            print(f"   Power: {sample.power_kw}kW")
            print(f"   Price: ₹{sample.price_inr}")
    
    print("\n🎉 All tests passed! Seeding system is working correctly.")
    return True

if __name__ == "__main__":
    test_seeding()
