from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import users
from app.routers import auth
from app.routers import bookings
from app.routers import stations


app = FastAPI()


# CORS middleware (THIS FIXES YOUR REGISTER ISSUE)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# include routers
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(bookings.router)
app.include_router(stations.router)


@app.get("/")
def root():
    return {"message": "EV Charging Platform API running"}