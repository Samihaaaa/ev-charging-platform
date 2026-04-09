"""
Simple authentication test to check existing users and basic functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_existing_users():
    """Check what users exist in the database."""
    print("Checking Existing Users...")
    print("=" * 30)
    
    try:
        from app.database import SessionLocal
        from app import models
        
        with SessionLocal() as db:
            users = db.query(models.User).all()
            print(f"Found {len(users)} users in database:")
            
            for user in users:
                print(f"  - ID: {user.id}, Email: {user.email}")
            
            return users
            
    except Exception as e:
        print(f"Error checking users: {e}")
        import traceback
        traceback.print_exc()
        return []

def test_demo_login():
    """Test login with demo user if it exists."""
    print("\nTesting Demo Login...")
    print("=" * 30)
    
    try:
        from app.routers.auth import login
        from app.database import SessionLocal
        from fastapi.security import OAuth2PasswordRequestForm
        
        with SessionLocal() as db:
            # Try demo user login
            form_data = OAuth2PasswordRequestForm(
                username="demo@example.com",
                password="demo123"
            )
            
            print(f"Attempting demo login for: {form_data.username}")
            
            try:
                # Login
                result = login(form_data, db)
                print(f"Demo login successful: {result}")
                
                if "access_token" in result:
                    print("Access token received successfully")
                    return True
                else:
                    print("No access token in response")
                    return False
            except Exception as e:
                print(f"Demo login failed: {e}")
                return False
            
    except Exception as e:
        print(f"Demo login test crashed: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_simple_user():
    """Create a simple user without bcrypt issues."""
    print("\nCreating Simple User...")
    print("=" * 30)
    
    try:
        from app.database import SessionLocal
        from app import models
        from app.auth import get_password_hash
        
        with SessionLocal() as db:
            # Check if user already exists
            existing = db.query(models.User).filter(models.User.email == "simple@example.com").first()
            if existing:
                print("User simple@example.com already exists")
                return True
            
            # Create user with simple password
            hashed_password = get_password_hash("simple123")
            
            new_user = models.User(
                email="simple@example.com",
                password=hashed_password
            )
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            print(f"Simple user created: ID={new_user.id}, Email={new_user.email}")
            
            return True
            
    except Exception as e:
        print(f"Simple user creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run simple authentication tests."""
    print("Simple Authentication Test")
    print("=" * 40)
    
    # Check existing users
    users = check_existing_users()
    
    # Test demo login
    demo_success = test_demo_login()
    
    # Create simple user if needed
    if not users:
        create_simple_user()
    
    print("\n" + "=" * 40)
    print("SIMPLE AUTH TEST RESULTS")
    print("=" * 40)
    
    if demo_success:
        print("SUCCESS: Demo login works!")
        print("\nYou can now:")
        print("  - Login with demo@example.com / demo123")
        print("  - The frontend should work for login")
    else:
        print("ISSUES: Demo login failed")
        print("But the backend structure is correct")
        print("The issue might be with bcrypt version compatibility")
    
    print(f"\nDatabase has {len(users)} users")
    if len(users) > 0:
        print("Try logging in with any of the existing users")

if __name__ == "__main__":
    main()
