"""
Complete test for the booking flow: creation -> display -> cancellation.
This tests the full user journey without authentication.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_booking_creation():
    """Test creating a booking through payment simulation."""
    print("Testing booking creation...")
    
    try:
        from app.routers.payments import create_checkout_session
        from app.database import SessionLocal
        from app.schemas import CheckoutSessionCreate
        
        with SessionLocal() as db:
            # Create a booking
            payload = CheckoutSessionCreate(
                station_id=1,
                time_slot="2pm-3pm"
            )
            
            result = create_checkout_session(payload, db)
            print(f"  - Booking creation result: {result}")
            
            if result.get("status") == "success":
                booking_id = result.get("booking_id")
                print(f"  - Booking created successfully with ID: {booking_id}")
                return True, booking_id
            else:
                print(f"  - Booking creation failed: {result.get('error')}")
                return False, None
                
    except Exception as e:
        print(f"  - Booking creation test failed: {e}")
        return False, None

def test_my_bookings_display():
    """Test that bookings appear in my-bookings endpoint."""
    print("\nTesting my-bookings display...")
    
    try:
        from app.routers.bookings import my_bookings_demo
        from app.database import SessionLocal
        
        with SessionLocal() as db:
            bookings = my_bookings_demo(db)
            print(f"  - Retrieved {len(bookings)} bookings")
            
            if len(bookings) > 0:
                print("  - Bookings found:")
                for booking in bookings:
                    print(f"    * ID: {booking.get('id')}, Station: {booking.get('station_name')}, Slot: {booking.get('time_slot')}, Status: {booking.get('status')}")
                
                # Check if booking has required fields
                sample = bookings[0]
                required_fields = ['id', 'station_name', 'time_slot', 'status']
                
                for field in required_fields:
                    if field not in sample:
                        print(f"  - Missing required field: {field}")
                        return False
                
                print("  - All bookings have required fields")
                return True, bookings
            else:
                print("  - No bookings found")
                return False, []
                
    except Exception as e:
        print(f"  - My bookings test failed: {e}")
        return False, []

def test_booking_cancellation():
    """Test cancelling a booking."""
    print("\nTesting booking cancellation...")
    
    try:
        from app.routers.bookings import cancel_booking_demo_simple
        from app.database import SessionLocal
        
        # First create a booking to cancel
        from app.routers.payments import create_checkout_session
        from app.schemas import CheckoutSessionCreate
        
        with SessionLocal() as db:
            # Create a booking
            payload = CheckoutSessionCreate(
                station_id=1,
                time_slot="3pm-4pm"
            )
            
            result = create_checkout_session(payload, db)
            booking_id = result.get("booking_id")
            
            if not booking_id:
                print("  - Could not create booking for cancellation test")
                return False
            
            print(f"  - Created booking {booking_id} for cancellation")
            
            # Cancel the booking
            cancel_result = cancel_booking_demo_simple(booking_id, db)
            print(f"  - Cancellation result: {cancel_result}")
            
            if cancel_result.get("status") == "success":
                print("  - Booking cancelled successfully")
                return True, booking_id
            else:
                print("  - Booking cancellation failed")
                return False, None
                
    except Exception as e:
        print(f"  - Booking cancellation test failed: {e}")
        return False, None

def test_slot_availability_after_cancellation():
    """Test that slots become available after cancellation."""
    print("\nTesting slot availability after cancellation...")
    
    try:
        from app.routers.stations import available_slots
        from app.database import SessionLocal
        
        with SessionLocal() as db:
            # Get available slots for station 1
            result = available_slots(1, db)
            available_slots_list = result.get("available_slots", [])
            
            print(f"  - Available slots: {available_slots_list}")
            
            # Check if "3pm-4pm" is available (should be freed after cancellation)
            if "3pm-4pm" in available_slots_list:
                print("  - Slot correctly freed after cancellation")
                return True
            else:
                print("  - Slot not freed after cancellation")
                return False
                
    except Exception as e:
        print(f"  - Slot availability test failed: {e}")
        return False

def test_booking_not_in_my_bookings_after_cancellation():
    """Test that cancelled bookings don't appear in my-bookings."""
    print("\nTesting cancelled bookings removal from my-bookings...")
    
    try:
        from app.routers.bookings import my_bookings_demo
        from app.database import SessionLocal
        
        with SessionLocal() as db:
            bookings = my_bookings_demo(db)
            print(f"  - Current bookings count: {len(bookings)}")
            
            # Check if any booking has "cancelled" status (should not appear)
            cancelled_bookings = [b for b in bookings if b.get('status') == 'cancelled']
            
            if len(cancelled_bookings) == 0:
                print("  - No cancelled bookings in my-bookings (correct)")
                return True
            else:
                print(f"  - Found {len(cancelled_bookings)} cancelled bookings in my-bookings (incorrect)")
                return False
                
    except Exception as e:
        print(f"  - Cancelled bookings test failed: {e}")
        return False

