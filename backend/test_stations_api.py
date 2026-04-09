"""
Test script to verify the stations API is working correctly.
This will test the GET /stations/ endpoint and ensure it returns proper data.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_database_has_stations():
    """Test that the database actually has stations."""
    print("Testing database content...")
    
    try:
        from app.database import SessionLocal
        from app import models
        
        with SessionLocal() as db:
            count = db.query(models.ChargingStation).count()
            print(f"  - Found {count} stations in database")
            
            if count == 0:
                print("  - No stations found. Running safe seeding...")
                from app.seed_data_safe import seed_stations_safely
                success = seed_stations_safely()
                if success:
                    # Check again after seeding
                    count = db.query(models.ChargingStation).count()
                    print(f"  - After seeding: {count} stations")
                else:
                    print("  - Seeding failed")
                    return False
            
            # Get sample stations for verification
            stations = db.query(models.ChargingStation).limit(3).all()
            print("  - Sample stations in database:")
            for station in stations:
                print(f"    * {station.name} at ({station.latitude}, {station.longitude})")
            
            return True
            
    except Exception as e:
        print(f"  - Database test failed: {e}")
        return False

def test_stations_router_function():
    """Test the stations router function directly."""
    print("\nTesting stations router function...")
    
    try:
        from app.routers.stations import get_stations
        from app.database import SessionLocal
        
        with SessionLocal() as db:
            stations = get_stations(db=db)
            print(f"  - Router returned {len(stations)} stations")
            
            if len(stations) == 0:
                print("  - Router returned no stations")
                return False
            
            # Check the structure of returned data
            sample = stations[0]
            print(f"  - Sample station type: {type(sample)}")
            
            # Check if it's a SQLAlchemy model or dict
            if hasattr(sample, '__dict__'):
                print("  - Returned SQLAlchemy model")
                fields = [attr for attr in dir(sample) if not attr.startswith('_')]
                print(f"  - Model fields: {fields}")
            elif isinstance(sample, dict):
                print("  - Returned dictionary")
                print(f"  - Dict keys: {list(sample.keys())}")
            else:
                print(f"  - Unknown return type: {type(sample)}")
            
            return True
            
    except Exception as e:
        print(f"  - Router function test failed: {e}")
        return False

def test_api_response_format():
    """Test API response format for frontend compatibility."""
    print("\nTesting API response format...")
    
    try:
        from app.routers.stations import get_stations
        from app.database import SessionLocal
        
        with SessionLocal() as db:
            stations = get_stations(db=db)
            
            if not stations:
                print("  - No stations to test format")
                return False
            
            # Test first station for required fields
            sample = stations[0]
            
            # Check for required fields based on frontend expectations
            required_fields = ['id', 'name', 'latitude', 'longitude', 'charger_type', 'power_kw', 'price_inr']
            
            if hasattr(sample, '__dict__'):
                # SQLAlchemy model
                for field in required_fields:
                    if not hasattr(sample, field):
                        print(f"  - Missing field in model: {field}")
                        return False
            elif isinstance(sample, dict):
                # Dictionary
                for field in required_fields:
                    if field not in sample:
                        print(f"  - Missing field in dict: {field}")
                        return False
            else:
                print(f"  - Unknown response format: {type(sample)}")
                return False
            
            print("  - All required fields present")
            print(f"  - Sample station: {sample.name if hasattr(sample, 'name') else sample.get('name')}")
            
            return True
            
    except Exception as e:
        print(f"  - API format test failed: {e}")
        return False

def test_fastapi_integration():
    """Test FastAPI integration and route registration."""
    print("\nTesting FastAPI integration...")
    
    try:
        from app.main import app
        
        # Check if stations router is included
        stations_routes = [route for route in app.routes if hasattr(route, 'path') and '/stations' in route.path]
        print(f"  - Found {len(stations_routes)} stations-related routes")
        
        # Get the GET /stations/ route
        get_stations_route = None
        for route in app.routes:
            if hasattr(route, 'path') and route.path == '/stations/' and hasattr(route, 'methods'):
                if 'GET' in route.methods:
                    get_stations_route = route
                    break
        
        if get_stations_route:
            print("  - GET /stations/ route found and registered")
            return True
        else:
            print("  - GET /stations/ route not found")
            return False
            
    except Exception as e:
        print(f"  - FastAPI integration test failed: {e}")
        return False

def test_complete_api_call():
    """Test complete API call simulation."""
    print("\nTesting complete API call simulation...")
    
    try:
        # Simulate what happens when GET /stations/ is called
        from app.routers.stations import get_stations, get_db
        from app.database import SessionLocal
        
        # Get database session the same way the endpoint does
        db_gen = get_db()
        db = next(db_gen)
        
        try:
            # Call the endpoint function
            stations = get_stations(db=db)
            print(f"  - API call returned {len(stations)} stations")
            
            # Verify the response is what frontend expects
            if len(stations) > 0:
                sample = stations[0]
                if hasattr(sample, 'name'):
                    print(f"  - Sample station: {sample.name}")
                elif isinstance(sample, dict):
                    print(f"  - Sample station: {sample.get('name')}")
                
                return True
            else:
                print("  - API call returned no stations")
                return False
                
        finally:
            # Clean up database session
            try:
                db.close()
            except:
                pass
                
    except Exception as e:
        print(f"  - Complete API call test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Stations API Verification Test Suite")
    print("=" * 50)
    
    tests = [
        ("Database Content", test_database_has_stations),
        ("Router Function", test_stations_router_function),
        ("API Response Format", test_api_response_format),
        ("FastAPI Integration", test_fastapi_integration),
        ("Complete API Call", test_complete_api_call),
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
    print("TEST RESULTS")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  {status:6} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\nSUCCESS: Stations API is working correctly!")
        print("GET /stations/ should return station data for the frontend.")
    else:
        print("\nISSUES: Some tests failed.")
        print("The stations API may need fixes.")
    
    return passed == len(results)

if __name__ == "__main__":
    main()
