# trade/combo_factory.py
from ib_insync import ComboLeg, Contract

def create_combo_contract(
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
    min_sweep_price: float,
    max_sweep_price: float,
    get_option_conid_callable,
    logger,
) -> Contract:
    """Create 2-leg Bull Put Spread BAG contract (drop-in extraction)."""

    # ------------------------------------------------------------------
    # QUALIFY OPTION CONTRACTS
    # ------------------------------------------------------------------
    leg1_contract = get_option_conid_callable(
        expiry, leg1, leg1_put_call, trading_class
    )
    leg2_contract = get_option_conid_callable(
        expiry, leg2, leg2_put_call, trading_class
    )

    if not all([leg1_contract, leg2_contract]):
        raise ValueError("Failed to qualify option contracts")

    # ------------------------------------------------------------------
    # CREATE COMBO LEGS
    # ------------------------------------------------------------------
    combo_leg1 = ComboLeg()
    combo_leg1.conId = leg1_contract.conId
    combo_leg1.ratio = leg1_qty
    combo_leg1.action = leg1_action
    combo_leg1.exchange = "SMART"

    combo_leg2 = ComboLeg()
    combo_leg2.conId = leg2_contract.conId
    combo_leg2.ratio = leg2_qty
    combo_leg2.action = leg2_action
    combo_leg2.exchange = "SMART"

    # ------------------------------------------------------------------
    # CREATE BAG CONTRACT
    # ------------------------------------------------------------------
    combo = Contract()
    combo.symbol = symbol
    combo.secType = "BAG"
    combo.currency = "USD"
    combo.exchange = "SMART"
    combo.comboLegs = [combo_leg1, combo_leg2]

    # ------------------------------------------------------------------
    # METADATA (IDENTISCH ZUM ORIGINAL)
    # ------------------------------------------------------------------
    combo._expiry = expiry
    combo._leg1_strike = leg1
    combo._leg2_strike = leg2
    combo._trading_class = trading_class
    combo._min_sweep_price = min_sweep_price
    combo._max_sweep_price = max_sweep_price

    logger.debug("=" * 80)
    logger.info("✅ Combo created:")
    logger.debug("=" * 80)
    logger.info(f"  Leg1: {leg1_action} {leg1_qty}× ${int(leg1)} PUT (short)")
    logger.info(f"  Leg2: {leg2_action} {leg2_qty}× ${int(leg2)} PUT (long)")

    return combo

# trade/combo_factory.py
from ib_insync import ComboLeg, Contract

def create_combo_contract_3leg(
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
    min_sweep_price: float,
    max_sweep_price: float,
    get_option_conid_callable,
    logger,
) -> Contract:
    c1 = get_option_conid_callable(expiry, leg1, leg1_put_call, trading_class)
    c2 = get_option_conid_callable(expiry, leg2, leg2_put_call, trading_class)
    c3 = get_option_conid_callable(expiry, leg3, leg3_put_call, trading_class)

    if not all([c1, c2, c3]):
        raise ValueError("PBW: Failed to qualify one or more option contracts")

    def mk(con, qty, action):
        cl = ComboLeg()
        cl.conId = con.conId
        cl.ratio = int(qty)
        cl.action = action
        cl.exchange = "SMART"
        return cl

    combo = Contract()
    combo.symbol = symbol
    combo.secType = "BAG"
    combo.currency = "USD"
    combo.exchange = "SMART"
    combo.comboLegs = [
        mk(c1, leg1_qty, leg1_action),
        mk(c2, leg2_qty, leg2_action),
        mk(c3, leg3_qty, leg3_action),
    ]

    # metadata (optional)
    combo._expiry = expiry
    combo._trading_class = trading_class
    combo._leg1_strike = leg1
    combo._leg2_strike = leg2
    combo._leg3_strike = leg3
    combo._min_sweep_price = min_sweep_price
    combo._max_sweep_price = max_sweep_price

    logger.info("✅ Combo created:")
    logger.info(f"  Leg1: {leg1_action} {leg1_qty}× {int(leg1)}{leg1_put_call}")
    logger.info(f"  Leg2: {leg2_action} {leg2_qty}× {int(leg2)}{leg2_put_call}")
    logger.info(f"  Leg3: {leg3_action} {leg3_qty}× {int(leg3)}{leg3_put_call}")

    return combo