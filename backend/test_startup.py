"""
Test script to verify backend startup without running the full server.
This helps identify import and initialization issues.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all imports work correctly."""
    print("🧪 Testing imports...")
    
    try:
        print("  - Importing database...")
        from app.database import SessionLocal, Base, engine
        print("    ✅ Database imports successful")
        
        print("  - Importing models...")
        from app import models
        print("    ✅ Models imports successful")
        
        print("  - Importing seed_data...")
        from app.seed_data import seed_stations_safely, get_bangalore_ev_stations
        print("    ✅ Seed data imports successful")
        
        print("  - Importing main app components...")
        from app.main import app
        print("    ✅ Main app imports successful")
        
        return True
    except Exception as e:
        print(f"    ❌ Import failed: {e}")
        return False

def test_database_connection():
    """Test database connection and basic operations."""
    print("\n🔌 Testing database connection...")
    
    try:
        from app.database import SessionLocal
        from app import models
        from app.database import Base, engine
        
        # Create tables
        print("  - Creating tables...")
        Base.metadata.create_all(bind=engine)
        print("    ✅ Tables created successfully")
        
        # Test session
        print("  - Testing database session...")
        with SessionLocal() as db:
            count = db.query(models.ChargingStation).count()
            print(f"    ✅ Database session successful (found {count} stations)")
        
        return True
    except Exception as e:
        print(f"    ❌ Database test failed: {e}")
        return False

def test_seeding():
    """Test the seeding functionality."""
    print("\n🌱 Testing seeding functionality...")
    
    try:
        from app.seed_data import seed_stations_safely, get_bangalore_ev_stations
        
        # Test station data generation
        print("  - Testing station data generation...")
        stations = get_bangalore_ev_stations()
        print(f"    ✅ Generated {len(stations)} station records")
        
        # Test actual seeding
        print("  - Testing seeding process...")
        success = seed_stations_safely()
        if success:
            print("    ✅ Seeding completed successfully")
        else:
            print("    ⚠️  Seeding returned False (may not be an error if data exists)")
        
        return True
    except Exception as e:
        print(f"    ❌ Seeding test failed: {e}")
        return False

def test_app_creation():
    """Test FastAPI app creation."""
    print("\n🚀 Testing FastAPI app creation...")
    
    try:
        # This will test the entire main.py import process
        print("  - Importing main app...")
        from app.main import app
        print("    ✅ FastAPI app created successfully")
        
        # Test basic app properties
        print(f"  - App title: {app.title}")
        print("    ✅ App properties accessible")
        
        return True
    except Exception as e:
        print(f"    ❌ App creation failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🔍 Backend Startup Test Suite")
    print("=" * 40)
    
    tests = [
        ("Imports", test_imports),
        ("Database Connection", test_database_connection),
        ("Seeding", test_seeding),
        ("App Creation", test_app_creation),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n📊 Test Results:")
    print("=" * 40)
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Backend should start successfully.")
        return True
    else:
        print("⚠️  Some tests failed. Backend may have startup issues.")
        return False

if __name__ == "__main__":
    main()
