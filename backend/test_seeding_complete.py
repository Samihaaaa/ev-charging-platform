"""
Complete test script to verify safe seeding functionality.
This tests the entire pipeline from seeding to API response.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_safe_seeding():
    """Test the safe seeding implementation."""
    print("Testing safe seeding implementation...")
    
    try:
        from app.seed_data_safe import seed_stations_safely, get_bangalore_ev_stations
        
        # Test station data generation
        print("  - Testing station data generation...")
        stations = get_bangalore_ev_stations()
        print(f"    Generated {len(stations)} stations")
        
        # Test actual seeding
        print("  - Testing seeding process...")
        success = seed_stations_safely()
        print(f"    Seeding result: {'SUCCESS' if success else 'FAILED'}")
        
        return success
        
    except Exception as e:
        print(f"  - Seeding test failed: {e}")
        return False

def test_database_content():
    """Test that stations are actually in the database."""
    print("\nTesting database content...")
    
    try:
        from app.database import SessionLocal
        from app import models
        
        with SessionLocal() as db:
            # Count stations
            count = db.query(models.ChargingStation).count()
            print(f"  - Found {count} stations in database")
            
            if count == 0:
                print("  - No stations found in database")
                return False
            
            # Get sample stations
            stations = db.query(models.ChargingStation).limit(3).all()
            print("  - Sample stations:")
            for station in stations:
                print(f"    * {station.name} ({station.charger_type}, {station.power_kw}kW, ${station.price_inr})")
            
            return True
            
    except Exception as e:
        print(f"  - Database test failed: {e}")
        return False

def test_api_endpoint():
    """Test the GET /stations/ API endpoint."""
    print("\nTesting API endpoint...")
    
    try:
        from app.routers.stations import get_stations
        from app.database import SessionLocal
        
        with SessionLocal() as db:
            stations = get_stations(db=db)
            print(f"  - API returned {len(stations)} stations")
            
            if len(stations) == 0:
                print("  - API returned no stations")
                return False
            
            # Check station structure
            sample = stations[0]
            required_fields = ['id', 'name', 'latitude', 'longitude', 'charger_type', 'power_kw', 'price_inr']
            
            for field in required_fields:
                if not hasattr(sample, field) and field not in sample:
                    print(f"  - Missing field in API response: {field}")
                    return False
            
            print("  - API response structure is valid")
            print(f"  - Sample station: {sample.name}")
            
            return True
            
    except Exception as e:
        print(f"  - API test failed: {e}")
        return False

def test_app_startup():
    """Test that the app can start without crashing."""
    print("\nTesting app startup...")
    
    try:
        from app.main import app
        print("  - App imported successfully")
        print(f"  - App title: {app.title}")
        print(f"  - Number of routes: {len(app.routes)}")
        return True
    except Exception as e:
        print(f"  - App startup test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Complete Seeding Test Suite")
    print("=" * 50)
    
    tests = [
        ("Safe Seeding", test_safe_seeding),
        ("Database Content", test_database_content),
        ("API Endpoint", test_api_endpoint),
        ("App Startup", test_app_startup),
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
        print("\nSUCCESS: All tests passed!")
        print("The safe seeding system is working correctly.")
        print("Your backend should start without issues and serve station data.")
    else:
        print("\nISSUES: Some tests failed.")
        print("Check the test output above for details.")
    
    return passed == len(results)

if __name__ == "__main__":
    main()
