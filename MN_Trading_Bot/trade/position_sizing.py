# trade/position_sizing.py

def calculate_quantity_from_buying_power(
    *,
    allocation: float,
    min_qty: int,
    max_qty: int,
    mid_credit: float,
    natural_credit: float,
    is_paper_trading: bool,
    logger,
) -> int:
    """
    Dynamic position sizing based on buying power and credit quality.

    Schedule / risk sizing logic.
    Drop-in extraction of Bot.calculate_quantity_from_buying_power.
    """

    if not natural_credit or not mid_credit or natural_credit >= 0 or mid_credit >= 0:
        logger.warning("Invalid credit - using MIN_QTY")
        return min_qty

    # Live Trading: size off abs(mid_credit)
    # Paper Trading: size off abs(natural_credit)
    if is_paper_trading:
        sizing_dollars = abs(natural_credit) * 100
        credit_type = "natural"
    else:
        sizing_dollars = abs(mid_credit) * 100
        credit_type = "mid"

    # floor() by int() to never exceed allocation
    calculated = int(allocation / sizing_dollars)

    # Clamp to MIN/MAX
    quantity = max(min_qty, min(calculated, max_qty))

    logger.info(
        f"Position sizing: ${allocation:.0f} / ${sizing_dollars:.0f} "
        f"({credit_type} credit) = {quantity} contracts "
        f"(range {min_qty}-{max_qty} contracts)"
    )
    logger.info(
        f"  Mid: ${mid_credit:.2f} | Natural: ${natural_credit:.2f} | "
        f"Worst-case cost: ${quantity * sizing_dollars:.0f}"
    )

    return quantity