"""
Test the fixed authentication system with proper password verification.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_password_verification():
    """Test password verification with debug logs."""
    print("Testing Password Verification")
    print("=" * 40)
    
    try:
        from app.auth import get_password_hash, verify_password
        
        # Test password
        test_password = "test123"
        print(f"Testing password: {test_password}")
        
        # Hash the password
        hashed = get_password_hash(test_password)
        print(f"Hashed password: {hashed[:50]}...")
        
        # Verify the password
        is_valid = verify_password(test_password, hashed)
        print(f"Verification result: {is_valid}")
        
        if is_valid:
            print("Password verification works correctly!")
        else:
            print("Password verification failed!")
            
        return is_valid
        
    except Exception as e:
        print(f"Password verification test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_existing_users():
    """Test login with existing users."""
    print("\nTesting Existing Users")
    print("=" * 40)
    
    try:
        from app.database import SessionLocal
        from app import models
        from app.auth import verify_password
        
        with SessionLocal() as db:
            users = db.query(models.User).all()
            print(f"Found {len(users)} users")
            
            for user in users:
                print(f"\nTesting user: {user.email}")
                print(f"Password hash: {user.password[:50]}...")
                
                # Try common passwords
                test_passwords = ["demo123", "fixed123", "test123", "password", "demo"]
                
                for pwd in test_passwords:
                    is_valid = verify_password(pwd, user.password)
                    if is_valid:
                        print(f"  SUCCESS: Password '{pwd}' works for {user.email}")
                        return True, user.email, pwd
                    else:
                        print(f"  Failed: Password '{pwd}' doesn't work")
            
            print("No working passwords found for existing users")
            return False, None, None
            
    except Exception as e:
        print(f"Existing users test failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None, None

def test_complete_login():
    """Test complete login process."""
    print("\nTesting Complete Login")
    print("=" * 40)
    
    try:
        from app.routers.auth import login
        from app.database import SessionLocal
        from fastapi.security import OAuth2PasswordRequestForm
        
        with SessionLocal() as db:
            # Test with known working credentials
            form_data = OAuth2PasswordRequestForm(
                username="fixed@example.com",
                password="fixed123"
            )
            
            print(f"Testing login for: {form_data.username}")
            
            try:
                result = login(form_data, db)
                print(f"Login successful: {result}")
                return True
            except Exception as e:
                print(f"Login failed: {e}")
                return False
                
    except Exception as e:
        print(f"Complete login test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all authentication tests."""
    print("Fixed Authentication Test Suite")
    print("=" * 50)
    
    tests = [
        ("Password Verification", test_password_verification),
        ("Existing Users", test_existing_users),
        ("Complete Login", test_complete_login),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            if test_name == "Existing Users":
                result, email, password = test_func()
                results.append((test_name, result, f"{email}/{password}" if email and password else ""))
            else:
                result = test_func()
                results.append((test_name, result, ""))
        except Exception as e:
            print(f"Test {test_name} crashed: {e}")
            results.append((test_name, False, ""))
    
    print("\n" + "=" * 50)
    print("FIXED AUTHENTICATION TEST RESULTS")
    print("=" * 50)
    
    for test_name, result, details in results:
        status = "PASS" if result else "FAIL"
        print(f"  {status:6} {test_name}")
        if details:
            print(f"         {details}")
    
    passed = sum(1 for _, result, _ in results if result)
    
    if passed == len(results):
        print("\nSUCCESS: Fixed authentication is working!")
        print("\nLogin should now work correctly.")
    else:
        print(f"\nISSUES: {len(results) - passed} tests failed.")
        print("Check the debug output above for details.")

if __name__ == "__main__":
    main()
