from datetime import datetime, time
import pytz

NY = pytz.timezone("America/New_York")

TRADING_MINUTES_PER_DAY = 390      # 6.5 hours
TRADING_DAYS_PER_YEAR = 252
MINUTES_PER_YEAR = TRADING_MINUTES_PER_DAY * TRADING_DAYS_PER_YEAR


def time_to_expiry_years(days_to_expiration: int) -> float:
    now = datetime.now(NY)

    market_close = NY.localize(
        datetime.combine(now.date(), time(16, 0))
    )

    if now >= market_close:
        remaining_today = 0
    else:
        remaining_today = (market_close - now).seconds / 60

    if days_to_expiration == 0:
        minutes_left = remaining_today
    else:
        minutes_left = (
            (days_to_expiration - 1) * TRADING_MINUTES_PER_DAY
            + remaining_today
        )

    # Floor to avoid T = 0
    minutes_left = max(minutes_left, 1)

    return minutes_left / MINUTES_PER_YEAR
