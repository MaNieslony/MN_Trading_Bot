# trade/execution.py
from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal, ROUND_FLOOR, ROUND_CEILING
from typing import Optional

from ib_insync import LimitOrder

def _quantize_up(price: float, step: float) -> float:
    """
    Quantize UP to tick size (toward +inf).
    For negative credits this becomes "less negative" or equal.
    Required for sweep progression; avoids getting stuck due to float+floor on negatives.
    Uses Decimal to avoid float artifacts.
    """
    p = Decimal(str(price))
    t = Decimal(str(step))
    q = (p / t).to_integral_value(rounding=ROUND_CEILING) * t
    return float(q)

def _round_to_0_05(price: float) -> float:
    # Standalone: round(target_price * 20) / 20
    return round(price * 20) / 20

def place_profit_target_order(
    *,
    ib,
    logger,
    combo,
    entry_credit: float,
    quantity: int,
    profit_target_pct: float,   # e.g. 50.0
    profit_target_eth: bool,    # outsideRth
    order_ref: str,
) -> dict | None:
    """
    Standalone-kompatibles Profit Target (GTC) für negative Credit-Combos.

    Für negative entry_credit (z.B. -3.60):
      target = entry_credit * (1 - pct/100)
      50% => -3.60 * 0.5 = -1.80
    """
    try:
        logger.debug("=" * 80)
        logger.info("🎯 PLACING PROFIT TARGET ORDER")
        logger.debug("=" * 80)

        logger.debug(f"Entry credit: ${entry_credit:.2f}")

        profit_multiplier = 1.0 - (profit_target_pct / 100.0)
        target_price = entry_credit * profit_multiplier

        # round to nearest 0.05 exactly like standalone
        target_price = _round_to_0_05(target_price)

        # Expected profit in $:
        # entry and target are negative; profit is reduction in absolute debit to close
        # abs(entry) - abs(target) per contract * 100 * qty
        expected_profit = (abs(entry_credit) - abs(target_price)) * quantity * 100.0

        logger.debug(f"Target profit: {profit_target_pct:.1f}%")
        logger.debug(f"Target exit price: ${target_price:.2f}")
        logger.debug(f"Expected profit: ${expected_profit:.2f}")

        order = LimitOrder(
            action="SELL",
            totalQuantity=quantity,
            lmtPrice=target_price,
            tif="GTC",
            outsideRth=profit_target_eth,
            orderRef=f"{order_ref}-PT",
        )

        trade = ib.placeOrder(combo, order)
        order_id = trade.order.orderId
        logger.debug("=" * 80)
        logger.info(f"✅ PROFIT TARGET ORDER placed (GTC)")
        logger.debug("=" * 80)

        return {
            "order_id": order_id,
            "target_pct": profit_target_pct,
            "exit_price": target_price,
            "expected_profit": expected_profit,
            "outsideRth": profit_target_eth,
        }

    except Exception as e:
        logger.error(f"Failed to place profit target order: {e}", exc_info=True)
        return None

