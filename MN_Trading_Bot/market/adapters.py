# market/adapters.py
from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional, Tuple

from market.market_data import get_open_price as _get_open_price
from market.market_data import get_current_price as _get_current_price
from market.market_data import get_rsi as _get_rsi
from market.market_data import get_sma as _get_sma
from market.market_data import get_vix_price as _get_vix_price
from market.option_chain import get_option_chain as _get_option_chain
from market.contracts import get_option_conid as _get_option_conid
from market.contracts import get_index_contract as _get_index_contract
from market.greeks import get_option_deltas as _get_option_deltas

# ---------------------------------------------------------------------------
# Cache Init (wichtig, weil cycle_steps auf diese Attribute zugreift)
# ---------------------------------------------------------------------------
def init_market_caches(bot) -> None:
    # Option Chain Preload Cache
    bot._cached_option_chain = None          # (trading_class, strikes)
    bot._cached_chain_expiry = None
    bot._cached_chain_timestamp = None

    # Delta Preload Cache
    bot._cached_deltas = None                # Dict[strike -> delta]
    bot._cached_deltas_expiry = None
    bot._cached_deltas_trading_class = None
    bot._cached_deltas_put_call = None
    bot._cached_deltas_strikes = None        # List[float]
    bot._cached_deltas_timestamp = None
    bot._cached_deltas_center = None
    bot._execution_delta_fetch_attempted = False

    # delta window state (cycle_steps nutzt das)
    bot._delta_window_center = None

# ---------------------------------------------------------------------------
# Contracts / Index
# ---------------------------------------------------------------------------
def get_option_conid_adapter(bot, expiry: str, strike: float, right: str, trading_class: str = None):
    return _get_option_conid(
        ib=bot.ib,
        symbol=bot.SYMBOL,
        expiry=expiry,
        strike=strike,
        right=right,
        trading_class=trading_class,
        logger=bot.logger,
        debug_mode=bot.DEBUG_MODE,
    )

# ---------------------------------------------------------------------------
# Option Chain Preload + Deltas Preload
# ---------------------------------------------------------------------------
def preload_option_chain_adapter(bot, expiry: str) -> None:
    """
    Side-effect only: fills bot._cached_option_chain + timestamp.
    Safe to call multiple times.
    """
    try:
        bot.logger.info(f"⏳ Preloading option chain for {bot.SYMBOL} expiry {expiry}")

        trading_class, strikes = _get_option_chain(
            ib=bot.ib,
            expiry=expiry,
            underlying_price=bot.underlying_price,
            get_index_contract_callable=bot.get_SPX_index_contract,
            logger=bot.logger,
            debug_mode=bot.DEBUG_MODE,
        )

        if trading_class and strikes:
            bot._cached_option_chain = (trading_class, strikes)
            bot._cached_chain_expiry = expiry
            bot._cached_chain_timestamp = datetime.now()

            bot.logger.info(f"✅ Option chain preloaded: {len(strikes)} strikes ({trading_class})")
        else:
            bot.logger.warning("⚠️ Option chain preload returned no data")

    except Exception as e:
        bot.logger.warning(f"⚠️ Option chain preload failed: {e}")

def preload_deltas_adapter(bot, expiry: str, trading_class: str, strikes_for_delta: List[float]) -> None:
    """
    Side-effect only: fills bot._cached_deltas + metadata.
    Safe to call multiple times.
    """
    try:
        if not trading_class or not strikes_for_delta:
            bot.logger.warning("⚠️ Delta preload skipped (missing trading_class or strikes)")
            return

        bot.logger.info(
            f"⏳ Preloading deltas for {bot.SYMBOL} {expiry} "
            f"({len(strikes_for_delta)} strikes, {bot.LEG1_PUT_CALL}, {trading_class})"
        )

        deltas = get_option_deltas_adapter(
            bot,
            expiry=expiry,
            strikes=strikes_for_delta,
            put_call=bot.LEG1_PUT_CALL,
            trading_class=trading_class,
        )

        if deltas:
            bot._cached_deltas = deltas
            bot._cached_deltas_expiry = expiry
            bot._cached_deltas_trading_class = trading_class
            bot._cached_deltas_put_call = bot.LEG1_PUT_CALL
            bot._cached_deltas_strikes = list(strikes_for_delta)
            bot._cached_deltas_timestamp = datetime.now()
            bot._cached_deltas_center = bot.underlying_price

            bot.logger.info(f"✅ Deltas preloaded: {len(deltas)} strikes cached")
        else:
            bot.logger.warning("⚠️ Delta preload returned no data")

    except Exception as e:
        bot.logger.warning(f"⚠️ Delta preload failed: {e}")


