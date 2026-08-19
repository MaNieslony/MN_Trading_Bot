# runtime/context/market_wait_context.py
from datetime import datetime, timedelta
import pytz

def wait_for_market_open_now(
    *,
    check_market_open: bool,
    market_open_time,
    market_close_time,
    interruptible_sleep,
    broker,
    logger,
):
    """
    Wait until the market opens if it's currently closed.
    Handles weekends, pre-market, after-hours and reconnects.
    """

    if not check_market_open:
        return

    et_tz = pytz.timezone("US/Eastern")
    reconnect_before_open = 300  # seconds (5 min)

    while True:
        now_et = datetime.now(et_tz)
        current_time = now_et.time()
        current_day = now_et.weekday()

        # ------------------------------------------------------------
        # WEEKEND
        # ------------------------------------------------------------
        if current_day >= 5:
            days_until_monday = (7 - current_day) % 7 or 1

            next_open = now_et.replace(
                hour=market_open_time.hour,
                minute=market_open_time.minute,
                second=0,
                microsecond=0,
            ) + timedelta(days=days_until_monday)

            logger.info(f"Weekend - market opens {next_open.strftime('%A at %H:%M')} ET")

            if broker.check_connection_health():
                broker.disconnect()

            _sleep_until_reconnect(
                now_et, next_open, reconnect_before_open, interruptible_sleep, logger
            )

            if not broker.reconnect():
                logger.error("Failed to reconnect - aborting")
                return

            if not interruptible_sleep(reconnect_before_open):
                return

            continue

        # ------------------------------------------------------------
        # PRE-MARKET
        # ------------------------------------------------------------
        if current_time < market_open_time:
            market_open_today = now_et.replace(
                hour=market_open_time.hour,
                minute=market_open_time.minute,
                second=0,
                microsecond=0,
            )

            logger.info(
                f"Pre-market: {(market_open_today - now_et).total_seconds()/60:.1f} min until open"
            )

            if broker.check_connection_health():
                broker.disconnect()

            _sleep_until_reconnect(
                now_et, market_open_today, reconnect_before_open, interruptible_sleep, logger
            )

            if not broker.reconnect():
                logger.error("Failed to reconnect - aborting")
                return

            if not interruptible_sleep(reconnect_before_open):
                return

            continue

        # ------------------------------------------------------------
        # AFTER HOURS
        # ------------------------------------------------------------
        if current_time > market_close_time:
            next_open = now_et.replace(
                hour=market_open_time.hour,
                minute=market_open_time.minute,
                second=0,
                microsecond=0,
            ) + timedelta(days=1)

            while next_open.weekday() >= 5:
                next_open += timedelta(days=1)

            logger.info(f"After hours - market opens {next_open.strftime('%A at %H:%M')} ET")

            if broker.check_connection_health():
                broker.disconnect()

            _sleep_until_reconnect(
                now_et, next_open, reconnect_before_open, interruptible_sleep, logger
            )

            if not broker.reconnect():
                logger.error("Failed to reconnect - aborting")
                return

            if not interruptible_sleep(reconnect_before_open):
                return

            continue

        # ------------------------------------------------------------
        # MARKET OPEN
        # ------------------------------------------------------------
        logger.info(f"✅ Market open ({now_et.strftime('%H:%M')} ET) - proceeding")
        return


def _sleep_until_reconnect(now, target, reconnect_before_open, sleep_fn, logger):
    wait_seconds = (target - now).total_seconds()
    long_wait = max(0, wait_seconds - reconnect_before_open)

    while long_wait > 0:
        chunk = min(3600, long_wait)
        if not sleep_fn(chunk):
            logger.info("Wait interrupted")
            return
        long_wait -= chunk