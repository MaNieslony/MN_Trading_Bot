# trade/strike_targets.py

def select_nearest_atm_strike(
    strikes: list,
    underlying_price: float,
):
    """
    Select ATM strike by flooring to the nearest strike BELOW or EQUAL
    to the underlying price.

    Example:
      underlying=7382.6 -> strike=7380
      underlying=7380.0 -> strike=7380
    """
    if not strikes or underlying_price is None:
        return None

    # nur Strikes <= Underlying zulassen
    candidates = [s for s in strikes if float(s) <= float(underlying_price)]

    if not candidates:
        return None  # alles ITM, sollte praktisch nicht passieren

    # größter Strike <= Underlying
    return float(max(candidates))

def select_percentage_otm_strike(
    strikes: list,
    underlying_price: float,
    pct: float,
):
    """
    Select strike based on percentage distance from underlying.

    pct < 0 → OTM puts
    pct > 0 → calls / OTM upside
    """
    if not strikes or underlying_price is None:
        return None

    strikes = [float(s) for s in strikes]
    underlying_price = float(underlying_price)

    target_price = underlying_price * (1 + pct / 100.0)

    if target_price <= underlying_price:
        candidates = [s for s in strikes if s <= target_price]
        return max(candidates) if candidates else min(strikes, key=lambda s: abs(s - target_price))
    else:
        candidates = [s for s in strikes if s >= target_price]
        return min(candidates) if candidates else min(strikes, key=lambda s: abs(s - target_price))