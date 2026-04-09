import stripe

from ..core.config import STRIPE_SECRET_KEY


def get_stripe_client() -> stripe.StripeClient:
    if not STRIPE_SECRET_KEY:
        raise RuntimeError("STRIPE_SECRET_KEY is not set")
    return stripe.Stripe(api_key=STRIPE_SECRET_KEY)

