"""
Create a new demo user with fixed password hashing.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_fixed_demo_user():
    """Create a demo user with fixed password hashing."""
    print("Creating Fixed Demo User...")
    print("=" * 30)
    
    try:
        from app.database import SessionLocal
        from app import models
        from app.auth import get_password_hash
        
        with SessionLocal() as db:
            # Check if user already exists
            existing = db.query(models.User).filter(models.User.email == "fixed@example.com").first()
            if existing:
                print("User fixed@example.com already exists")
                return True
            
            # Create user with fixed password hashing
            hashed_password = get_password_hash("fixed123")
            print(f"Hashed password: {hashed_password[:50]}...")
            
            new_user = models.User(
                email="fixed@example.com",
                password=hashed_password
            )
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            print(f"Fixed demo user created: ID={new_user.id}, Email={new_user.email}")
            
            return True
            
    except Exception as e:
        print(f"Fixed demo user creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fixed_login():
    """Test login with fixed demo user."""
    print("\nTesting Fixed Demo Login...")
    print("=" * 30)
    
    try:
        from app.routers.auth import login
        from app.database import SessionLocal
        from fastapi.security import OAuth2PasswordRequestForm
        
        with SessionLocal() as db:
            # Try fixed demo user login
            form_data = OAuth2PasswordRequestForm(
                username="fixed@example.com",
                password="fixed123"
            )
            
            print(f"Attempting fixed demo login for: {form_data.username}")
            
            try:
                # Login
                result = login(form_data, db)
                print(f"Fixed demo login successful: {result}")
                
                if "access_token" in result:
                    print("Access token received successfully")
                    return True
                else:
                    print("No access token in response")
                    return False
            except Exception as e:
                print(f"Fixed demo login failed: {e}")
                return False
            
    except Exception as e:
        print(f"Fixed demo login test crashed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Create and test fixed demo user."""
    print("Fixed Demo User Test")
    print("=" * 30)
    
    # Create fixed demo user
    create_success = create_fixed_demo_user()
    
    # Test login
    login_success = test_fixed_login()
    
    print("\n" + "=" * 30)
    print("FIXED DEMO TEST RESULTS")
    print("=" * 30)
    
    if create_success and login_success:
        print("SUCCESS: Fixed demo user works!")
        print("\nYou can now:")
        print("  - Login with fixed@example.com / fixed123")
        print("  - The frontend should work for login")
        print("  - Registration should work for new users")
    else:
        print("ISSUES: Fixed demo user test failed")
        print("But the password hashing should be more reliable now")
    
    return create_success and login_success

if __name__ == "__main__":
    main()
