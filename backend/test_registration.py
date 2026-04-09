"""
Test the registration endpoint to identify why account creation fails.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_registration_endpoint():
    """Test the registration endpoint directly."""
    print("Testing Registration Endpoint")
    print("=" * 40)
    
    try:
        from app.routers.users import create_user
        from app.database import SessionLocal
        from app.schemas import UserCreate
        
        with SessionLocal() as db:
            # Test user data
            test_user = UserCreate(
                email="testuser@example.com",
                password="testpass123"
            )
            
            print(f"Creating user: {test_user.email}")
            print(f"Password: {test_user.password}")
            
            try:
                # Create user
                user = create_user(test_user, db)
                print(f"User created successfully: ID={user.id}, Email={user.email}")
                print(f"Password hash: {user.password[:30]}...")
                return True
            except Exception as e:
                print(f"Registration failed: {e}")
                print(f"Error type: {type(e)}")
                
                # Check if it's an HTTPException
                if hasattr(e, 'status_code'):
                    print(f"Status code: {e.status_code}")
                    print(f"Detail: {e.detail}")
                
                return False
            
    except Exception as e:
        print(f"Test setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_duplicate_email():
    """Test duplicate email handling."""
    print("\nTesting Duplicate Email Handling")
    print("=" * 40)
    
    try:
        from app.routers.users import create_user
        from app.database import SessionLocal
        from app.schemas import UserCreate
        
        with SessionLocal() as db:
            # Try to create user with existing email
            test_user = UserCreate(
                email="demo@example.com",  # This already exists
                password="testpass123"
            )
            
            print(f"Trying to create duplicate user: {test_user.email}")
            
            try:
                user = create_user(test_user, db)
                print(f"Unexpected success: {user}")
                return False
            except Exception as e:
                print(f"Expected error: {e}")
                if "already registered" in str(e) or "409" in str(e):
                    print("Duplicate email handling works correctly")
                    return True
                else:
                    print("Unexpected error for duplicate email")
                    return False
            
    except Exception as e:
        print(f"Duplicate test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_password_hashing():
    """Test password hashing in registration."""
    print("\nTesting Password Hashing")
    print("=" * 30)
    
    try:
        from app.auth import get_password_hash
        
        test_password = "testpass123"
        print(f"Testing password: {test_password}")
        
        try:
            hashed = get_password_hash(test_password)
            print(f"Hashed successfully: {hashed[:30]}...")
            return True
        except Exception as e:
            print(f"Password hashing failed: {e}")
            return False
            
    except Exception as e:
        print(f"Password hashing test failed: {e}")
        return False

def main():
    """Run all registration tests."""
    print("Registration Test Suite")
    print("=" * 40)
    
    tests = [
        ("Password Hashing", test_password_hashing),
        ("Registration Endpoint", test_registration_endpoint),
        ("Duplicate Email", test_duplicate_email),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 40)
    print("REGISTRATION TEST RESULTS")
    print("=" * 40)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  {status:6} {test_name}")
    
    passed = sum(1 for _, result in results if result)
    
    if passed == len(results):
        print("\nSUCCESS: Registration is working!")
        print("The issue might be in the frontend.")
    else:
        print(f"\nISSUES: {len(results) - passed} tests failed.")
        print("Check the test output above for details.")
    
    return passed == len(results)

if __name__ == "__main__":
    main()
