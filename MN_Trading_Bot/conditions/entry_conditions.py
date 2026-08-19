# conditions/entry_conditions.py

def check_entry_conditions(
    *,
    check_conditions: bool,
    symbol: str,
    entry_conditions: dict,
    get_rsi_callable,
    get_sma_callable,
    get_vix_callable,
    underlying_price: float,
    open_price: float,
    logger,
) -> bool:
    """
    Check entry conditions with ORDER-based priority.
    Supported conditions:
    - ABOVE_SMA
    - INTRADAY_MOVE
    - RSI
    - VIX
    - WEEKDAY_FILTER
    """

    if not check_conditions:
        logger.debug("Entry condition checks disabled")
        return True

    if not entry_conditions:
        logger.info("No entry conditions configured – entry allowed")
        return True

    logger.debug("Checking entry conditions...")

    ordered_conditions = sorted(
        entry_conditions.items(),
        key=lambda kv: kv[1].get("ORDER", 100)
    )

    active_names = [name for name, _ in ordered_conditions]
    logger.info(
        f"Active entry conditions (in order): {', '.join(active_names)}"
    )

    for name, cfg in ordered_conditions:

        # ── ABOVE SMA ───────────────────────────────────────────
        if name == "ABOVE_SMA":
            period = cfg["PERIOD"]
            sma = get_sma_callable(period=period, bar_size="1 day")

            if sma is None:
                logger.warning("SMA unavailable – entry blocked")
                return False

            ok = underlying_price >= sma

            logger.info(
                f"Check Trade Condition: {symbol}: "
                f"{underlying_price:.2f} >= SMA({period}) {sma:.2f}  "
                f"Result: {ok}"
            )
            logger.info(
                f"{symbol} Current: {underlying_price:.2f}  Open: {open_price:.2f}"
            )

            if not ok:
                logger.warning("SMA condition failed – entry blocked")
                return False

        # ── INTRADAY MOVE ───────────────────────────────────────
        elif name == "INTRADAY_MOVE":
            min_move_pct = cfg["MIN_PCT"]

            if open_price <= 0 or underlying_price <= 0:
                logger.warning("Invalid price data for intraday move check")
                return False

            move_pct = ((underlying_price - open_price) / open_price) * 100.0
            ok = move_pct >= min_move_pct

            logger.info(
                f"Check Trade Condition (Intraday): "
                f"{move_pct:.2f}% >= {min_move_pct:.2f}%  "
                f"Result: {ok}"
            )

            if not ok:
                logger.warning(
                    f"Intraday move {move_pct:.2f}% below "
                    f"minimum {min_move_pct:.2f}% – entry blocked"
                )
                return False

        # ── RSI ────────────────────────────────────────────────
        elif name == "RSI":
            period = cfg["PERIOD"]
            rsi_min = cfg["MIN"]
            rsi_max = cfg["MAX"]

            rsi = get_rsi_callable(period=period, bar_size="1 day")

            if rsi is None:
                logger.warning("RSI unavailable – entry blocked")
                return False

            ok = rsi_min <= rsi <= rsi_max

            logger.info(
                f"Check Trade Condition (RSI): "
                f"{rsi:.2f} in [{rsi_min}, {rsi_max}]  "
                f"Result: {ok}"
            )

            if not ok:
                logger.warning(
                    f"RSI {rsi:.2f} outside "
                    f"[{rsi_min}, {rsi_max}] – entry blocked"
                )
                return False

        # ── VIX ────────────────────────────────────────
        elif name == "VIX":
            vix_value = get_vix_callable()

            if vix_value is None:
                logger.warning("VIX unavailable – entry blocked")
                return False

            min_vix = cfg.get("MIN")
            max_vix = cfg.get("MAX")

            ok = True

            if min_vix is not None and vix_value < min_vix:
                ok = False

            if max_vix is not None and vix_value > max_vix:
                ok = False

            logger.info(
                f"Check Trade Condition (VIX): "
                f"{vix_value:.2f} in [{min_vix}, {max_vix}]  "
                f"Result: {ok}"
            )

            if not ok:
                logger.warning(
                    f"VIX {vix_value:.2f} outside "
                    f"[{min_vix}, {max_vix}] – entry blocked"
                )
                return False

        # ── WEEKDAY FILTER (Tranchen-Rhythmus, z.B. Mo/Do) ──────
        elif name == "WEEKDAY_FILTER":
            from datetime import datetime as _dt

            allowed_days = [d.upper() for d in cfg.get("DAYS", [])]
            today_name = _dt.now().strftime("%A").upper()

            ok = today_name in allowed_days

            logger.info(
                f"Check Trade Condition (Weekday): "
                f"{today_name} in {allowed_days}  Result: {ok}"
            )

            if not ok:
                logger.warning(
                    f"Weekday {today_name} not in allowed {allowed_days} – entry blocked"
                )
                return False

        # ── Unknown condition ──────────────────────────────────
        else:
            logger.warning(f"Unknown entry condition '{name}' – skipping")

    logger.info("✓ Entry conditions passed")
    return True