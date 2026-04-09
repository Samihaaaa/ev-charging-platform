"""
Diagnostic script to identify what's blocking FastAPI startup.
This will test each component individually to find the bottleneck.
"""

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_step(step_name, test_func):
    """Test a single step and report timing."""
    print(f"\n{'='*50}")
    print(f"Testing: {step_name}")
    print('='*50)
    
    start_time = time.time()
    try:
        result = test_func()
        end_time = time.time()
        duration = end_time - start_time
        print(f"Result: {'SUCCESS' if result else 'FAILED'}")
        print(f"Duration: {duration:.2f} seconds")
        return result, duration
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        print(f"Result: EXCEPTION - {e}")
        print(f"Duration: {duration:.2f} seconds")
        return False, duration

def test_basic_imports():
    """Test basic Python imports."""
    print("Importing basic modules...")
    import fastapi
    import uvicorn
    print(f"FastAPI version: {fastapi.__version__}")
    return True

def test_fastapi_creation():
    """Test FastAPI app creation."""
    print("Creating FastAPI app...")
    from fastapi import FastAPI
    app = FastAPI()
    
    @app.get("/test")
    def test_endpoint():
        return {"message": "test"}
    
    print("FastAPI app created successfully")
    return True

def test_database_imports():
    """Test database-related imports."""
    print("Importing database modules...")
    from app.database import SessionLocal, Base, engine
    print("Database imports successful")
    return True

def test_database_connection():
    """Test database connection."""
    print("Testing database connection...")
    from app.database import SessionLocal
    try:
        with SessionLocal() as db:
            # Simple test query
            result = db.execute("SELECT 1").fetchone()
            print(f"Database query result: {result}")
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

def test_model_imports():
    """Test model imports."""
    print("Importing models...")
    from app import models
    print(f"Available models: {[name for name in dir(models) if not name.startswith('_')]}")
    return True

def test_seed_data_imports():
    """Test seed data imports."""
    print("Importing seed data...")
    from app.seed_data import get_bangalore_ev_stations
    stations = get_bangalore_ev_stations()
    print(f"Station data loaded: {len(stations)} stations")
    return True

def test_seeding_function():
    """Test seeding function (without actually seeding)."""
    print("Testing seeding function availability...")
    from app.seed_data import seed_stations_safely
    print("Seeding function imported successfully")
    # Don't actually run seeding to avoid database changes
    return True

def test_config_imports():
    """Test configuration imports."""
    print("Importing configuration...")
    from app.core.config import CORS_ALLOW_ORIGINS
    print(f"CORS origins: {CORS_ALLOW_ORIGINS}")
    return True

def test_router_imports():
    """Test router imports."""
    print("Importing routers...")
    from app.routers import stations
    from app.routers import users
    from app.routers import auth
    from app.routers import bookings
    from app.routers import payments
    print("All routers imported successfully")
    return True

def test_full_app_import():
    """Test importing the full main app."""
    print("Importing full main app...")
    from app.main import app
    print(f"App title: {app.title}")
    print(f"App routes: {len(app.routes)} routes")
    return True

def main():
    """Run all diagnostic tests."""
    print("FastAPI Startup Diagnostic Tool")
    print("This will help identify what's causing the startup delay/failure")
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("FastAPI Creation", test_fastapi_creation),
        ("Database Imports", test_database_imports),
        ("Database Connection", test_database_connection),
        ("Model Imports", test_model_imports),
        ("Config Imports", test_config_imports),
        ("Router Imports", test_router_imports),
        ("Seed Data Imports", test_seed_data_imports),
        ("Seeding Function", test_seeding_function),
        ("Full App Import", test_full_app_import),
    ]
    
    results = []
    total_time = 0
    
    for test_name, test_func in tests:
        success, duration = test_step(test_name, test_func)
        results.append((test_name, success, duration))
        total_time += duration
        
        # If a test takes more than 5 seconds, it's likely the problem
        if duration > 5:
            print(f"\n*** WARNING: {test_name} took {duration:.2f} seconds! ***")
            print("This is likely causing the startup issue.")
    
    print(f"\n{'='*50}")
    print("DIAGNOSTIC SUMMARY")
    print('='*50)
    
    for test_name, success, duration in results:
        status = "SUCCESS" if success else "FAILED"
        time_indicator = "SLOW" if duration > 2 else "OK"
        print(f"{test_name:25} | {status:8} | {duration:6.2f}s | {time_indicator}")
    
    print(f"\nTotal time: {total_time:.2f} seconds")
    
    # Identify the bottleneck
    slow_tests = [(name, duration) for name, success, duration in results if duration > 2]
    if slow_tests:
        print(f"\nBOTTLENECKS IDENTIFIED:")
        for name, duration in slow_tests:
            print(f"  - {name}: {duration:.2f} seconds")
    else:
        print(f"\nNo major bottlenecks detected. Issue might be elsewhere.")

if __name__ == "__main__":
    main()
