from datetime import datetime
from conditions.entry_conditions import check_entry_conditions

from trade.cycle_steps import (
    select_expiry,
    preload_market_data,
    get_chain_for_expiry,
    init_delta_cache,
    build_strikes_for_delta_window,
    maybe_invalidate_delta_cache,
    fetch_deltas_if_needed,
    select_legs,
    price_and_set_last,
    build_combo,
    log_and_execute,
)

def run_trading_cycle(bot):
    logger = bot.logger

    logger.debug("=" * 80)
    logger.info("🎯 Starting trading cycle")
    logger.debug("=" * 80)

    if not bot.should_trade_today():
        logger.info("✅ Already traded today – stopping bot")
        bot.running = False
        return

    bot.ensure_live_data_if_market_open()
    expiry = select_expiry(bot)

    preload_market_data(bot, expiry)

    if not bot.wait_for_EXECUTION_TIME():
        logger.info("Trading skipped due to late start")
        return

    if not bot.is_market_open():
        logger.error("Market closed - aborting")
        return

    if bot.get_open_price() is None:
        logger.error("Failed to get open price")
        return

    entry_price = bot.get_current_price()

    if entry_price is None:
        logger.error("Failed to refresh current price (entry)")
        return

    bot.underlying_price = entry_price

    entry_conditions = bot.trade_cfg.get("ENTRY_CONDITIONS", {})

    vix_value = None

    if "VIX" in entry_conditions:
        vix_value = bot.get_vix()

        if vix_value is None:
            logger.warning("VIX unavailable – skipping trade")
            return

    if not check_entry_conditions(
        symbol=bot.SYMBOL,
        check_conditions=bot.CHECK_CONDITIONS,
        entry_conditions=entry_conditions,
        get_rsi_callable=bot.get_rsi,
        get_sma_callable=bot.get_sma,
        get_vix_callable=lambda: vix_value,
        underlying_price=bot.underlying_price,
        open_price=bot.open_price,
        logger=logger,
    ):
        logger.warning(
            f"Entry Condition Failed. Cancelling Trade: {bot.STRATEGY_NAME}"
        )
        return

    expiry_label = datetime.strptime(expiry, "%Y%m%d").strftime("%b%d'%y")

    trading_class, strikes = get_chain_for_expiry(bot, expiry)
    if not trading_class or not strikes:
        logger.error("Failed to get option chain")
        return

    max_rescans = int(bot.trade_cfg.get("MAX_RESCAN_ATTEMPTS", 4))
    rescan_wait = 5

    delta_cache = init_delta_cache(bot, expiry, trading_class)

    for rescan in range(max_rescans):

        if rescan > 0:
            logger.info(
                f"♻️  RESCAN {rescan}/{max_rescans - 1} - waiting {rescan_wait}s"
            )

            if not bot.interruptible_sleep(rescan_wait):
                return

            refreshed_price = bot.get_current_price()
            if refreshed_price is None:
                logger.error("Failed to refresh price")
                return

            bot.underlying_price = refreshed_price
            logger.debug(f"{bot.SYMBOL} updated price during rescan: {refreshed_price:.2f}")

        strikes_for_delta = build_strikes_for_delta_window(bot, strikes)
        delta_cache = maybe_invalidate_delta_cache(bot, delta_cache)

        deltas, delta_cache = fetch_deltas_if_needed(
            bot, expiry, trading_class, strikes_for_delta, delta_cache
        )

        if deltas is None:
            continue

        legs = select_legs(
            bot,
            expiry,
            strikes_for_delta if bot.STRATEGY_NAME == "NDX-50BPS" else strikes,
            deltas,
            rescan,
            trading_class,
        )

        if not legs:
            continue

        leg1, leg2, leg3, leg4, metrics = legs

        if not price_and_set_last(
            bot, expiry, trading_class, leg1, leg2, leg3, leg4, metrics
        ):
            continue

        combo = build_combo(
            bot, expiry, trading_class, leg1, leg2, leg3, leg4, metrics
        )

        trade = log_and_execute(
            bot,
            combo,
            expiry_label,
            leg1, leg2, leg3, leg4,
            metrics,
        )

        if trade:
            bot.last_trade_date = datetime.now().date()
            logger.info("✅ Trade completed – stopping bot")
            bot.running = False
            return

        logger.warning(f"Sweep failed ({rescan + 1}/{max_rescans})")

    logger.warning("=" * 80)
    logger.warning("❌ All scan attempts exhausted - no trade today")
    logger.warning("=" * 80)