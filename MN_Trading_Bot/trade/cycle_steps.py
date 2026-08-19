# trade/cycle_steps.py
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from market.option_chain import get_best_expiry_by_dte
from market.ndx_steering import select_ndx_50bps_spread
from trade.metrics import TradeMetrics
from trade.pricing import price_2leg_credit, price_3leg_credit

def _set_short_mid_from_tickers(metrics: TradeMetrics, tickers) -> None:
    """Set metrics.short_leg_mid from the first ticker's bid/ask (short leg)."""
    if not tickers:
        metrics.short_leg_mid = None
        return

    t_short = tickers[0]
    if getattr(t_short, "bid", None) and getattr(t_short, "ask", None) and t_short.bid > 0 and t_short.ask > 0:
        metrics.short_leg_mid = (t_short.bid + t_short.ask) / 2.0
    else:
        metrics.short_leg_mid = None

def select_expiry(bot) -> str:
    """Long DTE => best expiry in window, else fixed calendar DTE."""
    if int(bot.LEG1_DTE) >= 30:
        target = int(bot.LEG1_DTE)
        return (
            get_best_expiry_by_dte(
                ib=bot.ib,
                target_dte=target,
                min_dte=target - 10,
                max_dte=target + 10,
                get_index_contract_callable=bot.get_SPX_index_contract,
                logger=bot.logger,
                debug_mode=bot.DEBUG_MODE,
            )
            or (datetime.now() + timedelta(days=target)).strftime("%Y%m%d")
        )
    return (datetime.now() + timedelta(days=int(bot.LEG1_DTE))).strftime("%Y%m%d")


def preload_market_data(bot, expiry: str) -> None:
    """Preload option chain + deltas into bot caches if underlying price available."""
    if bot.get_current_price() is None:
        return

    bot.preload_option_chain(expiry)

    if bot._cached_option_chain and bot._cached_chain_expiry == expiry:
        trading_class_pre, strikes_pre = bot._cached_option_chain
        strikes_for_delta_pre = bot._build_strikes_for_delta(strikes_pre)

        # --- PRE-EXECUTION: try delta preload up to 3 times ---
        max_attempts = int(getattr(bot, "DELTA_PRELOAD_ATTEMPTS", 3))
        sleep_s = float(getattr(bot, "DELTA_PRELOAD_RETRY_SLEEP", 1.0))

        for i in range(1, max_attempts + 1):
            bot.preload_deltas(expiry, trading_class_pre, strikes_for_delta_pre)

            if bot._cached_deltas:
                bot.logger.info(f"✅ Delta preload succeeded on attempt {i}/{max_attempts}")
                break

            bot.logger.warning(f"⚠️ Delta preload attempt {i}/{max_attempts} returned no data")
            try:
                bot.ib.sleep(sleep_s)
            except Exception:
                pass


def get_chain_for_expiry(bot, expiry: str) -> Tuple[Optional[str], List[float]]:
    """Use cached chain if fresh; otherwise refetch."""
    if bot._cached_chain_timestamp:
        age = (datetime.now() - bot._cached_chain_timestamp).total_seconds()
        if age > 300:
            bot.logger.debug("Preloaded option chain too old – refetching")
            bot._cached_option_chain = None
            bot._cached_chain_expiry = None
            bot._cached_chain_timestamp = None

    if bot._cached_option_chain and bot._cached_chain_expiry == expiry:
        bot.logger.debug("✅ Using preloaded option chain")
        return bot._cached_option_chain

    return bot.get_option_chain(expiry)


