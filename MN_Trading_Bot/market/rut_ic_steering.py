# market/rut_ic_steering.py
from typing import Dict, List, Optional, Tuple


def resolve_dte_and_delta_from_iv_rank(
    *,
    iv_rank: float,
    matrix: List[dict],
) -> Optional[Tuple[int, float]]:
    """
    matrix: Liste von {"MIN_IV_RANK": float, "MAX_DTE": int, "DELTA_LIMIT": float}.
    Gibt (max_dte, delta_limit) für die höchste Schwelle zurück, die iv_rank noch erfüllt (>=).
    """
    if iv_rank is None or not matrix:
        return None

    sorted_matrix = sorted(matrix, key=lambda r: float(r["MIN_IV_RANK"]))

    selected = None
    for row in sorted_matrix:
        if iv_rank >= float(row["MIN_IV_RANK"]):
            selected = row
        else:
            break

    if selected is None:
        selected = sorted_matrix[0]

    return int(selected["MAX_DTE"]), float(selected["DELTA_LIMIT"])


def is_late_entry(*, now_et, late_entry_cutoff_et) -> bool:
    """True, wenn die aktuelle ET-Zeit die Late-Entry-Grenze erreicht/überschreitet (=> DTE+1)."""
    return now_et.time() >= late_entry_cutoff_et

def _norm_delta(x: float) -> float:
    """
    Normalisiert Delta-Werte robust, analog zu ndx_steering.py:
    - 4      -> 0.04
    - 0.04   -> 0.04
    """
    x = float(x)
    return x / 100.0 if x > 1.0 else x

def _pick_short_strike_below_delta_limit(
    *,
    candidates: List[Tuple[float, float]],  # (strike, abs_delta)
    delta_limit: float,
) -> Optional[Tuple[float, float]]:
    """
    "Short Strike wählen, dessen Delta als erstes unterhalb der Delta-Grenze liegt"
    = beim Wandern von ATM nach außen die erste Strike unterhalb des Limits.
    Äquivalent: unter allen Strikes mit |delta| < limit die mit dem höchsten |delta|.
    """
    below = [(s, d) for s, d in candidates if d < delta_limit]
    if not below:
        return None
    return max(below, key=lambda x: x[1])


def _walk_long_strike(
    *,
    short_strike: float,
    direction: int,  # -1 = Put (long strike unterhalb short), +1 = Call (long strike oberhalb short)
    strike_step: float,
    min_width: float,
    max_width: float,
    strikes_available: set,
    get_ask_callable,  # (strike) -> Optional[float]
    logger,
    side_label: str,
) -> Optional[dict]:
    """
    Briefkurs-Regel: bei min_width starten, so lange nach außen wandern, wie der
    Briefkurs (Ask) noch sinkt; stoppen sobald der Ask-Preis identisch bleibt
    (kein Prämienvorteil) oder max_width erreicht ist.
    """
    n_min_steps = max(1, round(min_width / strike_step))
    n_max_steps = round(max_width / strike_step)

    def strike_at(n_steps: float) -> float:
        return short_strike + direction * n_steps * strike_step

    current_n = n_min_steps
    current_strike = strike_at(current_n)

    if current_strike not in strikes_available:
        logger.warning(f"{side_label}: Min-Width Long-Strike {current_strike} nicht in Chain")
        return None

    current_ask = get_ask_callable(current_strike)
    if current_ask is None:
        logger.warning(f"{side_label}: kein Ask-Preis für Long-Strike {current_strike}")
        return None

    while current_n < n_max_steps:
        next_n = current_n + 1
        next_strike = strike_at(next_n)

        if next_strike not in strikes_available:
            break

        next_ask = get_ask_callable(next_strike)
        if next_ask is None:
            break

        # Briefkurs identisch -> kein Vorteil -> beim näheren Strike bleiben
        if abs(next_ask - current_ask) < 0.001:
            logger.debug(
                f"{side_label}: Ask-Plateau bei {current_strike} (${current_ask:.2f}) "
                f"vs {next_strike} (${next_ask:.2f}) – kein weiteres Hinausschieben"
            )
            break

        # Ask günstiger -> mehr Prämie für gleiches Risiko -> weiter hinausschieben
        current_n = next_n
        current_strike = next_strike
        current_ask = next_ask

    return {"strike": current_strike, "ask": current_ask, "width": current_n * strike_step}


