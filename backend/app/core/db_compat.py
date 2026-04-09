from __future__ import annotations

from sqlalchemy import inspect

from ..database import engine


def table_has_column(table_name: str, column_name: str) -> bool:
    """
    Runtime compatibility helper.

    This project’s DB schema evolved during monetization work (new columns like
    `stations.price_cents`, `bookings.status`, payment metadata).
    If those columns don't exist yet in the user's current Postgres DB,
    we want the API to keep working instead of 500’ing.
    """
    try:
        inspector = inspect(engine)
        cols = inspector.get_columns(table_name)
    except Exception:
        # If the table doesn't exist or can't be inspected, treat as missing.
        return False

    return any(c.get("name") == column_name for c in cols)

