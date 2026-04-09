"""
Test script to verify cancel booking works with correct booking_id.
Tests the exact flow from frontend to backend.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_cancel_booking_with_correct_id():
    """Test cancel booking with correct booking_id."""
    print("Testing cancel booking with correct booking_id...")
    
    try:
        from app.routers.bookings import cancel_booking
        from app.database import SessionLocal
        from app.schemas import CheckoutSessionCreate
        from app.routers.payments import create_checkout_session
        from app import models
        
        with SessionLocal() as db:
            # Step 1: Create a booking
            print("Step 1: Creating a booking...")
            payload = CheckoutSessionCreate(
                station_id=1,
                time_slot="3pm-4pm"
            )
            
            result = create_checkout_session(payload, db)
            print(f"  - Booking creation result: {result}")
            
            if result.get("status") != "success":
                print("  - Failed to create booking for testing")
                return False
            
            booking_id = result.get("booking_id")
            print(f"  - Created booking with ID: {booking_id}")
            
            # Step 2: Verify booking exists
            booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
            if not booking:
                print("  - Booking not found in database")
                return False
            
            print(f"  - Booking found: station_id={booking.station_id}, slot={booking.time_slot}, status={getattr(booking, 'status', 'unknown')}")
            
            # Step 3: Cancel booking using correct ID
            print(f"Step 2: Cancelling booking with correct ID: {booking_id}")
            cancel_result = cancel_booking(booking_id, db)
            print(f"  - Cancel result: {cancel_result}")
            
            if cancel_result.get("message") != "Booking cancelled successfully":
                print("  - Cancel booking failed")
                return False
            
            # Step 4: Verify booking status updated
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
            
            print("  - Cancel booking with correct ID works!")
            return True
            
    except Exception as e:
        print(f"  - Cancel booking test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cancel_booking_with_wrong_id():
    """Test cancel booking with wrong booking_id."""
    print("\nTesting cancel booking with wrong booking_id...")
    
    try:
        from app.routers.bookings import cancel_booking
        from app.database import SessionLocal
        
        with SessionLocal() as db:
            # Try to cancel non-existent booking
            print("Step 1: Attempting to cancel non-existent booking ID: 99999")
            
            try:
                result = cancel_booking(99999, db)
                print(f"  - Unexpected success: {result}")
                return False
            except Exception as e:
                print(f"  - Expected error for non-existent booking: {e}")
                if "Booking not found" in str(e):
                    print("  - Correct error message returned")
                    return True
                else:
                    print("  - Wrong error message returned")
                    return False
            
    except Exception as e:
        print(f"  - Wrong ID test failed: {e}")
        return False

def test_frontend_booking_id_usage():
    """Test that frontend uses booking.id correctly."""
    print("\nTesting frontend booking.id usage...")
    
    try:
        from app.routers.bookings import my_bookings_demo
        from app.database import SessionLocal
        
        with SessionLocal() as db:
            # Get bookings like frontend would
            bookings = my_bookings_demo(db)
            print(f"  - Retrieved {len(bookings)} bookings")
            
            if len(bookings) > 0:
                # Check booking structure
                sample_booking = bookings[0]
                print(f"  - Sample booking structure: {sample_booking}")
                
                # Verify booking has id field
                if 'id' in sample_booking:
                    booking_id = sample_booking['id']
                    print(f"  - Booking has ID: {booking_id}")
                    print("  - Frontend can use booking.id correctly")
                    return True
                else:
                    print("  - Booking missing 'id' field")
                    return False
            else:
                print("  - No bookings found to test")
                return False
            
    except Exception as e:
        print(f"  - Frontend booking ID test failed: {e}")
        return False

def main():
    """Run all cancel booking ID tests."""
    print("Cancel Booking ID Test Suite")
    print("=" * 40)
    
    tests = [
        ("Cancel Booking with Correct ID", test_cancel_booking_with_correct_id),
        ("Cancel Booking with Wrong ID", test_cancel_booking_with_wrong_id),
        ("Frontend Booking ID Usage", test_frontend_booking_id_usage),
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
    print("CANCEL BOOKING ID TEST RESULTS")
    print("=" * 40)
    
    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  {status:6} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\nSUCCESS: Cancel booking ID usage is correct!")
        print("Frontend and backend are working together properly.")
    else:
        print("\nISSUES: Some cancel booking ID tests failed.")
        print("Check the test output above for details.")
    
    return passed == len(results)

if __name__ == "__main__":
    main()
