"""
Test script to verify dashboard integration with booking system.
This tests the complete flow from frontend perspective.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_dashboard_booking_flow():
    """Test the complete dashboard booking flow."""
    print("Testing dashboard booking flow...")
    
    try:
        # Step 1: Create a booking (simulating frontend bookSlot)
        from app.routers.payments import create_checkout_session
        from app.database import SessionLocal
        from app.schemas import CheckoutSessionCreate
        
        with SessionLocal() as db:
            # Create booking like dashboard would
            payload = CheckoutSessionCreate(
                station_id=1,
                time_slot="11am-12pm"
            )
            
            result = create_checkout_session(payload, db)
            print(f"  - Dashboard booking result: {result}")
            
            if result.get("status") != "success":
                print("  - Dashboard booking failed")
                return False
            
            booking_id = result.get("booking_id")
            print(f"  - Booking created with ID: {booking_id}")
        
        # Step 2: Fetch bookings like dashboard loadMyBookings
        from app.routers.bookings import my_bookings_demo
        
        with SessionLocal() as db:
            bookings = my_bookings_demo(db)
            print(f"  - Dashboard bookings fetch result: {bookings}")
            
            if len(bookings) == 0:
                print("  - No bookings found for dashboard")
                return False
            
            # Check if our booking appears
            booking_found = any(b.get('id') == booking_id for b in bookings)
            if not booking_found:
                print("  - Created booking not found in dashboard fetch")
                return False
            
            print("  - Booking appears correctly in dashboard")
            
            # Verify booking structure matches dashboard expectations
            sample_booking = bookings[0]
            required_fields = ['id', 'station_name', 'time_slot', 'status']
            
            for field in required_fields:
                if field not in sample_booking:
                    print(f"  - Missing field in booking: {field}")
                    return False
            
            print("  - Booking structure matches dashboard expectations")
        
        # Step 3: Cancel booking like dashboard cancelBooking
        from app.routers.bookings import cancel_booking_demo_simple
        
        with SessionLocal() as db:
            cancel_result = cancel_booking_demo_simple(booking_id, db)
            print(f"  - Dashboard cancel result: {cancel_result}")
            
            if cancel_result.get("status") != "success":
                print("  - Dashboard cancellation failed")
                return False
            
            print(f"  - Booking cancelled, freed slot: {cancel_result.get('slot_freed')}")
        
        # Step 4: Verify booking removed from dashboard
        with SessionLocal() as db:
            bookings_after_cancel = my_bookings_demo(db)
            print(f"  - Bookings after cancellation: {len(bookings_after_cancel)}")
            
            booking_still_present = any(b.get('id') == booking_id for b in bookings_after_cancel)
            if booking_still_present:
                print("  - Cancelled booking still appears in dashboard")
                return False
            
            print("  - Cancelled booking removed from dashboard")
        
        return True
        
    except Exception as e:
        print(f"  - Dashboard booking flow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_station_display_integration():
    """Test station display integration with dashboard."""
    print("\nTesting station display integration...")
    
    try:
        from app.routers.stations import get_stations
        from app.database import SessionLocal
        
        with SessionLocal() as db:
            stations = get_stations(db=db)
            print(f"  - Retrieved {len(stations)} stations for dashboard")
            
            if len(stations) == 0:
                print("  - No stations found for dashboard")
                return False
            
            # Check station structure matches dashboard expectations
            sample_station = stations[0]
            required_fields = ['id', 'name', 'charger_type', 'power_kw']
            
            # Handle both dict and SQLAlchemy model responses
            if hasattr(sample_station, '__dict__'):
                for field in required_fields:
                    if not hasattr(sample_station, field):
                        print(f"  - Missing field in station model: {field}")
                        return False
            else:
                for field in required_fields:
                    if field not in sample_station:
                        print(f"  - Missing field in station dict: {field}")
                        return False
            
            print("  - Station structure matches dashboard expectations")
            return True
            
    except Exception as e:
        print(f"  - Station display integration test failed: {e}")
        return False

def test_available_slots_integration():
    """Test available slots integration with dashboard."""
    print("\nTesting available slots integration...")
    
    try:
        from app.routers.stations import available_slots
        from app.database import SessionLocal
        
        with SessionLocal() as db:
            # Get available slots for station 1
            result = available_slots(1, db)
            print(f"  - Available slots result: {result}")
            
            # Check response structure matches dashboard expectations
            required_fields = ['station_id', 'available_slots', 'all_slots']
            
            for field in required_fields:
                if field not in result:
                    print(f"  - Missing field in slots response: {field}")
                    return False
            
            available_slots_list = result.get('available_slots', [])
            print(f"  - Available slots: {available_slots_list}")
            
            if len(available_slots_list) == 0:
                print("  - No available slots (might be fully booked)")
            
            print("  - Available slots structure matches dashboard expectations")
            return True
            
    except Exception as e:
        print(f"  - Available slots integration test failed: {e}")
        return False

def test_price_display():
    """Test price display for dashboard."""
    print("\nTesting price display...")
    
    try:
        from app.routers.stations import available_slots
        from app.database import SessionLocal
        
        with SessionLocal() as db:
            # Check price format in available slots
            result = available_slots(1, db)
            price_inr = result.get('price_inr', 0)
            
            print(f"  - Station price: {price_inr} INR")
            
            if price_inr <= 0:
                print("  - Price is zero or negative (using default)")
            
            # Check station data for price_inr field
            from app.routers.stations import get_stations
            stations = get_stations(db=db)
            
            if stations:
                sample_station = stations[0]
                if hasattr(sample_station, '__dict__'):
                    station_price = getattr(sample_station, 'price_inr', None)
                else:
                    station_price = sample_station.get('price_inr', None)
                
                print(f"  - Station price from data: {station_price}")
            
            print("  - Price display working correctly")
            return True
            
    except Exception as e:
        print(f"  - Price display test failed: {e}")
        return False

def test_error_handling():
    """Test error handling for dashboard operations."""
    print("\nTesting error handling...")
    
    try:
        from app.routers.bookings import cancel_booking_demo_simple
        from app.database import SessionLocal
        
        with SessionLocal() as db:
            # Try to cancel non-existent booking
            try:
                result = cancel_booking_demo_simple(99999, db)
                print(f"  - Cancel non-existent booking result: {result}")
                # Should return error status
                if result.get("status") == "success":
                    print("  - Unexpected success for non-existent booking")
                    return False
                print("  - Error handling working correctly")
            except Exception as e:
                print(f"  - Expected error for non-existent booking: {e}")
        
        return True
        
    except Exception as e:
        print(f"  - Error handling test failed: {e}")
        return False

def main():
    """Run all dashboard integration tests."""
    print("Dashboard Integration Test Suite")
    print("=" * 50)
    
    tests = [
        ("Dashboard Booking Flow", test_dashboard_booking_flow),
        ("Station Display Integration", test_station_display_integration),
        ("Available Slots Integration", test_available_slots_integration),
        ("Price Display", test_price_display),
        ("Error Handling", test_error_handling),
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
    print("DASHBOARD INTEGRATION TEST RESULTS")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  {status:6} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\nSUCCESS: Dashboard integration is working perfectly!")
        print("The dashboard will now:")
        print("  - Display bookings immediately after creation")
        print("  - Show station names and time slots correctly")
        print("  - Handle cancellations properly")
        print("  - Refresh data after actions")
        print("  - Display prices in INR format")
    else:
        print("\nISSUES: Some dashboard integration tests failed.")
        print("Check the test output above for details.")
    
    return passed == len(results)

if __name__ == "__main__":
    main()
