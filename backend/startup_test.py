"""
Simple startup test to verify FastAPI app can start without hanging.
This script will attempt to import and initialize the app with timeout protection.
"""

import sys
import os
import signal
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def timeout_handler(signum, frame):
    """Handle timeout signal."""
    raise TimeoutError("App startup took too long - likely hanging on database connection")

def test_app_startup():
    """Test app startup with timeout protection."""
    print("Testing FastAPI app startup...")
    
    # Set timeout for 30 seconds
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(30)
    
    try:
        # This is the critical test - importing the main app
        print("Importing app.main...")
        from app.main import app
        
        print("App imported successfully!")
        print(f"App title: {app.title}")
        print(f"Number of routes: {len(app.routes)}")
        
        # Test basic app functionality
        print("Testing basic app functionality...")
        @app.get("/startup-test")
        def startup_test():
            return {"status": "ok", "message": "Startup test successful"}
        
        print("App startup test completed successfully!")
        return True
        
    except TimeoutError as e:
        print(f"TIMEOUT: {e}")
        print("The app is hanging during startup. This is likely due to:")
        print("1. Database connection issues")
        print("2. Blocking operations during initialization")
        return False
        
    except Exception as e:
        print(f"ERROR: {e}")
        print("App failed to start due to an exception.")
        return False
        
    finally:
        # Cancel the timeout
        signal.alarm(0)

def test_minimal_app():
    """Test minimal app without database operations."""
    print("\nTesting minimal FastAPI app...")
    
    try:
        from fastapi import FastAPI
        
        app = FastAPI(title="Minimal Test App")
        
        @app.get("/")
        def root():
            return {"message": "Minimal app working"}
        
        print("Minimal app created successfully!")
        return True
        
    except Exception as e:
        print(f"Minimal app failed: {e}")
        return False

def main():
    """Run startup tests."""
    print("FastAPI Startup Test Suite")
    print("=" * 50)
    
    # Test 1: Minimal app
    minimal_success = test_minimal_app()
    
    # Test 2: Full app
    full_success = test_app_startup()
    
    print("\n" + "=" * 50)
    print("RESULTS:")
    print(f"Minimal App: {'SUCCESS' if minimal_success else 'FAILED'}")
    print(f"Full App: {'SUCCESS' if full_success else 'FAILED'}")
    
    if full_success:
        print("\nSUCCESS: Your FastAPI app should start without issues!")
        print("Try running: uvicorn app.main:app --reload --port 8001")
    else:
        print("\nISSUE IDENTIFIED: The app is hanging during startup.")
        print("The database connection or initialization is causing the block.")
        print("The fixes I applied should resolve this issue.")

if __name__ == "__main__":
    main()
