"""
Debug login authentication to identify why correct password shows 'Invalid credentials'.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def debug_login_process():
    """Debug the complete login process step by step."""
    print("Debug Login Process")
    print("=" * 30)
    
    try:
        from app.database import SessionLocal
        from app import models
        from app.auth import verify_password, get_password_hash
        from fastapi.security import OAuth2PasswordRequestForm
        
        # Test credentials
        test_email = "fixed@example.com"
        test_password = "fixed123"
        
        print(f"Testing login for: {test_email}")
        print(f"Password: {test_password}")
        
        with SessionLocal() as db:
            # Step 1: Check if user exists
            print("\nStep 1: Checking if user exists...")
            user = db.query(models.User).filter(models.User.email == test_email).first()
            
            if not user:
                print(f"User {test_email} not found in database")
                return False
            
            print(f"User found: ID={user.id}, Email={user.email}")
            print(f"Stored password hash: {user.password[:50]}...")
            
            # Step 2: Test password hashing
            print("\nStep 2: Testing password hashing...")
            new_hash = get_password_hash(test_password)
            print(f"New hash for '{test_password}': {new_hash[:50]}...")
            
            # Step 3: Test password verification with stored hash
            print("\nStep 3: Testing password verification...")
            try:
                is_valid = verify_password(test_password, user.password)
                print(f"Password verification result: {is_valid}")
                
                if not is_valid:
                    print("Password verification failed - this is the issue!")
                    
                    # Let's try manual verification
                    print("\nManual verification attempts:")
                    import hashlib
                    
                    # Test SHA256
                    sha256_hash = hashlib.sha256(test_password.encode()).hexdigest()
                    print(f"SHA256 hash: {sha256_hash[:50]}...")
                    print(f"Matches stored hash: {sha256_hash == user.password}")
                    
                    # Test if stored hash is SHA256
                    if user.password == sha256_hash:
                        print("Stored hash is SHA256 - verification should work")
                    else:
                        print("Stored hash is not SHA256 - might be bcrypt")
                        
                        # Try to verify with bcrypt directly
                        try:
                            from passlib.context import CryptContext
                            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
                            bcrypt_result = pwd_context.verify(test_password, user.password)
                            print(f"Bcrypt verification result: {bcrypt_result}")
                        except Exception as e:
                            print(f"Bcrypt verification failed: {e}")
                
                else:
                    print("Password verification succeeded!")
                    
            except Exception as e:
                print(f"Password verification crashed: {e}")
                import traceback
                traceback.print_exc()
            
            # Step 4: Test complete login process
            print("\nStep 4: Testing complete login process...")
            try:
                from app.routers.auth import login
                
                form_data = OAuth2PasswordRequestForm(
                    username=test_email,
                    password=test_password
                )
                
                result = login(form_data, db)
                print(f"Complete login result: {result}")
                
                if "access_token" in result:
                    print("Login successful!")
                    return True
                else:
                    print("Login failed - no access token")
                    return False
                    
            except Exception as e:
                print(f"Complete login failed: {e}")
                return False
            
    except Exception as e:
        print(f"Debug process failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run debug process."""
    success = debug_login_process()
    
    print("\n" + "=" * 30)
    print("DEBUG RESULTS")
    print("=" * 30)
    
    if success:
        print("Login process is working correctly")
        print("The issue might be in the frontend")
    else:
        print("Login process has issues in the backend")
        print("Check the debug output above for details")

if __name__ == "__main__":
    main()