def select_rut_iron_condor(
    *,
    strikes: List[float],
    underlying_price: float,
    expiry: str,
    trading_class: str,
    iv_rank: float,  # ← Jetzt aus Config
    iv_rank_matrix: List[dict],
    delta_limit: float,
    strike_step: float,
    put_spread_width: float,  # ← Fest (z.B. 100)
    max_call_spread_width: float,  # ← Dynamisch bis hier
    put_delta_window: float,
    call_delta_window: float,
    get_option_conid,
    ib,
    wait_for_ticker_data,
    logger,
) -> Optional[dict]:
    """
    Delta-symmetrischer RUT Iron Condor:
    - GET DTE/DELTA_LIMIT from iv_rank + matrix
    - Short Put/Call: erste Strike außerhalb ATM, deren |Delta| < delta_limit
    - Long Put: Fest 100 Punkte tiefer
    - Long Call: Dynamisch durch _walk_long_strike bis max_call_spread_width
    """
    from market.greeks import get_option_deltas

    strikes_set = set(strikes)
    
    # Resolve DTE and Delta from IV-Rank matrix
    result = resolve_dte_and_delta_from_iv_rank(iv_rank=iv_rank, matrix=iv_rank_matrix)
    if result is None:
        logger.warning(f"Cannot resolve DTE/Delta from IV-Rank {iv_rank}")
        return None
    
    max_dte, delta_limit = result
    logger.info(f"IV-Rank {iv_rank}% -> DTE={max_dte}, Delta-Limit={delta_limit}%")

    conid_cb = lambda e, s, r, tc=None: get_option_conid(e, s, r, tc or trading_class)

    # GET DELTAS
    put_window_strikes = [s for s in strikes if underlying_price - put_delta_window <= s <= underlying_price]
    call_window_strikes = [s for s in strikes if underlying_price <= s <= underlying_price + call_delta_window]

    put_deltas = get_option_deltas(
        ib=ib, expiry=expiry, strikes=put_window_strikes, put_call="P",
        trading_class=trading_class, get_option_conid_callable=conid_cb,
        wait_for_ticker_data_callable=wait_for_ticker_data, logger=logger,
    )
    call_deltas = get_option_deltas(
        ib=ib, expiry=expiry, strikes=call_window_strikes, put_call="C",
        trading_class=trading_class, get_option_conid_callable=conid_cb,
        wait_for_ticker_data_callable=wait_for_ticker_data, logger=logger,
    )

    if not put_deltas or not call_deltas:
        logger.warning("RUT-IC: keine Put- oder Call-Deltas verfügbar")
        return None

    # SHORT PUT
    put_candidates = sorted(
        ((s, abs(d)) for s, d in put_deltas.items() if s < underlying_price),
        key=lambda x: underlying_price - x[0],
    )
    short_put = _pick_short_strike_below_delta_limit(
        candidates=put_candidates, 
        delta_limit=delta_limit
    )

    if not short_put:
        logger.warning("RUT-IC: Keine PUT-Short-Strike gefunden")
        return None

    short_put_strike = short_put[0]
    logger.info(f"RUT-IC: Short PUT @ {short_put_strike} (delta={short_put[1]:.2f}%)")

    # LONG PUT: Fest 100 Punkte tiefer
    long_put_strike = short_put_strike - put_spread_width
    if long_put_strike not in strikes_set:
        logger.warning(f"RUT-IC: Long PUT {long_put_strike} nicht in Chain")
        return None

    logger.info(f"RUT-IC: Long PUT @ {long_put_strike} (width={put_spread_width})")

    # SHORT CALL
    call_candidates = sorted(
        ((s, abs(d)) for s, d in call_deltas.items() if s > underlying_price),
        key=lambda x: x[0] - underlying_price,
    )
    short_call = _pick_short_strike_below_delta_limit(
        candidates=call_candidates,
        delta_limit=delta_limit
    )

    if not short_call:
        logger.warning("RUT-IC: Keine CALL-Short-Strike gefunden")
        return None

    short_call_strike = short_call[0]
    logger.info(f"RUT-IC: Short CALL @ {short_call_strike} (delta={short_call[1]:.2f}%)")

    # LONG CALL: Dynamisch durch _walk_long_strike
    long_call_result = _walk_long_strike(
        short_strike=short_call_strike,
        direction=+1,  # CALL = nach oben
        strike_step=strike_step,
        min_width=strike_step,  # Mind. 1 Step
        max_width=max_call_spread_width,
        strikes_available=strikes_set,
        get_ask_callable=lambda s: _get_ask_for_strike(ib, expiry, s, "C", get_option_conid),
        logger=logger,
        side_label="RUT-IC CALL",
    )

    if not long_call_result:
        logger.warning("RUT-IC: Keine CALL-Long-Strike gefunden")
        return None

    long_call_strike = long_call_result["strike"]
    call_spread_width = long_call_result["width"]

    logger.info(f"RUT-IC: Long CALL @ {long_call_strike} (width={call_spread_width})")

    # Return Legs
    return {
        "legs": [
            {
                "strike": short_put_strike,
                "put_call": "P",
                "action": "SELL",
                "delta": short_put[1],
            },
            {
                "strike": long_put_strike,
                "put_call": "P",
                "action": "BUY",
                "delta": abs(put_deltas.get(long_put_strike, 0.0)),
            },
            {
                "strike": short_call_strike,
                "put_call": "C",
                "action": "SELL",
                "delta": short_call[1],
            },
            {
                "strike": long_call_strike,
                "put_call": "C",
                "action": "BUY",
                "delta": abs(call_deltas.get(long_call_strike, 0.0)),
            },
        ],
        "put_width": put_spread_width,
        "call_width": call_spread_width,
        "dte": max_dte,
    }


def _get_ask_for_strike(ib, expiry, strike, put_call, get_option_conid_callable):
    """Helper: holt Ask-Preis für einen Strike"""
    try:
        conid = get_option_conid_callable(expiry, strike, put_call)
        # Mkt Data abrufen → Ask
        # (Implementation je nach ib_insync Pattern)
        return None  # Placeholder
    except Exception:
        return None