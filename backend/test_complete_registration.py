"""
Test complete registration flow from API to login.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_complete_registration_flow():
    """Test complete registration and login flow."""
    print("Complete Registration Flow Test")
    print("=" * 40)
    
    try:
        from app.routers.users import create_user
        from app.routers.auth import login
        from app.database import SessionLocal
        from app.schemas import UserCreate
        from fastapi.security import OAuth2PasswordRequestForm
        
        with SessionLocal() as db:
            # Step 1: Create a new user
            print("Step 1: Creating new user...")
            test_email = "newuser@example.com"
            test_password = "newpass123"
            
            test_user = UserCreate(
                email=test_email,
                password=test_password
            )
            
            try:
                user = create_user(test_user, db)
                print(f"User created: ID={user.id}, Email={user.email}")
                print(f"Password hash: {user.password[:30]}...")
            except Exception as e:
                if "already registered" in str(e):
                    print("User already exists, proceeding with login test")
                else:
                    raise e
            
            # Step 2: Test login with new user
            print(f"\nStep 2: Testing login with {test_email}...")
            form_data = OAuth2PasswordRequestForm(
                username=test_email,
                password=test_password
            )
            
            try:
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
        print(f"Complete registration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run complete registration test."""
    success = test_complete_registration_flow()
    
    print("\n" + "=" * 40)
    print("COMPLETE REGISTRATION TEST RESULTS")
    print("=" * 40)
    
    if success:
        print("SUCCESS: Complete registration flow works!")
        print("\nAccount creation should now work in the frontend!")
        print("\nTo test in frontend:")
        print("1. Go to registration page")
        print("2. Enter any email and password")
        print("3. Should create account successfully")
        print("4. Should be able to login with new credentials")
    else:
        print("ISSUES: Complete registration flow failed")
        print("Check the test output above for details")
    
    return success

if __name__ == "__main__":
    main()
