"""
Create a demo user for testing login functionality.
This creates a user that can be used for testing the login flow.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_demo_user():
    """Create a demo user for testing."""
    print("Creating Demo User...")
    print("=" * 30)
    
    try:
        from app.routers.users import create_user
        from app.database import SessionLocal
        from app.schemas import UserCreate
        
        with SessionLocal() as db:
            # Demo user data
            demo_user = UserCreate(
                email="demo@example.com",
                password="demo123"
            )
            
            print(f"Creating demo user: {demo_user.email}")
            
            # Create user
            user = create_user(demo_user, db)
            print(f"Demo user created successfully: ID={user.id}, Email={user.email}")
            
            print("\nDemo Login Credentials:")
            print("Email: demo@example.com")
            print("Password: demo123")
            
            return True
            
    except Exception as e:
        print(f"Demo user creation failed: {e}")
        if "already registered" in str(e):
            print("Demo user already exists - that's fine!")
            return True
        import traceback
        traceback.print_exc()
        return False

def main():
    """Create demo user."""
    success = create_demo_user()
    
    if success:
        print("\nSUCCESS: Demo user is ready for testing!")
        print("\nYou can now:")
        print("  - Login with demo@example.com / demo123")
        print("  - Create new accounts")
        print("  - Test the full authentication flow")
    else:
        print("\nFAILED: Could not create demo user")
    
    return success

if __name__ == "__main__":
    main()