def init_delta_cache(bot, expiry: str, trading_class: str) -> Optional[Dict[float, float]]:
    """Return cached deltas if matching; cache is considered valid for this run.

    Operating mode: bot starts shortly before execution time.
    Therefore we prefer *stable* cached deltas for timing-critical entry.
    Strategy-specific re-fetching (e.g. NDX rescans) is handled in steering.
    """
    if not (
        bot._cached_deltas
        and bot._cached_deltas_expiry == expiry
        and bot._cached_deltas_trading_class == trading_class
        and bot._cached_deltas_put_call == bot.LEG1_PUT_CALL
    ):
        return None

    age = (datetime.now() - bot._cached_deltas_timestamp).total_seconds() if bot._cached_deltas_timestamp else 9999
    if age <= 300:
        bot._delta_window_center = bot._cached_deltas_center or bot.underlying_price
        bot.logger.debug(f"✅ Using preloaded deltas ({len(bot._cached_deltas)} strikes)")
        return bot._cached_deltas

    bot.logger.debug(f"Preloaded deltas stale (age={age:.0f}s) – ignoring cache")
    return None


def build_strikes_for_delta_window(bot, strikes: List[float]) -> List[float]:
    """Apply optional OTM window for NDX-style scans."""

    strike_lower_offset = getattr(bot, "STRIKE_LOWER_OFFSET", None)
    strike_upper_offset = getattr(bot, "STRIKE_UPPER_OFFSET", None)

    if strike_lower_offset is None or strike_upper_offset is None:
        return strikes

    strikes = [float(s) for s in strikes]
    underlying = float(bot.underlying_price)

    lower = underlying - float(strike_lower_offset)
    upper = underlying - float(strike_upper_offset)

    # Guard gegen kaputte Config
    if lower > upper:
        bot.logger.error(
            f"{bot.STRATEGY_NAME}: invalid strike window "
            f"(lower={lower}, upper={upper})"
        )
        return []

    filtered = [s for s in strikes if lower <= s <= upper]
    filtered = sorted(filtered, reverse=True)[: bot.MAX_STRIKE_SCAN]

    if not filtered:
        bot.logger.warning(
            f"{bot.STRATEGY_NAME}: no strikes in "
            f"{strike_upper_offset}-{strike_lower_offset} OTM window"
        )

    bot.logger.debug(
        f"{bot.STRATEGY_NAME}: delta window "
        f"{int(lower)}–{int(upper)} | "
        f"selected={len(filtered)} | "
        f"max_scan={bot.MAX_STRIKE_SCAN}"
    )

    return filtered


def maybe_invalidate_delta_cache(bot, delta_cache: Optional[Dict[float, float]]) -> Optional[Dict[float, float]]:
    """No-op invalidation for timing-critical entry.

    Delta re-fetch decisions belong to strategy modules (e.g. NDX steering),
    not the generic cycle steps.
    """
    return delta_cache


def fetch_deltas_if_needed(
    bot,
    expiry: str,
    trading_class: str,
    strikes_for_delta: List[float],
    delta_cache: Optional[Dict[float, float]],
) -> Tuple[Optional[Dict[float, float]], Optional[Dict[float, float]]]:
    """Return (deltas, updated_cache).

    Timing rule (entry @ execution time):
    - If cached deltas exist: use them immediately (non-blocking).
    - If no cache: do NOT fetch synchronously here (would delay order placement).

    Strategy-specific delta refresh (e.g. NDX rescan>=3) is handled inside the
    steering logic (market/ndx_steering.py).
    """

    if delta_cache is not None:
        bot.logger.debug(f"Using cached deltas ({len(delta_cache)} strikes)")
        return delta_cache, delta_cache

    # No cache available at execution-time stage.
    # For NDX-50BPS: allow steering to refresh deltas starting at rescan>=3.
    if getattr(bot, "STRATEGY_NAME", "") == "NDX-50BPS":
        bot.logger.warning(
            "No delta cache available for NDX-50BPS (continuing with empty cache; steering may refresh on later rescans)"
        )
        empty: Dict[float, float] = {}
        return empty, empty

    # --- EXECUTION: exactly ONE synchronous attempt per trading cycle ---
    if not hasattr(bot, "_execution_delta_fetch_attempted"):
        bot._execution_delta_fetch_attempted = False

    if not bot._execution_delta_fetch_attempted:
        bot._execution_delta_fetch_attempted = True

        bot.logger.info(
            "No delta cache available at execution – attempting ONE synchronous delta fetch"
        )
        bot.preload_deltas(expiry, trading_class, strikes_for_delta)

        # after preload, try to use freshly cached deltas
        refreshed = init_delta_cache(bot, expiry, trading_class)
        if refreshed is not None:
            bot.logger.debug(f"✅ Using freshly fetched deltas ({len(refreshed)} strikes)")
            return refreshed, refreshed

        bot.logger.warning(
            "Delta fetch failed at execution – skipping further attempts to preserve timing"
        )
        return None, None

    bot.logger.warning(
        "No delta cache available (already attempted sync fetch once – skipping to preserve timing)"
    )
    return None, None