def test_complete_flow():
    """Test the complete flow: create -> display -> cancel -> verify."""
    print("\nTesting complete booking flow...")
    
    try:
        # Step 1: Create booking
        print("  Step 1: Creating booking...")
        from app.routers.payments import create_checkout_session
        from app.routers.bookings import my_bookings_demo, cancel_booking_demo_simple
        from app.database import SessionLocal
        from app.schemas import CheckoutSessionCreate
        
        with SessionLocal() as db:
            # Create booking
            payload = CheckoutSessionCreate(
                station_id=1,
                time_slot="4pm-5pm"
            )
            
            result = create_checkout_session(payload, db)
            booking_id = result.get("booking_id")
            
            if not booking_id:
                print("  - Failed to create booking")
                return False
            
            print(f"  - Created booking {booking_id}")
            
            # Step 2: Verify booking appears in my-bookings
            print("  Step 2: Verifying booking appears in my-bookings...")
            bookings = my_bookings_demo(db)
            booking_found = any(b.get('id') == booking_id for b in bookings)
            
            if not booking_found:
                print("  - Booking not found in my-bookings")
                return False
            
            print("  - Booking found in my-bookings")
            
            # Step 3: Cancel booking
            print("  Step 3: Cancelling booking...")
            cancel_result = cancel_booking_demo_simple(booking_id, db)
            
            if cancel_result.get('status') != 'success':
                print("  - Failed to cancel booking")
                return False
            
            print("  - Booking cancelled")
            
            # Step 4: Verify booking removed from my-bookings
            print("  Step 4: Verifying booking removed from my-bookings...")
            bookings_after_cancel = my_bookings_demo(db)
            booking_still_present = any(b.get('id') == booking_id for b in bookings_after_cancel)
            
            if booking_still_present:
                print("  - Booking still appears in my-bookings after cancellation")
                return False
            
            print("  - Booking removed from my-bookings")
            
            print("  - Complete flow successful!")
            return True
            
    except Exception as e:
        print(f"  - Complete flow test failed: {e}")
        return False

def main():
    """Run all booking flow tests."""
    print("Complete Booking Flow Test Suite")
    print("=" * 60)
    
    tests = [
        ("Booking Creation", test_booking_creation),
        ("My Bookings Display", test_my_bookings_display),
        ("Booking Cancellation", test_booking_cancellation),
        (" Slot Availability After Cancellation", test_slot_availability_after_cancellation),
        ("Cancelled Bookings Removal", test_booking_not_in_my_bookings_after_cancellation),
        ("Complete Flow", test_complete_flow),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            if test_name == "Booking Creation":
                result, booking_id = test_func()
                results.append((test_name, result))
            elif test_name == "My Bookings Display":
                result, bookings = test_func()
                results.append((test_name, result))
            elif test_name == "Booking Cancellation":
                result, booking_id = test_func()
                results.append((test_name, result))
            else:
                result = test_func()
                results.append((test_name, result))
        except Exception as e:
            print(f"Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("COMPLETE BOOKING FLOW TEST RESULTS")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  {status:6} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\nSUCCESS: Complete booking flow is working perfectly!")
        print("Users can now:")
        print("  - Create bookings and see them instantly")
        print("  - View their bookings with station names")
        print("  - Cancel bookings with working buttons")
        print("  - See slots become available after cancellation")
        print("  - Experience a complete, realistic booking system")
    else:
        print("\nISSUES: Some booking flow tests failed.")
        print("Check the test output above for details.")
    
    return passed == len(results)

if __name__ == "__main__":
    main()
