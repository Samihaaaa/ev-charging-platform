from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from .database import Base


class ChargingStation(Base):
    __tablename__ = "stations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    charger_type = Column(String)
    power_kw = Column(Integer)
    # Pricing (in INR).
    # Intentionally no Python-side default for DB compatibility.
    # If you insert without this column and the DB schema doesn't have it,
    # we don't want SQLAlchemy to reference it.
    price_inr = Column(Integer)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    station_id = Column(Integer, ForeignKey("stations.id"))
    time_slot = Column(String)
    # Booking lifecycle for monetization.
    # - pending: payment started but not confirmed
    # - paid: webhook confirmed payment
    # - cancelled: booking cancelled/refunded/failed
    #
    # Intentionally no Python-side defaults for DB compatibility.
    status = Column(String, index=True)

    amount_cents = Column(Integer)
    currency = Column(String)

    checkout_session_id = Column(String, nullable=True)
    payment_intent_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)