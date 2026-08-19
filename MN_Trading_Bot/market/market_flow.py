# market/market_flow.py
from datetime import datetime, timedelta, time as dt_time
import pytz
import time
import os
import pandas as pd
from typing import List


# ------------------------------------------------------------------
# MARKET HOURS
# ------------------------------------------------------------------

def is_market_open(
    now_et: datetime,
    market_open: dt_time,
    market_close: dt_time,
    check_market_open: bool,
    logger
) -> bool:
    if not check_market_open:
        logger.info("Market hours check disabled - proceeding")
        return True

    if now_et.weekday() >= 5:
        logger.warning(f"Market closed - Weekend ({now_et.strftime('%A')})")
        return False

    current_time = now_et.time()
    if market_open <= current_time <= market_close:
        return True

    logger.warning(
        f"Market closed - Outside hours "
        f"({current_time.strftime('%H:%M')} ET, "
        f"{market_open.strftime('%H:%M')}–{market_close.strftime('%H:%M')} ET)"
    )
    return False


# ------------------------------------------------------------------
# EXECUTION TIME WAIT
# ------------------------------------------------------------------

def wait_for_execution_time(
    execution_time: dt_time,
    check_execution_time: bool,
    interruptible_sleep,
    logger
) -> bool:
    if not check_execution_time:
        logger.debug("Execution time check disabled")
        return True

    et = pytz.timezone("US/Eastern")
    now = datetime.now(et)

    entry_dt = now.replace(
        hour=execution_time.hour,
        minute=execution_time.minute,
        second=execution_time.second,
        microsecond=0
    )

    grace_end = entry_dt + timedelta(minutes=15)

    if now > grace_end:
        logger.warning("⏰ Bot started too late – trading blocked today")
        return False

    if now < entry_dt:
        wait_seconds = (entry_dt - now).total_seconds()
        logger.info(f"Waiting until execution time ({wait_seconds/60:.1f} min)")
        if not interruptible_sleep(wait_seconds):
            return False

    logger.info("✓ Execution time reached")
    return True


# ------------------------------------------------------------------
# TRADE-ONCE-PER-DAY CHECK
# ------------------------------------------------------------------

def check_if_schedule_traded_today(
    csv_file: str,
    schedule_name: str,
    logger
) -> bool:
    if not os.path.exists(csv_file):
        return False

    try:
        df = pd.read_csv(csv_file)

        required_cols = {"Trade date and time", "Notes", "SCHEDULE_NAME"}
        if df.empty or not required_cols.issubset(df.columns):
            return False

        df["Trade date and time"] = pd.to_datetime(
            df["Trade date and time"],
            errors="coerce",
        )

        today = datetime.now().date()

        entry_rows = df[
            (~df["Notes"].str.contains("Exit", na=False)) &
            (df["SCHEDULE_NAME"] == schedule_name) &
            (df["Trade date and time"].dt.date == today)
        ]

        return not entry_rows.empty

    except Exception as e:
        logger.warning(f"CSV schedule trade check failed: {e}")
        return False

def should_trade_today(
    *,
    last_trade_date,
    csv_file: str,
    schedule_name: str,
    logger,
):
    today = datetime.now().date()

    # ------------------------------------------------------------
    # Fast cache guard (per Schedule, wenn du last_trade_date so führst)
    # ------------------------------------------------------------
    if last_trade_date == today:
        logger.info(
            f"Already traded today for schedule '{schedule_name}' (cached)"
        )
        return False

    # ------------------------------------------------------------
    # CSV guard: per Schedule
    # ------------------------------------------------------------
    if check_if_schedule_traded_today(
        csv_file=csv_file,
        schedule_name=schedule_name,
        logger=logger,
    ):
        logger.info(
            f"Already traded today for schedule '{schedule_name}' (CSV)"
        )
        return False

    logger.info(
        f"✓ No trades today for schedule '{schedule_name}'"
    )
    return True


# ------------------------------------------------------------------
# TICKER DATA WAIT
# ------------------------------------------------------------------

def wait_for_ticker_data(
    tickers: List,
    timeout: float,
    wait_for_greeks: bool = False
) -> bool:
    start = time.time()

    while time.time() - start < timeout:
        if wait_for_greeks:
            if all(t.modelGreeks for t in tickers):
                return True
        else:
            if all(t.bid > 0 and t.ask > 0 for t in tickers):
                return True

        #time.sleep(0.05)

    return False