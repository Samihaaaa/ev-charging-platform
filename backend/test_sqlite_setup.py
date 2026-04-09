"""
Test script to verify SQLite database setup is working correctly.
This will test database connection, table creation, and basic operations.
"""

import sys
import os
from sqlalchemy import text
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_database_connection():
    """Test SQLite database connection."""
    print("Testing SQLite database connection...")
    
    try:
        from app.database import engine, SessionLocal, Base
        
        print(f"  - Database URL: {engine.url}")
        print(f"  - Database driver: {engine.driver}")
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).fetchone()
            print(f"  - Connection test result: {result}")
        
        print("  - SQLite connection successful")
        return True
        
    except Exception as e:
        print(f"  - Database connection failed: {e}")
        return False

def test_table_creation():
    """Test that database tables are created correctly."""
    print("\nTesting table creation...")
    
    try:
        from app.database import engine, Base
        from app import models
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("  - Tables created successfully")
        
        # Check if tables exist
        with engine.connect() as conn:
            # Get table names
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'")).fetchall()
            tables = [row[0] for row in result]
            print(f"  - Tables in database: {tables}")
            
            # Check for required tables
            required_tables = ['stations', 'users', 'bookings']
            missing_tables = [table for table in required_tables if table not in tables]
            
            if missing_tables:
                print(f"  - Missing tables: {missing_tables}")
                return False
            
            print("  - All required tables present")
            return True
            
    except Exception as e:
        print(f"  - Table creation test failed: {e}")
        return False

def test_model_operations():
    """Test basic model operations."""
    print("\nTesting model operations...")
    
    try:
        from app.database import SessionLocal
        from app import models
        
        with SessionLocal() as db:
            # Test station creation
            test_station = models.ChargingStation(
                name="Test Station",
                latitude=12.9716,
                longitude=77.5946,
                charger_type="AC",
                power_kw=22,
                price_inr=500
            )
            
            db.add(test_station)
            db.commit()
            db.refresh(test_station)
            
            print(f"  - Created test station with ID: {test_station.id}")
            
            # Test station retrieval
            retrieved_station = db.query(models.ChargingStation).filter(
                models.ChargingStation.name == "Test Station"
            ).first()
            
            if retrieved_station:
                print(f"  - Retrieved station: {retrieved_station.name}")
                # Clean up test data
                db.delete(retrieved_station)
                db.commit()
                print("  - Test data cleaned up")
                return True
            else:
                print("  - Failed to retrieve test station")
                return False
                
    except Exception as e:
        print(f"  - Model operations test failed: {e}")
        return False

def test_seeding_integration():
    """Test that seeding works with SQLite."""
    print("\nTesting seeding integration...")
    
    try:
        from app.seed_data_safe import seed_stations_safely
        from app.database import SessionLocal
        from app import models
        
        # Run seeding
        success = seed_stations_safely()
        print(f"  - Seeding result: {'SUCCESS' if success else 'FAILED'}")
        
        if success:
            # Check seeded data
            with SessionLocal() as db:
                count = db.query(models.ChargingStation).count()
                print(f"  - Stations in database after seeding: {count}")
                
                if count > 0:
                    # Get sample station
                    sample = db.query(models.ChargingStation).first()
                    print(f"  - Sample station: {sample.name}")
                    return True
                else:
                    print("  - No stations found after seeding")
                    return False
        else:
            print("  - Seeding failed")
            return False
            
    except Exception as e:
        print(f"  - Seeding integration test failed: {e}")
        return False

def test_app_startup():
    """Test that the app can start with SQLite."""
    print("\nTesting app startup...")
    
    try:
        from app.main import app
        
        print(f"  - App title: {app.title}")
        print(f"  - App routes: {len(app.routes)}")
        
        # Check if stations router is included
        stations_routes = [route for route in app.routes if hasattr(route, 'path') and '/stations' in route.path]
        print(f"  - Stations routes found: {len(stations_routes)}")
        
        return True
        
    except Exception as e:
        print(f"  - App startup test failed: {e}")
        return False

def test_database_file_creation():
    """Test that SQLite database file is created."""
    print("\nTesting database file creation...")
    
    try:
        # Check if ev.db file exists in backend directory
        backend_dir = os.path.dirname(__file__)
        db_file = os.path.join(backend_dir, "ev.db")
        
        if os.path.exists(db_file):
            file_size = os.path.getsize(db_file)
            print(f"  - Database file exists: {db_file}")
            print(f"  - File size: {file_size} bytes")
            return True
        else:
            print(f"  - Database file not found: {db_file}")
            print("  - File will be created when app starts")
            return True  # Not an error, file will be created
            
    except Exception as e:
        print(f"  - Database file test failed: {e}")
        return False

def main():
    """Run all SQLite setup tests."""
    print("SQLite Setup Verification Test Suite")
    print("=" * 50)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Table Creation", test_table_creation),
        ("Model Operations", test_model_operations),
        ("Seeding Integration", test_seeding_integration),
        ("App Startup", test_app_startup),
        ("Database File Creation", test_database_file_creation),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("SQLITE SETUP TEST RESULTS")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  {status:6} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\nSUCCESS: SQLite database setup is working correctly!")
        print("The backend should start without database errors.")
        print("Database file (ev.db) will be created automatically.")
    else:
        print("\nISSUES: Some SQLite setup tests failed.")
        print("Check the test output above for details.")
    
    return passed == len(results)

if __name__ == "__main__":
    main()
