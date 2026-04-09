"""
Simple test to verify the database connection fix works.
This tests the specific SQLAlchemy text() fix.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_database_connection():
    """Test that the database connection works with text() wrapper."""
    print("Testing database connection with text() wrapper...")
    
    try:
        from app.database import engine
        
        print(f"  - Database URL: {engine.url}")
        
        # Test connection the same way database.py does
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).fetchone()
            print(f"  - Connection test result: {result}")
        
        print("  - Database connection successful!")
        return True
        
    except Exception as e:
        print(f"  - Database connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_app_import():
    """Test that the app can be imported without errors."""
    print("\nTesting app import...")
    
    try:
        from app.main import app
        print(f"  - App imported successfully: {app.title}")
        return True
    except Exception as e:
        print(f"  - App import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the connection test."""
    print("Database Connection Fix Test")
    print("=" * 40)
    
    # Test database connection
    db_success = test_database_connection()
    
    # Test app import
    app_success = test_app_import()
    
    print("\n" + "=" * 40)
    print("RESULTS:")
    print(f"Database Connection: {'PASS' if db_success else 'FAIL'}")
    print(f"App Import: {'PASS' if app_success else 'FAIL'}")
    
    if db_success and app_success:
        print("\nSUCCESS: SQLAlchemy execution error is fixed!")
        print("The backend should start without database errors.")
    else:
        print("\nISSUES: Some tests failed.")
        print("Check the error messages above.")
    
    return db_success and app_success

if __name__ == "__main__":
    # Import text for the test
    from sqlalchemy import text
    main()