def execute_credit_sweep(
    *,
    ib,
    logger,
    combo,
    found_credit: Optional[float],
    natural_credit: Optional[float],
    # sizing / logging hooks
    calculate_quantity_callable,
    log_trade_callable,
    interruptible_sleep_callable,
    # config values
    min_qty: int,
    max_qty: int,
    max_sweep_price: float,
    sweep_step: float,
    sweep_wait_seconds: int,
    max_sweep_attempts: int,
    expiration_minutes: int,
    order_ref: str,
    profit_target_enabled: bool,
    profit_target_pct: float,
    profit_target_eth: bool,
    start_sweep_quantile: float = 0.25,
):
    """
    IMPORTANT:
    - Start price is quantized UP to tick (market-friendly for credits).
    - Sweep progression quantizes UP to tick (so we always progress for negative prices).

    Start-Sweep-Position:
    - Start-Preis wird innerhalb der Geldkurs-/Briefkurs-Spanne (theoretischer
      Bestpreis <-> natural credit) per start_sweep_quantile gewählt:
        0.0 -> Start am Geldkurs (Bestpreis, meiste Credit)
        0.5 -> Start am Mid-Preis (altes Verhalten)
        1.0 -> Start am Briefkurs (natural credit, wenigste Credit)
      Default 0.25 = oberes Viertel der Spanne (näher am Geldkurs).
      Geldkurs wird rechnerisch aus mid/natural abgeleitet:
        best = 2*mid - natural
      Keine zusätzlichen IB-Anfragen nötig.
    """

    # --------------------------------------------------------------------
    # Quantity (size off natural credit worst-case fill; fallback to min_qty)
    # --------------------------------------------------------------------
    if found_credit and found_credit < 0 and natural_credit and natural_credit < 0:
        quantity = calculate_quantity_callable(
            mid_credit=found_credit,
            natural_credit=natural_credit
        )
    else:
        quantity = min_qty

    quantity = max(min_qty, min(int(quantity), max_qty))

    # --------------------------------------------------------------------
    # Validate credit
    # --------------------------------------------------------------------
    if not found_credit or found_credit >= 0:
        logger.error("Invalid credit price - cannot execute sweep")
        return None

    # --------------------------------------------------------------------
    # Start price: oberes Viertel der Geld-/Briefkurs-Spanne (statt reinem Mid).
    # Geldkurs (best-case) = 2*mid - natural (rechnerisch, ohne zusätzliche IB-Calls).
    # Quantize UP to tick. Clamp to max_sweep_price (ceiling).
    # --------------------------------------------------------------------
    if natural_credit and natural_credit < 0 and found_credit <= natural_credit:
        best_credit = (2.0 * found_credit) - natural_credit
        q = min(max(float(start_sweep_quantile), 0.0), 1.0)
        raw_start = ((1.0 - q) * best_credit) + (q * natural_credit)

        logger.debug(f"Geldkurs (best-case, rechnerisch): ${best_credit:.2f}")
        logger.debug(f"Briefkurs (natural credit): ${natural_credit:.2f}")
        logger.debug(f"Start-Sweep-Quantile: {q:.2f} (0=Geldkurs, 1=Briefkurs)")
    else:
        raw_start = found_credit
        logger.debug("Kein gültiger natural_credit für Quantile-Start – starte am Mid-Preis")

    start_credit = _quantize_up(raw_start, sweep_step)
    start_credit = min(start_credit, max_sweep_price)

    logger.debug(f"Quantity: {quantity} contracts")
    logger.debug(f"Reference credit (mid): ${found_credit:.2f}")
    logger.debug(f"Start sweep @: ${start_credit:.2f}")
    logger.debug(f"Max sweep price: ${max_sweep_price:.2f}")
    logger.debug(f"Step: +${sweep_step:.2f} per attempt")
    logger.debug(f"Sweep wait seconds: {sweep_wait_seconds}s")
    logger.debug(f"Max sweep attempts: {max_sweep_attempts}")
    logger.debug(f"Expiration window: {expiration_minutes} minutes")

    order = None
    trade = None
    current_credit = start_credit
    attempt = 0

    start_time = datetime.now()
    expiration_time = start_time + timedelta(minutes=expiration_minutes)

    # --------------------------------------------------------------------
    # MAIN SWEEP LOOP
    # --------------------------------------------------------------------
    while attempt < max_sweep_attempts:
        # stop if we've crossed the max price ceiling (less negative than allowed)
        if current_credit > max_sweep_price:
            break

        # expiration window check
        if datetime.now() > expiration_time:
            logger.warning(f"Expiration window ({expiration_minutes}m) exceeded")
            if trade:
                try:
                    ib.cancelOrder(trade.order)
                    logger.info("✓ Order cancelled due to expiration window")
                except Exception as e:
                    logger.debug(f"Order already cancelled: {e}")
            return None

        attempt += 1

        # ----------------------------------------------------------------
        # PLACE NEW ORDER (first attempt)
        # ----------------------------------------------------------------
        if order is None:
            logger.info(f"[{attempt}/{max_sweep_attempts}] Placing order @ ${current_credit:.2f}")

            order = LimitOrder(
                action="BUY",
                totalQuantity=quantity,
                lmtPrice=current_credit,
                orderRef=order_ref,
                tif="DAY",
            )

            try:
                trade = ib.placeOrder(combo, order)
                logger.debug(f"  Order ID: {trade.order.orderId}")

            except Exception as e:
                logger.error(f"Failed to place initial order: {e}")
                return None

        else:
            # ------------------------------------------------------------
            # CHECK FILL STATUS BEFORE MODIFYING
            # ------------------------------------------------------------
            filled = float(getattr(trade.orderStatus, "filled", 0) or 0)
            remaining = float(getattr(trade.orderStatus, "remaining", 0) or 0)
            status = getattr(trade.orderStatus, "status", "") or ""

            if status == "Filled" or filled >= trade.order.totalQuantity or remaining == 0:
                pass
            else:
                logger.info(f"[{attempt}/{max_sweep_attempts}] Modifying to ${current_credit:.2f}")

                # Cancel & replace (preferred for BAG)
                try:
                    ib.cancelOrder(trade.order)
                    logger.debug("Cancelled old order for price update")
                    ib.sleep(1.5)
                except Exception as cancel_e:
                    logger.debug(f"Cancel exception (may be normal): {cancel_e}")

                # ---- FILL CHECK AFTER CANCEL ----
                already_filled = int(float(getattr(trade.orderStatus, "filled", 0) or 0))
                status2 = getattr(trade.orderStatus, "status", "") or ""
                remaining2 = float(getattr(trade.orderStatus, "remaining", 0) or 0)

                is_fully_filled = (status2 == "Filled") or (already_filled >= quantity) or (remaining2 == 0)
                is_partially_filled = already_filled > 0 and not is_fully_filled

                if is_fully_filled:
                    logger.debug("")
                    logger.debug("=" * 80)
                    logger.debug("✅ ORDER FILLED DURING CANCEL/REPLACE ✅")
                    logger.debug("=" * 80)
                    fill_price = trade.orderStatus.avgFillPrice
                    logger.info(f"Fill credit: ${fill_price:.2f}, Quantity: {already_filled}")
                    logger.debug(f"vs Reference credit: ${found_credit:.2f}")
                    discount_pct = ((found_credit - fill_price) / found_credit) * 100
                    label = "Discount" if discount_pct >= 0 else "Premium"
                    direction = "below" if discount_pct >= 0 else "above"
                    logger.debug(f"{label}: {abs(discount_pct):.1f}% {direction} reference")
                    time_elapsed = (datetime.now() - start_time).total_seconds() / 60
                    logger.debug(f"Time elapsed since entry: {time_elapsed:.1f}m")

                    profit_target = None

                    if profit_target_enabled:
                        profit_target = place_profit_target_order(
                            ib=ib,
                            logger=logger,
                            combo=combo,
                            entry_credit=fill_price,
                            quantity=int(quantity),
                            profit_target_pct=profit_target_pct,
                            profit_target_eth=profit_target_eth,
                            order_ref=order_ref,
                        )

                    log_trade_callable(trade, fill_price, quantity, profit_target=profit_target)
                    return trade

                if is_partially_filled:
                    logger.warning(
                        f"Partial fill detected on cancelled order: "
                        f"{already_filled}/{quantity} contracts @ "
                        f"${trade.orderStatus.avgFillPrice:.2f} — "
                        f"treating as complete to avoid duplicate fills"
                    )
                    fill_price = trade.orderStatus.avgFillPrice
                    log_trade_callable(trade, fill_price, already_filled)
                    return trade

                # Nothing filled — replace
                try:
                    order = LimitOrder(
                        action="BUY",
                        totalQuantity=quantity,
                        lmtPrice=current_credit,
                        orderRef=order_ref,
                        tif="DAY",
                    )
                    trade = ib.placeOrder(combo, order)
                    logger.debug(f"Replacement order placed - new Order ID: {trade.order.orderId}")

                except Exception as e2:
                    logger.error(f"Failed to place replacement order: {e2}")
                    return None

        # ----------------------------------------------------------------
        # Wait for fill
        # ----------------------------------------------------------------
        if not interruptible_sleep_callable(sweep_wait_seconds):
            if trade:
                try:
                    ib.cancelOrder(trade.order)
                    logger.info("✓ Order cancelled by stop request")
                except Exception as e:
                    logger.debug(f"Order already cancelled: {e}")
            return None

        # ----------------------------------------------------------------
        # Check if filled
        # ----------------------------------------------------------------
        if trade and getattr(trade.orderStatus, "status", "") == "Filled":
            fill_price = trade.orderStatus.avgFillPrice

            logger.debug("=" * 80)
            logger.info("✅ ORDER FILLED ✅")
            logger.debug("=" * 80)
            logger.info(f"Fill credit: ${fill_price:.2f}, Quantity: {trade.orderStatus.filled}")
            logger.debug(f"vs Reference credit: ${found_credit:.2f}")

            discount_pct = ((found_credit - fill_price) / found_credit) * 100
            label = "Discount" if discount_pct >= 0 else "Premium"
            direction = "below" if discount_pct >= 0 else "above"
            logger.debug(f"{label}: {abs(discount_pct):.1f}% {direction} reference")

            time_elapsed = (datetime.now() - start_time).total_seconds() / 60
            logger.debug(f"Time elapsed since entry: {time_elapsed:.1f}m")

            profit_target = None

            if profit_target_enabled:
                profit_target = place_profit_target_order(
                    ib=ib,
                    logger=logger,
                    combo=combo,
                    entry_credit=fill_price,
                    quantity=int(quantity),
                    profit_target_pct=profit_target_pct,
                    profit_target_eth=profit_target_eth,
                    order_ref=order_ref,
                )

            log_trade_callable(
                trade,
                fill_price,
                quantity,
                profit_target=profit_target,
            )

            return trade

        # ----------------------------------------------------------------
        # MAX ATTEMPTS reached → cancel and return
        # ----------------------------------------------------------------
        if attempt >= max_sweep_attempts:
            status = getattr(trade.orderStatus, "status", "") if trade else ""
            filled = float(getattr(trade.orderStatus, "filled", 0) or 0) if trade else 0
            remaining = float(getattr(trade.orderStatus, "remaining", 0) or 0) if trade else 0
            total_qty = float(getattr(trade.order, "totalQuantity", 0) or 0) if trade else 0

            if not (status == "Filled" or filled >= total_qty or remaining == 0):
                logger.warning("")
                logger.warning("=" * 80)
                logger.warning(f"❌ MAX SWEEP ATTEMPTS REACHED ({max_sweep_attempts})")
                logger.warning("=" * 80)
                logger.warning(f"Order still not filled at ${current_credit:.2f}")
                logger.warning("Cancelling order and returning to rescan...")
                logger.warning("=" * 80)

                if trade:
                    try:
                        ib.cancelOrder(trade.order)
                        logger.info("✓ Order cancelled - sweep completed")
                    except Exception as e:
                        logger.debug(f"Error cancelling order: {e}")

                return None

        # ----------------------------------------------------------------
        # Not filled → step towards market (less negative)
        # Use Decimal arithmetic throughout to avoid float artifacts
        # (e.g. -0.36 + 0.02 = -0.33999... in float → snaps 2 ticks).
        # ----------------------------------------------------------------
        next_credit = float(
            Decimal(str(current_credit)) + Decimal(str(sweep_step))
        )

        # Safety: if somehow still no progress, force one tick via quantize
        if next_credit <= current_credit:
            next_credit = _quantize_up(current_credit + sweep_step, sweep_step)

        current_credit = next_credit

    # ------------------------------------------------------------------------
    # SWEEP EXHAUSTED - No fill achieved
    # ------------------------------------------------------------------------
    if trade:
        try:
            ib.cancelOrder(trade.order)
            logger.info("✓ Order cancelled - sweep exhausted")
        except Exception as e:
            logger.debug(f"Order already cancelled: {e}")

    reason = (
        f"Price ceiling reached (${max_sweep_price:.2f})"
        if attempt < max_sweep_attempts
        else f"Max attempts reached ({max_sweep_attempts})"
    )

    logger.warning("")
    logger.warning("=" * 80)
    logger.warning(f"❌ ORDER NOT FILLED – {reason}")
    logger.warning(f"Attempts used: {attempt}/{max_sweep_attempts}")
    logger.warning(f"Price range: ${start_credit:.2f} → ${current_credit:.2f}")
    logger.warning(f"Reference credit: ${found_credit:.2f}")
    logger.warning(f"Max sweep price: ${max_sweep_price:.2f}")
    logger.warning("=" * 80)

    return None