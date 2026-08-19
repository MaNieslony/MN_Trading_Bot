# trade/pricing.py
from __future__ import annotations

from typing import Tuple, Optional


def round_to_tick(*, symbol: str, price: float) -> float:
    tick = 0.02 if (symbol or "").upper() == "NDX" else 0.05
    return round(price / tick) * tick


def price_legs_credit(*, symbol: str, legs, tickers) -> Tuple[Optional[float], Optional[float]]:
    mid_pos = 0.0
    nat_pos = 0.0

    for leg in legs:
        t = tickers[leg["ticker_index"]]
        qty = float(leg["qty"])
        action = (leg["action"] or "").upper()

        if not (t.bid and t.ask and t.bid > 0 and t.ask > 0):
            return None, None

        leg_mid = (t.bid + t.ask) / 2.0

        if action == "SELL":
            mid_pos += leg_mid * qty
            nat_pos += t.bid * qty
        else:  # BUY
            mid_pos -= leg_mid * qty
            nat_pos -= t.ask * qty

    credit_mid = -round_to_tick(symbol=symbol, price=mid_pos)
    credit_nat = -round_to_tick(symbol=symbol, price=nat_pos)
    return credit_mid, credit_nat


def price_2leg_credit(
    *,
    symbol: str,
    expiry: str,
    leg1: float,
    leg2: float,
    trading_class: str,
    leg1_put_call: str,
    leg2_put_call: str,
    leg1_action: str,
    leg2_action: str,
    leg1_qty: int,
    leg2_qty: int,
    get_option_conid_callable=None,
    wait_for_ticker_data_callable=None,
    logger=None,
    timeout: float = 1.0,
    tickers=None,
    req_tickers_callable=None,
) -> Tuple[Optional[float], Optional[float]]:
    """
    Price a 2-leg credit combo. If `tickers` is provided, it will be used and no reqTickers call is made.
    Returns (credit_mid, credit_natural) in IB-style NEGATIVE credits.
    """
    if tickers is None:
        if req_tickers_callable is None or get_option_conid_callable is None:
            raise ValueError(
                "price_2leg_credit requires get_option_conid_callable and req_tickers_callable when tickers is None"
            )
        if wait_for_ticker_data_callable is None:
            raise ValueError("price_2leg_credit requires wait_for_ticker_data_callable when tickers is None")

        c1 = get_option_conid_callable(expiry, leg1, leg1_put_call, trading_class)
        c2 = get_option_conid_callable(expiry, leg2, leg2_put_call, trading_class)

        if not c1 or not c2:
            if logger:
                logger.warning("2-leg: failed to qualify one or more option contracts")
            return None, None

        tickers = req_tickers_callable(c1, c2)

        if not wait_for_ticker_data_callable(tickers, timeout=timeout):
            if logger:
                logger.warning("2-leg: ticker timeout")
            return None, None

    legs = [
        {"action": leg1_action, "qty": leg1_qty, "ticker_index": 0},
        {"action": leg2_action, "qty": leg2_qty, "ticker_index": 1},
    ]

    credit_mid, credit_natural = price_legs_credit(symbol=symbol, legs=legs, tickers=tickers)

    if credit_mid is None or credit_natural is None:
        if logger:
            logger.warning("2-leg: invalid bid/ask data")
        return None, None

    return credit_mid, credit_natural

def price_3leg_credit(
    *,
    symbol: str,
    expiry: str,
    leg1: float,
    leg2: float,
    leg3: float,
    trading_class: str,
    leg1_put_call: str,
    leg2_put_call: str,
    leg3_put_call: str,
    leg1_action: str,
    leg2_action: str,
    leg3_action: str,
    leg1_qty: int,
    leg2_qty: int,
    leg3_qty: int,
    get_option_conid_callable=None,
    wait_for_ticker_data_callable=None,
    logger=None,
    timeout: float = 1.0,
    tickers=None,
    req_tickers_callable=None,
) -> Tuple[Optional[float], Optional[float]]:
    """
    Price a 3-leg credit combo. If `tickers` is provided, it will be used and no reqTickers call is made.
    Returns (credit_mid, credit_natural) in IB-style NEGATIVE credits.
    """

    if tickers is None:
        if req_tickers_callable is None or get_option_conid_callable is None:
            raise ValueError(
                "price_3leg_credit requires get_option_conid_callable and req_tickers_callable when tickers is None"
            )
        if wait_for_ticker_data_callable is None:
            raise ValueError("price_3leg_credit requires wait_for_ticker_data_callable when tickers is None")

        c1 = get_option_conid_callable(expiry, leg1, leg1_put_call, trading_class)
        c2 = get_option_conid_callable(expiry, leg2, leg2_put_call, trading_class)
        c3 = get_option_conid_callable(expiry, leg3, leg3_put_call, trading_class)

        if not c1 or not c2 or not c3:
            if logger:
                logger.warning("3-leg: failed to qualify one or more option contracts")
            return None, None

        tickers = req_tickers_callable(c1, c2, c3)

        if not wait_for_ticker_data_callable(tickers, timeout=timeout):
            if logger:
                logger.warning("3-leg: ticker timeout")
            return None, None

    legs = [
        {"action": leg1_action, "qty": leg1_qty, "ticker_index": 0},
        {"action": leg2_action, "qty": leg2_qty, "ticker_index": 1},
        {"action": leg3_action, "qty": leg3_qty, "ticker_index": 2},
    ]

    credit_mid, credit_natural = price_legs_credit(symbol=symbol, legs=legs, tickers=tickers)

    if credit_mid is None or credit_natural is None:
        if logger:
            logger.warning("3-leg: invalid bid/ask data")
        return None, None

    return credit_mid, credit_natural