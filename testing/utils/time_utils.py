from datetime import datetime, timezone
import math

SECONDS_PER_YEAR = 365 * 24 * 60 * 60


def time_to_expiry_years(expiration_iso_utc: str) -> float:
    """
    expiration_iso_utc: "2026-01-20T21:00:00.000+00:00"
    """
    now = datetime.now(timezone.utc)
    expiration = datetime.fromisoformat(expiration_iso_utc.replace("Z", "+00:00"))

    seconds_left = (expiration - now).total_seconds()

    # Prevent T = 0
    seconds_left = max(seconds_left, 60)

    return seconds_left / SECONDS_PER_YEAR
