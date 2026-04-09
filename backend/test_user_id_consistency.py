"""
Test script to verify user_id consistency across booking creation, fetching, and cancellation.
This ensures all operations use user_id = 1 consistently.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_booking_creation_user_id():
    """Test that booking creation uses user_id = 1."""
    print("Testing booking creation with user_id = 1...")
    
    try:
        from app.routers.payments import create_checkout_session
        from app.database import SessionLocal
        from app.schemas import CheckoutSessionCreate
        
        with SessionLocal() as db:
            # Create a booking
            payload = CheckoutSessionCreate(
                station_id=1,
                time_slot="9am-10am"
            )
            
            result = create_checkout_session(payload, db)
            print(f"  - Booking creation result: {result}")
            
            if result.get("status") == "success":
                booking_id = result.get("booking_id")
                print(f"  - Booking created with ID: {booking_id}")
                
                # Verify the booking was created with user_id = 1
                from app import models
                booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
                if booking:
                    actual_user_id = getattr(booking, 'user_id', None)
                    print(f"  - Actual user_id in database: {actual_user_id}")
                    
                    if actual_user_id == 1:
                        print("  - Booking created with correct user_id = 1")
                        return True, booking_id
                    else:
                        print(f"  - Booking created with wrong user_id: {actual_user_id}")
                        return False, booking_id
                else:
                    print("  - Booking not found in database")
                    return False, None
            else:
                print(f"  - Booking creation failed: {result.get('error')}")
                return False, None
                
    except Exception as e:
        print(f"  - Booking creation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def test_my_bookings_user_id():
    """Test that my-bookings returns bookings for user_id = 1."""
    print("\nTesting my-bookings with user_id = 1...")
    
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
                
                # Verify all bookings are for user_id = 1 by checking database directly
                from app import models
                booking_ids = [b.get('id') for b in bookings]
                
                for booking_id in booking_ids:
                    db_booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
                    if db_booking:
                        actual_user_id = getattr(db_booking, 'user_id', None)
                        if actual_user_id != 1:
                            print(f"  - Booking {booking_id} has wrong user_id: {actual_user_id}")
                            return False
                
                print("  - All bookings have correct user_id = 1")
                return True, bookings
            else:
                print("  - No bookings found")
                return False, []
                
    except Exception as e:
        print(f"  - My bookings test failed: {e}")
        import traceback
        traceback.print_exc()
        return False, []

def test_cancellation_user_id():
    """Test that cancellation works for bookings with user_id = 1."""
    print("\nTesting cancellation for user_id = 1 bookings...")
    
    try:
        # First create a booking to cancel
        from app.routers.payments import create_checkout_session
        from app.routers.bookings import cancel_booking_demo_simple
        from app.database import SessionLocal
        from app.schemas import CheckoutSessionCreate
        
        with SessionLocal() as db:
            # Create a booking
            payload = CheckoutSessionCreate(
                station_id=1,
                time_slot="10am-11am"
            )
            
            result = create_checkout_session(payload, db)
            booking_id = result.get("booking_id")
            
            if not booking_id:
                print("  - Could not create booking for cancellation test")
                return False
            
            print(f"  - Created booking {booking_id} for cancellation")
            
            # Verify booking has user_id = 1
            from app import models
            booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
            if booking and getattr(booking, 'user_id', None) == 1:
                print("  - Booking has correct user_id = 1")
            else:
                print("  - Booking does not have user_id = 1")
                return False
            
            # Cancel the booking
            cancel_result = cancel_booking_demo_simple(booking_id, db)
            print(f"  - Cancellation result: {cancel_result}")
            
            if cancel_result.get("status") == "success":
                print("  - Booking cancelled successfully")
                
                # Verify booking status is now cancelled
                updated_booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
                if updated_booking:
                    new_status = getattr(updated_booking, 'status', None)
                    print(f"  - Updated booking status: {new_status}")
                    
                    if new_status == "cancelled":
                        print("  - Booking status correctly updated to 'cancelled'")
                        return True
                    else:
                        print(f"  - Booking status not updated correctly: {new_status}")
                        return False
                else:
                    print("  - Booking not found after cancellation")
                    return False
            else:
                print("  - Booking cancellation failed")
                return False
                
    except Exception as e:
        print(f"  - Cancellation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

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
            
            # Check if "10am-11am" is available (should be freed after cancellation)
            if "10am-11am" in available_slots_list:
                print("  - Slot correctly freed after cancellation")
                return True
            else:
                print("  - Slot not freed after cancellation")
                return False
                
    except Exception as e:
        print(f"  - Slot availability test failed: {e}")
        return False

def test_database_consistency():
    """Test database consistency for user_id = 1."""
    print("\nTesting database consistency...")
    
    try:
        from app.database import SessionLocal
        from app import models
        
        with SessionLocal() as db:
            # Count all bookings
            total_bookings = db.query(models.Booking).count()
            print(f"  - Total bookings in database: {total_bookings}")
            
            # Count bookings with user_id = 1
            user_id_1_bookings = db.query(models.Booking).filter(models.Booking.user_id == 1).count()
            print(f"  - Bookings with user_id = 1: {user_id_1_bookings}")
            
            # Count confirmed bookings with user_id = 1
            confirmed_bookings = db.query(models.Booking).filter(
                models.Booking.user_id == 1,
                models.Booking.status == "confirmed"
            ).count()
            print(f"  - Confirmed bookings with user_id = 1: {confirmed_bookings}")
            
            # Count cancelled bookings with user_id = 1
            cancelled_bookings = db.query(models.Booking).filter(
                models.Booking.user_id == 1,
                models.Booking.status == "cancelled"
            ).count()
            print(f"  - Cancelled bookings with user_id = 1: {cancelled_bookings}")
            
            # Verify user exists
            user = db.query(models.User).filter(models.User.id == 1).first()
            if user:
                print(f"  - User with ID = 1 exists: {user.email}")
            else:
                print("  - User with ID = 1 does not exist")
                return False
            
            return True
            
    except Exception as e:
        print(f"  - Database consistency test failed: {e}")
        return False

def main():
    """Run all user_id consistency tests."""
    print("User ID Consistency Test Suite")
    print("=" * 50)
    
    tests = [
        ("Booking Creation (user_id = 1)", test_booking_creation_user_id),
        ("My Bookings (user_id = 1)", test_my_bookings_user_id),
        ("Cancellation (user_id = 1)", test_cancellation_user_id),
        ("Slot Availability After Cancellation", test_slot_availability_after_cancellation),
        ("Database Consistency", test_database_consistency),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            if test_name == "Booking Creation (user_id = 1)":
                result, booking_id = test_func()
                results.append((test_name, result))
            elif test_name == "My Bookings (user_id = 1)":
                result, bookings = test_func()
                results.append((test_name, result))
            else:
                result = test_func()
                results.append((test_name, result))
        except Exception as e:
            print(f"Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("USER ID CONSISTENCY TEST RESULTS")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  {status:6} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\nSUCCESS: User ID consistency is working perfectly!")
        print("All operations use user_id = 1 consistently:")
        print("  - Booking creation uses user_id = 1")
        print("  - My Bookings fetches user_id = 1 bookings")
        print("  - Cancellation works for user_id = 1 bookings")
        print("  - Slots free up correctly after cancellation")
        print("  - Database state is consistent")
    else:
        print("\nISSUES: Some user_id consistency tests failed.")
        print("Check the debug output above for details.")
    
    return passed == len(results)

if __name__ == "__main__":
    main()
