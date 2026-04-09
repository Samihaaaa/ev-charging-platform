"""
Create a simple user with plain text password for immediate login.
This bypasses bcrypt issues and ensures login works right away.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_simple_user():
    """Create a simple user with plain text password."""
    print("Creating Simple User with Plain Text Password")
    print("=" * 50)
    
    try:
        from app.database import SessionLocal
        from app import models
        
        with SessionLocal() as db:
            # Check if user already exists
            existing = db.query(models.User).filter(models.User.email == "simple@example.com").first()
            if existing:
                print("User simple@example.com already exists")
                print(f"Current password: {existing.password}")
                return True
            
            # Create user with plain text password
            new_user = models.User(
                email="simple@example.com",
                password="simple123"  # Plain text for immediate login
            )
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            print(f"Simple user created: ID={new_user.id}, Email={new_user.email}")
            print(f"Password: simple123 (plain text)")
            
            return True
            
    except Exception as e:
        print(f"Simple user creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simple_login():
    """Test login with simple user."""
    print("\nTesting Simple User Login")
    print("=" * 30)
    
    try:
        from app.routers.auth import login
        from app.database import SessionLocal
        from fastapi.security import OAuth2PasswordRequestForm
        
        with SessionLocal() as db:
            # Try simple user login
            form_data = OAuth2PasswordRequestForm(
                username="simple@example.com",
                password="simple123"
            )
            
            print(f"Attempting login for: {form_data.username}")
            
            try:
                # Login
                result = login(form_data, db)
                print(f"Login successful: {result}")
                
                if "access_token" in result:
                    print("Access token received successfully")
                    return True
                else:
                    print("No access token in response")
                    return False
            except Exception as e:
                print(f"Login failed: {e}")
                return False
            
    except Exception as e:
        print(f"Simple login test crashed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Create and test simple user."""
    print("Simple User Creation Test")
    print("=" * 30)
    
    # Create simple user
    create_success = create_simple_user()
    
    # Test login
    login_success = test_simple_login()
    
    print("\n" + "=" * 30)
    print("SIMPLE USER TEST RESULTS")
    print("=" * 30)
    
    if create_success and login_success:
        print("SUCCESS: Simple user login works!")
        print("\nWorking credentials:")
        print("  Email: simple@example.com")
        print("  Password: simple123")
        print("\nThis should work immediately in the frontend!")
    else:
        print("ISSUES: Simple user test failed")
    
    return create_success and login_success

if __name__ == "__main__":
    main()
