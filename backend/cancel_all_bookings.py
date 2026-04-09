"""
Script to cancel all existing bookings in the database.
Updates all booking records to status = "cancelled" without deleting them.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def cancel_all_bookings():
    """Cancel all bookings by setting status to 'cancelled'."""
    try:
        from app.database import SessionLocal
        from app import models
        
        with SessionLocal() as db:
            # Check if bookings table has status column
            has_status_column = False
            try:
                # Test if status column exists
                test_booking = db.query(models.Booking).first()
                if test_booking and hasattr(test_booking, 'status'):
                    has_status_column = True
                    print("Bookings table has 'status' column")
                else:
                    print("Bookings table does not have 'status' column")
            except Exception as e:
                print(f"Error checking status column: {e}")
            
            # Count total bookings before cancellation
            total_bookings = db.query(models.Booking).count()
            print(f"Total bookings in database: {total_bookings}")
            
            if total_bookings == 0:
                print("No bookings found in database. Nothing to cancel.")
                return True
            
            if has_status_column:
                # Update all bookings to status = "cancelled"
                from sqlalchemy import text
                
                # Use raw SQL for efficient bulk update
                update_result = db.execute(text("UPDATE bookings SET status = 'cancelled'"))
                db.commit()
                
                print(f"Updated {update_result.rowcount} bookings to status 'cancelled'")
                
                # Verify the update
                cancelled_count = db.query(models.Booking).filter(models.Booking.status == "cancelled").count()
                confirmed_count = db.query(models.Booking).filter(models.Booking.status == "confirmed").count()
                paid_count = db.query(models.Booking).filter(models.Booking.status == "paid").count()
                
                print(f"Verification:")
                print(f"  - Cancelled bookings: {cancelled_count}")
                print(f"  - Confirmed bookings: {confirmed_count}")
                print(f"  - Paid bookings: {paid_count}")
                
                if confirmed_count == 0 and paid_count == 0:
                    print("SUCCESS: All active bookings have been cancelled!")
                    return True
                else:
                    print("WARNING: Some active bookings remain")
                    return False
            else:
                # For legacy DBs without status column, we can't update status
                print("WARNING: Legacy database without status column")
                print("Cannot cancel bookings without status field")
                print("Consider migrating database to include status column")
                return False
                
    except Exception as e:
        print(f"Error cancelling all bookings: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_slots_available():
    """Verify that all slots are now available after cancellation."""
    try:
        from app.database import SessionLocal
        from app import models
        
        with SessionLocal() as db:
            # Check for any confirmed/paid bookings that would block slots
            has_status_column = False
            try:
                test_booking = db.query(models.Booking).first()
                if test_booking and hasattr(test_booking, 'status'):
                    has_status_column = True
            except:
                pass
            
            if has_status_column:
                active_bookings = db.query(models.Booking).filter(
                    models.Booking.status.in_(["confirmed", "paid"])
                ).count()
                
                print(f"Active bookings that block slots: {active_bookings}")
                
                if active_bookings == 0:
                    print("SUCCESS: All slots are now available!")
                    return True
                else:
                    print("WARNING: Some slots may still be blocked")
                    return False
            else:
                print("Cannot verify slot availability (legacy DB)")
                return True  # Assume success for legacy DB
                
    except Exception as e:
        print(f"Error verifying slot availability: {e}")
        return False

def main():
    """Main function to cancel all bookings and verify."""
    print("Cancel All Bookings Script")
    print("=" * 40)
    
    print("Step 1: Cancelling all bookings...")
    success = cancel_all_bookings()
    
    if success:
        print("\nStep 2: Verifying slot availability...")
        verify_success = verify_slots_available()
        
        if verify_success:
            print("\n" + "=" * 40)
            print("SUCCESS: All bookings cancelled!")
            print("All slots are now available for booking.")
            print("=" * 40)
        else:
            print("\n" + "=" * 40)
            print("PARTIAL SUCCESS: Bookings cancelled but verification failed")
            print("Please check the database manually.")
            print("=" * 40)
    else:
        print("\n" + "=" * 40)
        print("FAILED: Could not cancel all bookings")
        print("Please check the error messages above.")
        print("=" * 40)

if __name__ == "__main__":
    main()
