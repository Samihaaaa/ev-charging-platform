from pydantic import BaseModel


class UserCreate(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True


class StationCreate(BaseModel):
    name: str
    latitude: float
    longitude: float
    charger_type: str
    power_kw: int
    price_inr: int = 0


class StationResponse(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float
    charger_type: str
    power_kw: int
    price_inr: int

    class Config:
        from_attributes = True


class BookingCreate(BaseModel):
    station_id: int
    time_slot: str


class CheckoutSessionCreate(BaseModel):
    station_id: int
    time_slot: str