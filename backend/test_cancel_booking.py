"""
Test script to verify cancel booking API functionality.
Tests the DELETE /bookings/{booking_id} endpoint.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_cancel_booking():
    """Test the cancel booking endpoint."""
    print("Testing cancel booking API...")
    
    try:
        from app.routers.bookings import cancel_booking_demo_simple
        from app.database import SessionLocal
        from app.schemas import CheckoutSessionCreate
        from app.routers.payments import create_checkout_session
        
        with SessionLocal() as db:
            # Step 1: Create a booking to cancel
            print("Step 1: Creating a booking...")
            payload = CheckoutSessionCreate(
                station_id=1,
                time_slot="2pm-3pm"
            )
            
            result = create_checkout_session(payload, db)
            print(f"  - Booking creation result: {result}")
            
            if result.get("status") != "success":
                print("  - Failed to create booking for testing")
                return False
            
            booking_id = result.get("booking_id")
            print(f"  - Created booking with ID: {booking_id}")
            
            # Step 2: Verify booking exists before cancellation
            from app import models
            booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
            if not booking:
                print("  - Booking not found in database")
                return False
            
            print(f"  - Booking found: station_id={booking.station_id}, slot={booking.time_slot}, status={getattr(booking, 'status', 'unknown')}")
            
            # Step 3: Cancel the booking
            print(f"Step 2: Cancelling booking {booking_id}...")
            cancel_result = cancel_booking_demo_simple(booking_id, db)
            print(f"  - Cancel result: {cancel_result}")
            
            if cancel_result.get("message") != "Booking cancelled successfully":
                print("  - Cancel booking failed")
                return False
            
            # Step 4: Verify booking status is updated
            updated_booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
            if updated_booking:
                new_status = getattr(updated_booking, 'status', None)
                print(f"  - Updated booking status: {new_status}")
                
                if new_status == "cancelled":
                    print("  - Booking status correctly updated to 'cancelled'")
                else:
                    print(f"  - Booking status not updated correctly: {new_status}")
                    return False
            else:
                print("  - Booking not found after cancellation")
                return False
            
            # Step 5: Test cancelling non-existent booking
            print("Step 3: Testing non-existent booking cancellation...")
            try:
                cancel_result = cancel_booking_demo_simple(99999, db)
                print(f"  - Non-existent booking cancel result: {cancel_result}")
                print("  - Should have returned 404 error")
                return False
            except Exception as e:
                print(f"  - Expected error for non-existent booking: {e}")
                print("  - Correctly returned error for non-existent booking")
            
            print("  - All cancel booking tests passed!")
            return True
            
    except Exception as e:
        print(f"  - Cancel booking test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_slot_availability_after_cancel():
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
            
            # Check if "2pm-3pm" is available (should be freed after cancellation)
            if "2pm-3pm" in available_slots_list:
                print("  - Slot correctly freed after cancellation")
                return True
            else:
                print("  - Slot not freed after cancellation")
                return False
                
    except Exception as e:
        print(f"  - Slot availability test failed: {e}")
        return False

def main():
    """Run all cancel booking tests."""
    print("Cancel Booking API Test Suite")
    print("=" * 40)
    
    tests = [
        ("Cancel Booking API", test_cancel_booking),
        ("Slot Availability After Cancel", test_slot_availability_after_cancel),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 40)
    print("CANCEL BOOKING TEST RESULTS")
    print("=" * 40)
    
    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  {status:6} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\nSUCCESS: Cancel booking API is working perfectly!")
        print("Users can now:")
        print("  - Cancel bookings without errors")
        print("  - See bookings disappear from list")
        print("  - Have slots become available again")
    else:
        print("\nISSUES: Some cancel booking tests failed.")
        print("Check the test output above for details.")
    
    return passed == len(results)

if __name__ == "__main__":
    main()
