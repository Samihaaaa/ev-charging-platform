from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import CORS_ALLOW_ORIGINS

from app.routers import users
from app.routers import auth
from app.routers import bookings
from app.routers import stations
from app.routers import payments
from app.database import Base, engine


from sqlalchemy import text
from app.core.db_compat import table_has_column

app = FastAPI()

# Create database tables for SQLite
# SQLite creates the database file automatically if it doesn't exist
try:
    print("Creating SQLite database tables...")
    Base.metadata.create_all(bind=engine)
    print("SQLite database tables created successfully")
except Exception as e:
    print(f"[Database] Failed to create tables: {e}")
    print("Application will continue but database operations may fail")

# Seed Bangalore EV charging stations data
# Use ultra-safe seeding implementation that never crashes
try:
    print("Initializing EV charging stations data...")
    from app.seed_data_safe import seed_stations_safely
    success = seed_stations_safely()
    if success:
        print("EV charging stations initialization completed successfully")
    else:
        print("EV charging stations seeding failed, but app continues...")
except ImportError as e:
    print(f"Failed to import seed_data_safe module: {e}")
except Exception as e:
    print(f"Unexpected error during seeding: {e}")
    print("Continuing without seeding data...")


# CORS middleware (THIS FIXES YOUR REGISTER ISSUE)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# include routers
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(bookings.router)
app.include_router(stations.router)
app.include_router(payments.router)


@app.get("/")
def root():
    return {"message": "EV Charging Platform API running"}