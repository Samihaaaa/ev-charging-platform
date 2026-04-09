"""
Test script to verify the complete booking and payment flow.
This tests the realistic booking system without authentication.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_payment_simulation():
    """Test the payment simulation endpoint."""
    print("Testing payment simulation...")
    
    try:
        from app.routers.payments import create_checkout_session
        from app.database import SessionLocal
        from app.schemas import CheckoutSessionCreate
        
        with SessionLocal() as db:
            # Create test payload
            payload = CheckoutSessionCreate(
                station_id=1,
                time_slot="10am-11am"
            )
            
            # Test payment simulation
            result = create_checkout_session(payload, db)
            print(f"  - Payment result: {result}")
            
            if result.get("status") == "success":
                print("  - Payment simulation successful")
                return True, result.get("booking_id")
            else:
                print(f"  - Payment failed: {result.get('error')}")
                return False, None
                
    except Exception as e:
        print(f"  - Payment test failed: {e}")
        return False, None

def test_slot_locking():
    """Test that slot locking prevents double bookings."""
    print("\nTesting slot locking...")
    
    try:
        from app.routers.payments import create_checkout_session
        from app.database import SessionLocal
        from app.schemas import CheckoutSessionCreate
        
        with SessionLocal() as db:
            # Create test payload for same slot
            payload = CheckoutSessionCreate(
                station_id=1,
                time_slot="10am-11am"
            )
            
            # Try to book the same slot again
            result = create_checkout_session(payload, db)
            print(f"  - Second booking result: {result}")
            
            if result.get("status") == "error" and result.get("error") == "Slot already booked":
                print("  - Slot locking working correctly")
                return True
            else:
                print("  - Slot locking failed - double booking allowed")
                return False
                
    except Exception as e:
        print(f"  - Slot locking test failed: {e}")
        return False

def test_available_slots():
    """Test that booked slots are hidden from available slots."""
    print("\nTesting available slots endpoint...")
    
    try:
        from app.routers.stations import available_slots
        from app.database import SessionLocal
        
        with SessionLocal() as db:
            # Get available slots for station 1
            result = available_slots(1, db)
            print(f"  - Available slots result: {result}")
            
            available_slots_list = result.get("available_slots", [])
            all_slots = result.get("all_slots", [])
            
            print(f"  - All slots: {all_slots}")
            print(f"  - Available slots: {available_slots_list}")
            
            # Check if "10am-11am" is hidden (should be booked from previous test)
            if "10am-11am" not in available_slots_list and "10am-11am" in all_slots:
                print("  - Booked slot correctly hidden from available slots")
                return True
            else:
                print("  - Booked slot not properly hidden")
                return False
                
    except Exception as e:
        print(f"  - Available slots test failed: {e}")
        return False

def test_booking_cancellation():
    """Test booking cancellation endpoint."""
    print("\nTesting booking cancellation...")
    
    try:
        from app.routers.bookings import cancel_booking_demo
        from app.database import SessionLocal
        
        # First, get a booking ID to cancel
        from app.routers.payments import create_checkout_session
        from app.schemas import CheckoutSessionCreate
        
        with SessionLocal() as db:
            # Create a new booking to cancel
            payload = CheckoutSessionCreate(
                station_id=1,
                time_slot="11am-12pm"
            )
            
            result = create_checkout_session(payload, db)
            booking_id = result.get("booking_id")
            
            if not booking_id:
                print("  - Could not create booking for cancellation test")
                return False
            
            print(f"  - Created booking {booking_id} for cancellation test")
            
            # Cancel the booking
            cancel_result = cancel_booking_demo(booking_id, db)
            print(f"  - Cancellation result: {cancel_result}")
            
            if cancel_result.get("status") == "success":
                print("  - Booking cancellation successful")
                return True
            else:
                print("  - Booking cancellation failed")
                return False
                
    except Exception as e:
        print(f"  - Cancellation test failed: {e}")
        return False

def test_slot_freed_after_cancellation():
    """Test that slots become available after cancellation."""
    print("\nTesting slot availability after cancellation...")
    
    try:
        from app.routers.stations import available_slots
        from app.database import SessionLocal
        
        with SessionLocal() as db:
            # Get available slots for station 1
            result = available_slots(1, db)
            available_slots_list = result.get("available_slots", [])
            
            print(f"  - Available slots after cancellation: {available_slots_list}")
            
            # Check if "11am-12am" is now available (should be freed after cancellation)
            if "11am-12pm" in available_slots_list:
                print("  - Slot correctly freed after cancellation")
                return True
            else:
                print("  - Slot not freed after cancellation")
                return False
                
    except Exception as e:
        print(f"  - Slot availability test failed: {e}")
        return False

def test_database_state():
    """Test the overall database state."""
    print("\nTesting database state...")
    
    try:
        from app.database import SessionLocal
        from app import models
        
        with SessionLocal() as db:
            # Count bookings
            booking_count = db.query(models.Booking).count()
            print(f"  - Total bookings in database: {booking_count}")
            
            # Count stations
            station_count = db.query(models.ChargingStation).count()
            print(f"  - Total stations in database: {station_count}")
            
            # Show recent bookings
            recent_bookings = db.query(models.Booking).limit(3).all()
            print("  - Recent bookings:")
            for booking in recent_bookings:
                status = getattr(booking, 'status', 'unknown')
                print(f"    * Booking {booking.id}: Station {booking.station_id}, Slot {booking.time_slot}, Status {status}")
            
            return True
            
    except Exception as e:
        print(f"  - Database state test failed: {e}")
        return False

def main():
    """Run all booking flow tests."""
    print("Complete Booking Flow Test Suite")
    print("=" * 50)
    
    tests = [
        ("Payment Simulation", test_payment_simulation),
        ("Slot Locking", test_slot_locking),
        ("Available Slots", test_available_slots),
        ("Booking Cancellation", test_booking_cancellation),
        ("Slot Freed After Cancellation", test_slot_freed_after_cancellation),
        ("Database State", test_database_state),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            if test_name == "Payment Simulation":
                result, booking_id = test_func()
                results.append((test_name, result))
            else:
                result = test_func()
                results.append((test_name, result))
        except Exception as e:
            print(f"Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("BOOKING FLOW TEST RESULTS")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  {status:6} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\nSUCCESS: Complete booking flow is working!")
        print("Users can now:")
        print("  - Book charging slots without authentication")
        print("  - See realistic payment success messages")
        print("  - Have slots locked to prevent double bookings")
        print("  - Cancel bookings to free slots")
        print("  - See real-time slot availability")
    else:
        print("\nISSUES: Some booking flow tests failed.")
        print("Check the test output above for details.")
    
    return passed == len(results)

if __name__ == "__main__":
    main()
