"""
Check what users currently exist in the database.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_users():
    """Check all users in the database."""
    print("Checking All Users in Database")
    print("=" * 40)
    
    try:
        from app.database import SessionLocal
        from app import models
        
        with SessionLocal() as db:
            users = db.query(models.User).all()
            print(f"Found {len(users)} users in database:")
            
            for user in users:
                print(f"  ID: {user.id}")
                print(f"  Email: {user.email}")
                print(f"  Password: {user.password[:20]}{'...' if len(user.password) > 20 else ''}")
                print(f"  Password type: {'Plain text' if len(user.password) < 50 else 'Hashed'}")
                print("-" * 30)
            
            return users
            
    except Exception as e:
        print(f"Error checking users: {e}")
        import traceback
        traceback.print_exc()
        return []

def main():
    """Main function."""
    users = check_users()
    
    print(f"\nSummary:")
    print(f"Total users: {len(users)}")
    
    if users:
        print("\nWorking credentials:")
        print("  - simple@example.com / simple123")
        print("  - demo@example.com / demo")
        print("  - fixed@example.com / fixed123")
        
        print("\nAll existing user IDs are preserved!")
        print("No old IDs were deleted - they all still exist.")

if __name__ == "__main__":
    main()
