# runtime/context/trading_day_context.py
from market.market_flow import should_trade_today


def should_trade_today_now(
    *,
    last_trade_date,
    schedule_name: str,
    logger,
    trade_report_csv: str,
) -> bool:
    """
    Runtime-Policy:
    Entscheidet, ob für ein Schedule heute noch ein Trade erlaubt ist.
    """
    return should_trade_today(
        last_trade_date=last_trade_date,
        csv_file=trade_report_csv,
        schedule_name=schedule_name,
        logger=logger,
    )