# runtime/context/market_context.py
from datetime import datetime
import pytz

from market.market_flow import (
    is_market_open as _is_market_open,
    wait_for_execution_time as _wait_for_execution_time,
)

def is_market_open_now(
    *,
    market_open_time,
    market_close_time,
    check_market_open: bool,
    logger,
) -> bool:
    et = pytz.timezone("US/Eastern")
    now_et = datetime.now(et)

    return _is_market_open(
        now_et=now_et,
        market_open=market_open_time,
        market_close=market_close_time,
        check_market_open=check_market_open,
        logger=logger,
    )


def wait_for_execution_time_now(
    *,
    execution_time,
    check_execution_time: bool,
    interruptible_sleep,
    logger,
) -> bool:
    return _wait_for_execution_time(
        execution_time=execution_time,
        check_execution_time=check_execution_time,
        interruptible_sleep=interruptible_sleep,
        logger=logger,
    )