def select_legs(bot, expiry: str, strikes: List[float], deltas: Dict[float, float], rescan: int, trading_class: str):
    """Return (leg1, leg2, leg3_or_None) + optional NDX metrics stored on bot."""

    metrics = TradeMetrics()

    # Special case: NDX-50BPS uses steering module
    if bot.STRATEGY_NAME == "NDX-50BPS":
        if bot.LEG1_TARGET_TYPE.lower() != "delta":
            bot.logger.error("NDX-50BPS requires LEG1_TARGET_TYPE = 'Delta'")
            return None

        target_delta = float(bot.LEG1_TARGET) / 100.0

        try:
            delta_max_abs_dec = float(bot.DELTA_MAX_ABS) / 100.0
            delta_rescan_expansion_dec = float(bot.DELTA_RESCAN_EXPANSION) / 100.0
            delta_target_offset_dec = float(bot.DELTA_TARGET_OFFSET) / 100.0
        except Exception:
            bot.logger.error("NDX-50BPS: Missing DELTA_* steering params in template")
            return None

        result = select_ndx_50bps_spread(
            strikes=strikes,
            deltas=deltas,
            underlying_price=bot.underlying_price,
            expiry=expiry,
            trading_class=trading_class,
            rescan=rescan,

            strike_upper_offset=bot.STRIKE_UPPER_OFFSET,
            strike_lower_offset=bot.STRIKE_LOWER_OFFSET,
            strike_step=bot.STRIKE_STEP,
            max_strike_scan=bot.MAX_STRIKE_SCAN,

            target_delta=target_delta,
            delta_target_offset=delta_target_offset_dec,
            delta_rescan_expansion=delta_rescan_expansion_dec,
            delta_max_abs=delta_max_abs_dec,

            short_mid_min=bot.SHORT_LEG_MID_MIN,
            short_mid_max=bot.SHORT_LEG_MID_MAX,
            short_leg_mid_expansion=bot.SHORT_LEG_MID_EXPANSION,

            credit_min=-bot.MAX_SWEEP_PRICE,
            credit_max=-bot.MIN_SWEEP_PRICE,

            get_option_conid=bot._get_option_conid,
            ib=bot.ib,
            wait_for_ticker_data=bot.wait_for_ticker_data,
            logger=bot.logger,

            leg1_put_call=bot.LEG1_PUT_CALL,
            leg2_put_call=bot.LEG2_PUT_CALL,
            leg2_target=bot.LEG2_TARGET,
            leg2_target_type=bot.LEG2_TARGET_TYPE,
        )

        if not result:
            bot.logger.warning("No valid spread found")
            return None

        metrics.short_leg_mid = result.get("short_mid")
        metrics.short_delta = result.get("short_delta")

        return result["short_strike"], result["long_strike"], None, metrics

    # Default: use TradeType
    selection = bot.trade_type.select_strikes(
        expiry=expiry,
        strikes=strikes,
        deltas=deltas,
        underlying_price=bot.underlying_price,
    )

    if not selection:
        bot.logger.warning("Strategy did not return strikes")
        return None

    # --------------------------------------------------------
    # Capture short-leg delta for non-NDX strategies (e.g. SPX BPS)
    # --------------------------------------------------------
    short_strike = None
    if isinstance(selection, tuple) and len(selection) >= 1:
        short_strike = selection[0]

    # robust lookup for strike key (handles float/int and minor rounding)
    key = float(short_strike) if short_strike is not None else None
    val = None
    if key is not None:
        if key in deltas:
            val = deltas[key]
        else:
            k2 = float(int(round(key)))
            if k2 in deltas:
                val = deltas[k2]

    metrics.short_delta = abs(val) if isinstance(val, (int, float)) else None


    if isinstance(selection, tuple):
        if len(selection) == 2:
            leg1, leg2 = selection
            return leg1, leg2, None, metrics
        if len(selection) == 3:
            leg1, leg2, leg3 = selection
            return leg1, leg2, leg3, metrics

    bot.logger.error(f"Invalid strike selection: {selection}")
    return None