def preload_deltas_with_retries_adapter(
    bot,
    *,
    expiry: str,
    trading_class: str,
    strikes_for_delta: List[float],
    attempts: int = 3,
    sleep_seconds: float = 1.0,
) -> None:
    """
    Preload deltas with retries (pre-execution).
    Side-effect: fills bot._cached_deltas on success.
    """
    for i in range(1, attempts + 1):
        preload_deltas_adapter(bot, expiry, trading_class, strikes_for_delta)

        if bot._cached_deltas:
            bot.logger.info(f"✅ Delta preload succeeded on attempt {i}/{attempts}")
            return

        bot.logger.warning(f"⚠️ Delta preload attempt {i}/{attempts} returned no data")
        # kleine Pause hilft IB oft (nicht zu lang, Pre-Execution ist ok)
        try:
            bot.ib.sleep(sleep_seconds)
        except Exception:
            pass


def ensure_deltas_at_execution_adapter(
    bot,
    *,
    expiry: str,
    trading_class: str,
    strikes_for_delta: List[float],
) -> None:
    """
    Execution-phase: if no cache available, try exactly once synchronously.
    Side-effect: fills bot._cached_deltas on success.
    """
    if bot._cached_deltas:
        return

    bot.logger.info("No delta cache at execution – attempting ONE synchronous delta fetch")
    preload_deltas_adapter(bot, expiry, trading_class, strikes_for_delta)

    if bot._cached_deltas:
        bot.logger.info(f"✅ Delta cache filled at execution: {len(bot._cached_deltas)} strikes")
    else:
        bot.logger.warning("⚠️ Delta fetch at execution failed – continuing without blocking further")


def build_strikes_for_delta_adapter(bot, strikes: List[float]) -> List[float]:
    strikes_for_delta = strikes

    strike_lower_offset = getattr(bot, "STRIKE_LOWER_OFFSET", None)
    strike_upper_offset = getattr(bot, "STRIKE_UPPER_OFFSET", None)

    if strike_lower_offset is not None and strike_upper_offset is not None:
        lower = bot.underlying_price - float(strike_lower_offset)
        upper = bot.underlying_price - float(strike_upper_offset)
        strikes_for_delta = [s for s in strikes if lower <= s <= upper]

    return sorted(strikes_for_delta)

# ---------------------------------------------------------------------------
# Prices / Indicators
# ---------------------------------------------------------------------------
def get_current_price_adapter(bot) -> Optional[float]:
    price = _get_current_price(
        ib=bot.ib,
        symbol=bot.SYMBOL,
        get_index_contract_callable=bot.get_SPX_index_contract,
        logger=bot.logger,
    )
    if price is not None:
        bot.underlying_price = price
    return price

def get_open_price_adapter(bot) -> Optional[float]:
    price = _get_open_price(
        ib=bot.ib,
        symbol=bot.SYMBOL,
        get_index_contract_callable=bot.get_SPX_index_contract,
        logger=bot.logger,
    )
    if price is not None:
        bot.open_price = price
    return price

def get_rsi_adapter(bot, period: int = 14, bar_size: str = "1 day") -> Optional[float]:
    return _get_rsi(
        ib=bot.ib,
        symbol=bot.SYMBOL,
        get_index_contract_callable=bot.get_SPX_index_contract,
        period=period,
        bar_size=bar_size,
        logger=bot.logger,
    )

def get_sma_adapter(bot, period: int, bar_size: str = "1 day"):
    return _get_sma(
        ib=bot.ib,
        symbol=bot.SYMBOL,
        get_index_contract_callable=bot.get_SPX_index_contract,
        period=period,
        bar_size=bar_size,
        logger=bot.logger,
    )

def get_vix_adapter(bot) -> Optional[float]:
    return _get_vix_price(
        ib=bot.ib,
        logger=bot.logger,
    )


# ---------------------------------------------------------------------------
# Chain / Deltas (on-demand)
# ---------------------------------------------------------------------------
def get_option_chain_adapter(bot, expiry: str) -> Tuple[Optional[str], List[float]]:
    trading_class, strikes = _get_option_chain(
        ib=bot.ib,
        expiry=expiry,
        underlying_price=bot.underlying_price,
        get_index_contract_callable=bot.get_SPX_index_contract,
        logger=bot.logger,
        debug_mode=bot.DEBUG_MODE,
    )

    if trading_class:
        bot.trading_class = trading_class

    return trading_class, strikes

def get_option_deltas_adapter(
    bot,
    *,
    expiry: str,
    strikes: List[float],
    put_call: str,
    trading_class: str,
) -> Dict[float, float]:
    return _get_option_deltas(
        ib=bot.ib,
        expiry=expiry,
        strikes=strikes,
        put_call=put_call,
        trading_class=trading_class,
        get_option_conid_callable=lambda e, s, r, tc=None: get_option_conid_adapter(bot, e, s, r, tc),
        wait_for_ticker_data_callable=bot.wait_for_ticker_data,
        logger=bot.logger,
    )