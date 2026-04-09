import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, Base, engine
from app import models
from sqlalchemy import text

print("Connecting to DB...")
try:
    print(f"DATABASE_URL is: {engine.url}")
    # Initialize DB (if not already done, though it should be)
    Base.metadata.create_all(bind=engine)

    # Make sure we have price_inr
    with engine.begin() as conn:
        try:
            # Check if price_inr exists
            res = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='stations' AND column_name='price_inr'"))
            if not res.fetchone():
                print("Adding price_inr column...")
                conn.execute(text("ALTER TABLE stations ADD COLUMN price_inr INTEGER"))
        except Exception as e:
            print(f"Postgres column check error: {e}")
            try:
                # SQLite fallback check
                res = conn.execute(text("PRAGMA table_info(stations)"))
                columns = [row[1] for row in res.fetchall()]
                if 'price_inr' not in columns:
                    print("Adding price_inr column (SQLite)...")
                    conn.execute(text("ALTER TABLE stations ADD COLUMN price_inr INTEGER"))
            except Exception as inner_e:
                pass


    with SessionLocal() as db:
        existing = db.query(models.ChargingStation).filter(models.ChargingStation.name == "MG Road Charger").first()
        if not existing:
            print("Seeding realistic Bangalore stations...")
            bangalore_stations = [
                {"name": "MG Road Charger", "latitude": 12.9719, "longitude": 77.6013, "charger_type": "DC Fast", "power_kw": 150, "price_inr": 800},
                {"name": "Indiranagar Charging Point", "latitude": 12.9784, "longitude": 77.6408, "charger_type": "AC", "power_kw": 22, "price_inr": 400},
                {"name": "Whitefield Supercharger", "latitude": 12.9698, "longitude": 77.7499, "charger_type": "DC Fast", "power_kw": 250, "price_inr": 1200},
                {"name": "Electronic City Station", "latitude": 12.8452, "longitude": 77.6602, "charger_type": "AC", "power_kw": 22, "price_inr": 350},
                {"name": "Koramangala EV Hub", "latitude": 12.9352, "longitude": 77.6245, "charger_type": "DC Fast", "power_kw": 120, "price_inr": 900},
                {"name": "Yelahanka Charging Point", "latitude": 13.1007, "longitude": 77.5963, "charger_type": "AC", "power_kw": 11, "price_inr": 300},
                {"name": "Jayanagar Eco Station", "latitude": 12.9250, "longitude": 77.5938, "charger_type": "DC Fast", "power_kw": 60, "price_inr": 700},
                {"name": "HSR Layout Supercharger", "latitude": 12.9121, "longitude": 77.6446, "charger_type": "DC Fast", "power_kw": 200, "price_inr": 1000},
                {"name": "Malleshwaram Hub", "latitude": 13.0031, "longitude": 77.5700, "charger_type": "AC", "power_kw": 22, "price_inr": 450},
                {"name": "Marathahalli Fast Charge", "latitude": 12.9569, "longitude": 77.7011, "charger_type": "DC Fast", "power_kw": 150, "price_inr": 850},
            ]
            for st in bangalore_stations:
                db.add(models.ChargingStation(**st))
            db.commit()
            print(f"Successfully seeded {len(bangalore_stations)} stations.")
        else:
            print("Stations already exist in DB.")
        
        count = db.query(models.ChargingStation).count()
        print(f"Total stations in DB: {count}")

except Exception as e:
    print(f"Error during seeding: {e}")
