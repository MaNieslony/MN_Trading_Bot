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
    delta_limit: float,
    strike_step: float,
    min_spread_width: float,
    max_spread_width: float,
    put_delta_window: float,
    call_delta_window: float,
    get_option_conid,
    ib,
    wait_for_ticker_data,
    logger,
) -> Optional[dict]:
    """
    Delta-symmetrischer RUT Iron Condor:
    - Short Put / Short Call: erste Strike außerhalb ATM, deren |Delta| < delta_limit
    - Long Put / Long Call: Briefkurs-Regel-Walk zwischen min_spread_width und max_spread_width
    Holt Put- und Call-Deltas selbst (unabhängig vom generischen Delta-Cache der anderen Strategien).
    """
    from market.greeks import get_option_deltas

    strikes_set = set(strikes)

    conid_cb = lambda e, s, r, tc=None: get_option_conid(e, s, r, tc or trading_class)

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

    # ------------------------------------------------------------
    # SHORT PUT (unterhalb Spot)
    # ------------------------------------------------------------
    put_candidates = sorted(
        ((s, abs(d)) for s, d in put_deltas.items() if s < underlying_price),
        key=lambda x: underlying_price - x[0],  # nächstes an ATM zuerst
    )
    short_put = _pick_short_strike_below_delta_limit(candidates=put_candidates, delta_limit=delta_limit)

    # ------------------------------------------------------------
    # SHORT CALL (oberhalb Spot)
    # ------------------------------------------------------------
    call_candidates = sorted(
        ((s, abs(d)) for s, d in call_deltas.items() if s > underlying_price),
        key=lambda x: x[0] - underlying_price,
    )
    short_call = _pick_short_strike_below_delta_limit(candidates=call_candidates, delta_limit=delta_limit)

    if not short_put or not short_call:
        logger.warning(
            f"RUT-IC: kein gültiger Short-Strike gefunden "
            f"(put={short_put}, call={short_call}, delta_limit={delta_limit:.4f})"
        )
        return None

    short_put_strike, short_put_delta = short_put
    short_call_strike, short_call_delta = short_call

    logger.info(
        f"RUT-IC Short Strikes: PUT {int(short_put_strike)} (Δ={short_put_delta:.4f}) / "
        f"CALL {int(short_call_strike)} (Δ={short_call_delta:.4f}) | Limit={delta_limit:.4f}"
    )

    # ------------------------------------------------------------
    # Briefkurs-Regel: Ask-Preise der möglichen Long-Strikes batched holen
    # ------------------------------------------------------------
    def build_ask_lookup(put_call: str, short_strike: float, direction: int) -> Dict[float, float]:
        n_min = max(1, round(min_spread_width / strike_step))
        n_max = round(max_spread_width / strike_step)

        candidate_strikes = [
            short_strike + direction * n * strike_step
            for n in range(n_min, n_max + 1)
        ]
        candidate_strikes = [s for s in candidate_strikes if s in strikes_set]

        contracts = []
        for s in candidate_strikes:
            c = get_option_conid(expiry, s, put_call, trading_class)
            if c:
                contracts.append((s, c))

        if not contracts:
            return {}

        tickers = ib.reqTickers(*[c for _, c in contracts])
        if not wait_for_ticker_data(tickers, timeout=2.0):
            logger.warning(f"RUT-IC: Ticker-Timeout bei {put_call} Long-Strike Kandidaten")

        asks: Dict[float, float] = {}
        for (s, _c), t in zip(contracts, tickers):
            if t.ask is not None and t.ask > 0:
                asks[s] = float(t.ask)
        return asks

    put_asks = build_ask_lookup("P", short_put_strike, -1)
    call_asks = build_ask_lookup("C", short_call_strike, 1)

    long_put = _walk_long_strike(
        short_strike=short_put_strike, direction=-1, strike_step=strike_step,
        min_width=min_spread_width, max_width=max_spread_width,
        strikes_available=strikes_set, get_ask_callable=lambda s: put_asks.get(s),
        logger=logger, side_label="RUT-IC PUT",
    )
    long_call = _walk_long_strike(
        short_strike=short_call_strike, direction=1, strike_step=strike_step,
        min_width=min_spread_width, max_width=max_spread_width,
        strikes_available=strikes_set, get_ask_callable=lambda s: call_asks.get(s),
        logger=logger, side_label="RUT-IC CALL",
    )

    if not long_put or not long_call:
        logger.warning("RUT-IC: Long-Strikes (Briefkurs-Regel) konnten nicht bestimmt werden")
        return None

    logger.info(
        f"RUT-IC Long Strikes (Briefkurs-Regel): "
        f"PUT {int(long_put['strike'])} (Breite={long_put['width']:.0f}) / "
        f"CALL {int(long_call['strike'])} (Breite={long_call['width']:.0f})"
    )

    return {
        "short_put_strike": short_put_strike,
        "long_put_strike": long_put["strike"],
        "short_call_strike": short_call_strike,
        "long_call_strike": long_call["strike"],
        "short_put_delta": short_put_delta,
        "short_call_delta": short_call_delta,
        "put_width": long_put["width"],
        "call_width": long_call["width"],
    }