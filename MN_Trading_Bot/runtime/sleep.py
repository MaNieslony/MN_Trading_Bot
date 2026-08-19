# runtime/sleep.py

import time

def interruptible_sleep(
    *,
    seconds,
    is_running_callable,
    ib,
    broker,
    logger
):
    remaining = seconds
    check_interval = 0.1

    while remaining > 0:
        if not is_running_callable():
            return False

        sleep_time = min(check_interval, remaining)
        time.sleep(sleep_time)

        if ib.isConnected():
            try:
                ib.sleep(0)
            except Exception:
                logger.warning("Connection lost during sleep - reconnecting")
                if not broker.reconnect():
                    logger.error("Reconnect failed")
                    return False

        remaining -= sleep_time

    return True