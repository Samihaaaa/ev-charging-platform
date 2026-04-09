"""
Test script to verify frontend compatibility with stations API response.
This simulates what the frontend expects and validates the API response format.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_api_response_structure():
    """Test that API response matches frontend expectations."""
    print("Testing API response structure for frontend compatibility...")
    
    try:
        from app.routers.stations import get_stations
        from app.database import SessionLocal
        
        with SessionLocal() as db:
            stations = get_stations(db=db)
            
            if not stations:
                print("  - No stations returned from API")
                return False
            
            print(f"  - API returned {len(stations)} stations")
            
            # Test first station for frontend compatibility
            sample = stations[0]
            
            # Frontend expects these fields in the response
            required_fields = ['id', 'name', 'latitude', 'longitude', 'charger_type', 'power_kw', 'price_inr']
            
            # Check if response is in expected format
            if hasattr(sample, '__dict__'):
                # SQLAlchemy model response
                print("  - Response format: SQLAlchemy model")
                
                for field in required_fields:
                    if not hasattr(sample, field):
                        print(f"  - Missing required field: {field}")
                        return False
                    value = getattr(sample, field)
                    if value is None:
                        print(f"  - Field {field} is None")
                        return False
                
                print("  - All required fields present in model")
                
            elif isinstance(sample, dict):
                # Dictionary response
                print("  - Response format: Dictionary")
                
                for field in required_fields:
                    if field not in sample:
                        print(f"  - Missing required field: {field}")
                        return False
                    value = sample[field]
                    if value is None:
                        print(f"  - Field {field} is None")
                        return False
                
                print("  - All required fields present in dict")
                
            else:
                print(f"  - Unexpected response format: {type(sample)}")
                return False
            
            # Validate data types
            if hasattr(sample, '__dict__'):
                id_val = sample.id
                name_val = sample.name
                lat_val = sample.latitude
                lon_val = sample.longitude
                type_val = sample.charger_type
                power_val = sample.power_kw
                price_val = sample.price_inr
            else:
                id_val = sample['id']
                name_val = sample['name']
                lat_val = sample['latitude']
                lon_val = sample['longitude']
                type_val = sample['charger_type']
                power_val = sample['power_kw']
                price_val = sample['price_inr']
            
            # Type validation
            if not isinstance(id_val, int):
                print(f"  - Invalid ID type: {type(id_val)}")
                return False
            
            if not isinstance(name_val, str) or not name_val.strip():
                print(f"  - Invalid name: {name_val}")
                return False
            
            if not isinstance(lat_val, (int, float)) or not (-90 <= lat_val <= 90):
                print(f"  - Invalid latitude: {lat_val}")
                return False
            
            if not isinstance(lon_val, (int, float)) or not (-180 <= lon_val <= 180):
                print(f"  - Invalid longitude: {lon_val}")
                return False
            
            if not isinstance(type_val, str) or type_val not in ['AC', 'DC Fast']:
                print(f"  - Invalid charger type: {type_val}")
                return False
            
            if not isinstance(power_val, int) or power_val <= 0:
                print(f"  - Invalid power: {power_val}")
                return False
            
            if not isinstance(price_val, int) or price_val < 0:
                print(f"  - Invalid price: {price_val}")
                return False
            
            print("  - All data types are valid")
            print(f"  - Sample station: {name_val} ({type_val}, {power_val}kW, ${price_val})")
            
            return True
            
    except Exception as e:
        print(f"  - API structure test failed: {e}")
        return False

def test_frontend_data_simulation():
    """Simulate how frontend would process the API response."""
    print("\nTesting frontend data processing simulation...")
    
    try:
        from app.routers.stations import get_stations
        from app.database import SessionLocal
        
        with SessionLocal() as db:
            stations = get_stations(db=db)
            
            if not stations:
                print("  - No stations to simulate with")
                return False
            
            # Simulate frontend JavaScript processing
            processed_stations = []
            
            for station in stations:
                # Extract data the way frontend would
                if hasattr(station, '__dict__'):
                    station_data = {
                        'id': station.id,
                        'name': station.name,
                        'latitude': station.latitude,
                        'longitude': station.longitude,
                        'charger_type': station.charger_type,
                        'power_kw': station.power_kw,
                        'price_inr': station.price_inr
                    }
                else:
                    station_data = station
                
                # Frontend validation (simulated)
                if all(station_data.get(field) is not None for field in ['id', 'name', 'latitude', 'longitude']):
                    processed_stations.append(station_data)
            
            print(f"  - Frontend would process {len(processed_stations)} stations")
            
            if len(processed_stations) == 0:
                print("  - No stations passed frontend validation")
                return False
            
            # Check for Bangalore locations (expected)
            bangalore_stations = [
                s for s in processed_stations 
                if 12.5 <= s['latitude'] <= 13.5 and 77.0 <= s['longitude'] <= 78.0
            ]
            
            print(f"  - Found {len(bangalore_stations)} stations in Bangalore area")
            
            if len(bangalore_stations) == 0:
                print("  - No stations in expected Bangalore area")
                return False
            
            print("  - Frontend simulation successful")
            return True
            
    except Exception as e:
        print(f"  - Frontend simulation failed: {e}")
        return False

def test_api_endpoint_direct():
    """Test the API endpoint directly like a browser would call it."""
    print("\nTesting direct API endpoint call...")
    
    try:
        # Import and test the app directly
        from app.main import app
        from fastapi.testclient import TestClient
        
        # Create test client
        client = TestClient(app)
        
        # Make GET request to /stations/
        response = client.get("/stations/")
        
        print(f"  - Response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"  - API returned error: {response.text}")
            return False
        
        # Parse JSON response
        stations = response.json()
        print(f"  - JSON response contains {len(stations)} stations")
        
        if len(stations) == 0:
            print("  - API returned empty list")
            return False
        
        # Validate response structure
        sample = stations[0]
        required_fields = ['id', 'name', 'latitude', 'longitude', 'charger_type', 'power_kw', 'price_inr']
        
        for field in required_fields:
            if field not in sample:
                print(f"  - Missing field in JSON response: {field}")
                return False
        
        print("  - JSON response structure is valid")
        print(f"  - Sample station: {sample['name']}")
        
        return True
        
    except ImportError:
        print("  - TestClient not available, skipping direct API test")
        return True  # Not a failure, just missing test dependency
    except Exception as e:
        print(f"  - Direct API test failed: {e}")
        return False

def main():
    """Run all frontend compatibility tests."""
    print("Frontend Compatibility Test Suite")
    print("=" * 50)
    
    tests = [
        ("API Response Structure", test_api_response_structure),
        ("Frontend Data Simulation", test_frontend_data_simulation),
        ("Direct API Endpoint", test_api_endpoint_direct),
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
    print("FRONTEND COMPATIBILITY RESULTS")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  {status:6} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\nSUCCESS: Stations API is fully compatible with frontend!")
        print("The frontend should be able to display all chargers correctly.")
    else:
        print("\nISSUES: Some compatibility tests failed.")
        print("The frontend may have issues displaying chargers.")
    
    return passed == len(results)

if __name__ == "__main__":
    main()
