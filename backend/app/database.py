from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

from .core.config import DATABASE_URL

# SQLite database for local development
print(f"Connecting to SQLite database: {DATABASE_URL}")

# Create SQLite engine with proper connect_args for local development
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Required for SQLite
)

# Test the connection
try:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("SQLite database connection successful")
except Exception as e:
    print(f"SQLite database connection failed: {e}")
    raise

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()