def price_and_set_last(bot, expiry: str, trading_class: str, leg1: float, leg2: float, leg3: Optional[float], metrics: TradeMetrics) -> bool:
    """Prices legs and sets bot._last_combo_premium/_natural. Returns True if ok."""
    if leg3 is not None:
        c1 = bot._get_option_conid(expiry, leg1, bot.LEG1_PUT_CALL, trading_class)
        c2 = bot._get_option_conid(expiry, leg2, bot.LEG2_PUT_CALL, trading_class)
        c3 = bot._get_option_conid(expiry, leg3, bot.LEG3_PUT_CALL, trading_class)

        if not all([c1, c2, c3]):
            bot.logger.warning("PBW: failed to qualify one or more option contracts")
            return False

        tickers = bot.ib.reqTickers(c1, c2, c3)

        if not bot.wait_for_ticker_data(tickers, timeout=1.0):
            bot.logger.warning("PBW: ticker timeout")
            return False

        # short leg = leg1 (PBW)
        _set_short_mid_from_tickers(metrics, tickers)

        credit_mid, credit_natural = price_3leg_credit(
            symbol=bot.SYMBOL,
            expiry=expiry,
            leg1=leg1,
            leg2=leg2,
            leg3=leg3,
            trading_class=trading_class,
            leg1_put_call=bot.LEG1_PUT_CALL,
            leg2_put_call=bot.LEG2_PUT_CALL,
            leg3_put_call=bot.LEG3_PUT_CALL,
            leg1_action=bot.LEG1_ACTION,
            leg2_action=bot.LEG2_ACTION,
            leg3_action=bot.LEG3_ACTION,
            leg1_qty=bot.LEG1_QTY,
            leg2_qty=bot.LEG2_QTY,
            leg3_qty=bot.LEG3_QTY,
            logger=bot.logger,
            timeout=1.0,
            tickers=tickers,
        )

    else:
        # --- also capture short-leg mid for reporting ---
        c1 = bot._get_option_conid(expiry, leg1, bot.LEG1_PUT_CALL, trading_class)
        c2 = bot._get_option_conid(expiry, leg2, bot.LEG2_PUT_CALL, trading_class)

        if not c1 or not c2:
            return False

        tickers = bot.ib.reqTickers(c1, c2)
        if not bot.wait_for_ticker_data(tickers, timeout=1.0):
            return False

        # short leg = leg1
        _set_short_mid_from_tickers(metrics, tickers)

        credit_mid, credit_natural = price_2leg_credit(
            symbol=bot.SYMBOL,
            expiry=expiry,
            leg1=leg1,
            leg2=leg2,
            trading_class=trading_class,
            leg1_put_call=bot.LEG1_PUT_CALL,
            leg2_put_call=bot.LEG2_PUT_CALL,
            leg1_action=bot.LEG1_ACTION,
            leg2_action=bot.LEG2_ACTION,
            leg1_qty=bot.LEG1_QTY,
            leg2_qty=bot.LEG2_QTY,
            logger=bot.logger,
            timeout=1.0,
            tickers=tickers,
        )

    if credit_mid is None or credit_natural is None:
        return False

    if credit_mid >= 0:
        bot.logger.warning(
            f"Credit {credit_mid:.2f} is not negative – skipping"
        )
        return False

    if credit_mid < bot.MIN_SWEEP_PRICE or credit_mid > bot.MAX_SWEEP_PRICE:
        bot.logger.warning(
            f"credit {credit_mid:.2f} out of range "
            f"{bot.MIN_SWEEP_PRICE:.2f}..{bot.MAX_SWEEP_PRICE:.2f}"
        )
        return False

    bot.logger.debug(f"pricing: natural={credit_natural:.2f}, mid={credit_mid:.2f}")
    metrics.combo_mid = credit_mid
    metrics.combo_natural = credit_natural
    return True

