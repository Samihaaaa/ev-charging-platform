import os
from typing import Optional


def _env(name: str, default: Optional[str] = None) -> str:
    value = os.getenv(name, default)
    if value is None:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


# Database
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./ev.db",
)

# JWT
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecretkey")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_HOURS = int(os.getenv("ACCESS_TOKEN_EXPIRE_HOURS", "2"))

# CORS
_cors = os.getenv("CORS_ALLOW_ORIGINS", "*")
if _cors.strip() == "*":
    CORS_ALLOW_ORIGINS = ["*"]
else:
    CORS_ALLOW_ORIGINS = [x.strip() for x in _cors.split(",") if x.strip()]

# Stripe
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
STRIPE_CURRENCY = os.getenv("STRIPE_CURRENCY", "usd")
USE_MOCK_PAYMENT = True

# Frontend URLs used by Stripe Checkout redirects.
FRONTEND_SUCCESS_URL = os.getenv(
    "FRONTEND_SUCCESS_URL",
    "http://127.0.0.1:5500/frontend/dashboard.html?checkout=success",
)
FRONTEND_CANCEL_URL = os.getenv(
    "FRONTEND_CANCEL_URL",
    "http://127.0.0.1:5500/frontend/dashboard.html?checkout=cancel",
)