def build_combo(bot, expiry: str, trading_class: str, leg1: float, leg2: float, leg3: Optional[float], metrics: TradeMetrics):
    """Creates combo contract and attaches metrics."""
    if leg3 is not None:
        from trade.combo_factory import create_combo_contract_3leg

        combo = create_combo_contract_3leg(
            symbol=bot.SYMBOL,
            expiry=expiry,
            leg1=leg1,
            leg2=leg2,
            leg3=leg3,
            trading_class=trading_class,
            leg1_put_call=bot.LEG1_PUT_CALL,
            leg2_put_call=bot.LEG2_PUT_CALL,
            leg3_put_call=bot.LEG3_PUT_CALL,
            leg1_action=bot.LEG1_ACTION,
            leg2_action=bot.LEG2_ACTION,
            leg3_action=bot.LEG3_ACTION,
            leg1_qty=bot.LEG1_QTY,
            leg2_qty=bot.LEG2_QTY,
            leg3_qty=bot.LEG3_QTY,
            min_sweep_price=bot.MIN_SWEEP_PRICE,
            max_sweep_price=bot.MAX_SWEEP_PRICE,
            get_option_conid_callable=bot._get_option_conid,
            logger=bot.logger,
        )

        lower_wing = abs(leg1 - leg2)
        upper_wing = abs(leg3 - leg1)
        entry_credit = abs(metrics.combo_mid or 0.0)

        combo._pbw_lower_wing_width = lower_wing
        combo._pbw_upper_wing_width = upper_wing
        combo._pbw_is_broken = upper_wing != lower_wing
        combo._pbw_entry_credit = entry_credit
        combo._pbw_max_profit_points = entry_credit
        combo._pbw_max_loss_points = max(lower_wing, upper_wing) - entry_credit

        combo.metrics = metrics

        return combo

    combo = bot.create_combo_contract(expiry, leg1, leg2, trading_class)
    combo.metrics = metrics
    return combo


def log_and_execute(bot, combo, expiry_label: str, leg1: float, leg2: float, leg3: Optional[float], metrics: TradeMetrics):
    qty = bot.get_effective_quantity()
    label = getattr(bot.trade_type, "display_name", None) or bot.TRADE_TYPE

    if leg3 is not None:
        bot.logger.debug("=" * 80)
        bot.logger.info(
            f"Executing BUY {qty} {bot.SYMBOL} {expiry_label} "
            f"{int(leg2)}/{int(leg1)}/{int(leg3)} {label}"
        )
        bot.logger.debug("=" * 80)
    else:
        bot.logger.debug("=" * 80)
        bot.logger.info(
            f"Executing BUY {qty} {bot.SYMBOL} {expiry_label} "
            f"{int(leg1)}/{int(leg2)} {label}"
        )
        bot.logger.debug("=" * 80)

    return bot.execute_credit_sweep(combo, found_credit=metrics.combo_mid, natural_credit=metrics.combo_natural)