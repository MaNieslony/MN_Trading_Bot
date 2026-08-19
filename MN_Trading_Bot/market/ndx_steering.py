# market/ndx_steering.py
from typing import Dict, List, Optional

def _ticker_conid(t) -> Optional[int]:
    c = getattr(t, "contract", None)
    return getattr(c, "conId", None) if c else None

def _norm_delta(x: float) -> float:
    """
    Normalisiert Delta-Werte robust:
    - 2      -> 0.02
    - 0.02   -> 0.02
    """
    x = float(x)
    return x / 100.0 if x > 1.0 else x

def _norm_delta_offset(x: float, *, target_is_points: bool) -> float:
    x = float(x)
    return x / 100.0 if target_is_points else x


def _is_multiple(x: float, step: float, eps: float = 1e-6) -> bool:
    """Float-tolerant modulo check."""
    q = x / step
    return abs(q - round(q)) < eps

def _has_ba(t) -> bool:
    return (
        t is not None
        and (t.bid is not None) and (t.ask is not None)
        and (t.bid > 0) and (t.ask > 0)
    )

def select_ndx_50bps_spread(
    *,
    strikes: List[float],
    deltas: Dict[float, float],
    underlying_price: float,
    expiry: str,
    trading_class: str,
    rescan: int,
    # template-driven parameters
    strike_upper_offset: float,
    strike_lower_offset: float,
    strike_step: Optional[float],
    max_strike_scan: int,
    target_delta: float,
    delta_target_offset: float,
    delta_rescan_expansion: float,
    delta_max_abs: float,
    short_mid_min: float,
    short_mid_max: float,
    short_leg_mid_expansion: float,
    # min_sweep_price / max_sweep_price from template (IB notation, usually negative)
    credit_min: float,
    credit_max: float,
    # callbacks / services
    get_option_conid,
    ib,
    wait_for_ticker_data,
    logger,
    leg1_put_call: str,
    leg2_put_call: str,
    leg2_target: float,
    leg2_target_type: str,
) -> Optional[dict]:
    """
    NDX 50BPS strike selection (MN Bot Steering):
    - Strike window: underlying - strike_lower_offset .. underlying - strike_upper_offset
    - Delta window:
        delta_min fixed = target - offset  (z.B. 1.8)
        delta_max grows with rescan:
          rescan=0 -> target (2.0)
          rescan=1 -> target+0.5 (2.5)
          rescan=2 -> target+1.0 (3.0)
          ...
        capped by DELTA_MAX_ABS (z.B. 5.0)
    - Evaluate up to max_strike_scan candidates per attempt.
    - Spread fixed width via leg2_target (typically -50 offset).
    - Adaptive selection:
        rescan=0: closest to target delta, tie-break higher credit
        rescan>=1: highest delta in range, tie-break higher credit
    - Credit window derived from MIN_SWEEP_PRICE/MAX_SWEEP_PRICE (negative IB notation) and evaluated as positive.
    """

    # ------------------------------------------------------------
    # Candidate strike window
    # ------------------------------------------------------------
    lower = underlying_price - float(strike_lower_offset)
    upper = underlying_price - float(strike_upper_offset)

    candidate_strikes = [s for s in strikes if lower <= s <= upper]

    if strike_step:
        step = float(strike_step)
        candidate_strikes = [s for s in candidate_strikes if _is_multiple(s, step)]

    if not candidate_strikes:
        logger.warning("No candidate strikes available in configured window")
        return None

    logger.info(f"Scanning {len(candidate_strikes)} strikes between {int(lower)} and {int(upper)}")

    # ------------------------------------------------------------
    # Short leg mid range expansion
    # ------------------------------------------------------------
    expansion = rescan * float(short_leg_mid_expansion)
    mid_min = float(short_mid_min)
    mid_max = float(short_mid_max) + expansion

    # Last rescans: allow higher premiums (nur mid_max betroffen)
    if rescan >= 3:
        mid_max = mid_max * 1.4  # +40%

    # ------------------------------------------------------------
    # Delta range (wie von dir spezifiziert)
    # LEG1_TARGET=2, OFFSET=0.2, EXPANSION=0.5, MAX_ABS=5.0
    #
    # rescan=0: 1.8 – 2.0
    # rescan=1: 1.8 – 2.5
    # rescan=2: 1.8 – 3.0
    # ...
    # ------------------------------------------------------------
    target_is_points = float(target_delta) >= 1.0

    target = _norm_delta(target_delta)  # 2 -> 0.02
    offset = _norm_delta_offset(delta_target_offset, target_is_points=target_is_points)  # 0.2 -> 0.002
    expand = _norm_delta_offset(delta_rescan_expansion, target_is_points=target_is_points)  # 0.5 -> 0.005
    max_abs = _norm_delta(delta_max_abs)  # 5 -> 0.05

    # lower bound FIX = target - offset (z.B. 0.018)
    delta_min = max(0.0001, target - offset)

    # upper bound: start at target, then expands per rescan
    # rescan=0 -> target
    # rescan=1 -> target + 1*expand
    # rescan=2 -> target + 2*expand
    delta_max_eff = min(max_abs, target + (rescan * expand))

    # safety
    delta_max_eff = max(delta_max_eff, delta_min)

    logger.info("=" * 80)
    logger.info(f"Expanded Short Leg range: ${mid_min:.2f} - ${mid_max:.2f}")
    logger.info(
        f"Delta range: {delta_min:.4f} – {delta_max_eff:.4f}  "
        f"({delta_min*100:.1f} – {delta_max_eff*100:.1f} delta-points)"
    )
    logger.info("=" * 80)

    # ------------------------------------------------------------
    # Delta refresh starting at rescan>=1
    # ------------------------------------------------------------
    delta_refresh_start = 1
    if rescan >= delta_refresh_start:
        # Refresh only a limited subset to avoid blocking too long.
        # Always ascending order, independent of put/call.
        ordered = sorted(candidate_strikes)

        # Limit strikes to refresh
        refresh_limit = min(len(ordered), max(int(max_strike_scan) * 3, 20))
        refresh_limit = min(refresh_limit, 60)
        refresh_strikes = ordered[:refresh_limit]

        try:
            from market.greeks import get_option_deltas as _get_option_deltas

            fresh = _get_option_deltas(
                ib=ib,
                expiry=expiry,
                strikes=refresh_strikes,
                put_call=leg1_put_call,
                trading_class=trading_class,
                get_option_conid_callable=lambda e, s, r, tc=None: get_option_conid(e, s, r, tc or trading_class),
                wait_for_ticker_data_callable=wait_for_ticker_data,
                logger=logger,
            )

            if fresh:
                deltas.update(fresh)  # in-place recache
                logger.info(
                    f"NDX delta refresh (rescan={rescan}) updated {len(fresh)}/{len(refresh_strikes)} strikes"
                )
            else:
                logger.warning(f"NDX delta refresh (rescan={rescan}) returned no data")
        except Exception as e:
            logger.warning(f"NDX delta refresh failed (rescan={rescan}): {e}")
    
    # ------------------------------------------------------------
    # Prepare deltas for candidate strikes (use cached deltas dict)
    # ------------------------------------------------------------
    deltas_available = []
    for s in candidate_strikes:
        d = deltas.get(s)
        if d is None:
            continue
        deltas_available.append((s, abs(float(d))))

    if not deltas_available:
        logger.warning("No Greeks/delta available for any candidate strikes")
        return None

    # ------------------------------------------------------------
    # Filter strikes by delta window [delta_min .. delta_max_eff]
    # ------------------------------------------------------------
    eligible = [(s, d) for s, d in deltas_available if delta_min <= d <= delta_max_eff]

    if not eligible:
        above_min = [(s, d) for s, d in deltas_available if d >= delta_min]
        if above_min:
            s_closest, d_closest = min(above_min, key=lambda x: x[1])
            logger.info(
                f"No deltas in range [{delta_min:.4f}-{delta_max_eff:.4f}]. "
                f"Closest above min: {int(s_closest)} (delta={d_closest:.4f})"
            )
        else:
            s_high, d_high = max(deltas_available, key=lambda x: x[1])
            logger.info(
                f"No deltas >= {delta_min:.4f}. Highest available: "
                f"{int(s_high)} (delta={d_high:.4f})"
            )
        logger.warning("No valid spread found using delta-window strategy")
        return None

    # ------------------------------------------------------------
    # Adaptive ordering for scan candidates:
    # - rescan==0: closest to target delta
    # - rescan>=1: highest delta in range
    # ------------------------------------------------------------
    if rescan == 0:
        method = "closest_to_target"
        eligible.sort(key=lambda x: (abs(x[1] - target), x[1], x[0]))
    else:
        method = "highest_in_range"
        is_put = (leg1_put_call or "").upper().startswith("P")
        if is_put:
            eligible.sort(key=lambda x: (-x[1], -x[0]))  # higher delta, then higher strike
        else:
            eligible.sort(key=lambda x: (-x[1], x[0]))   # higher delta, then lower strike

    scan_candidates = eligible[: int(max_strike_scan)]
    logger.info(
        f"Delta-eligible strikes: {len(eligible)} (scanning up to {len(scan_candidates)} this attempt)"
    )

    # optional: sichtbar machen, welchen "anchor" du faktisch priorisierst
    anchor_s, anchor_d = scan_candidates[0]
    logger.info(
        f"Anchor priority by delta: {int(anchor_s)} (delta={anchor_d:.4f}, method={method})"
    )

    # ------------------------------------------------------------
    # Credit window normalization (template uses negative IB notation)
    # MIN_SWEEP_PRICE=-0.6, MAX_SWEEP_PRICE=-0.3 -> positive credit range [0.30..0.60]
    # ------------------------------------------------------------
    pos_credit_min = min(abs(float(credit_min)), abs(float(credit_max)))
    pos_credit_max = max(abs(float(credit_min)), abs(float(credit_max)))

    best = None
    eval_rows = []  # (short_strike, long_strike, short_delta, c1, c2)
    all_contracts = []

    # ------------------------------------------------------------
    # 1) Build all contract pairs first (no market data yet)
    # ------------------------------------------------------------
    for short_strike, short_delta in scan_candidates:
        # long strike derived from template
        if (leg2_target_type or "").lower() == "strikeoffset_leg1":
            long_strike = short_strike + float(leg2_target)
        else:
            long_strike = float(leg2_target)

        if long_strike >= short_strike:
            continue

        try:
            c1 = get_option_conid(expiry, short_strike, leg1_put_call, trading_class)
            c2 = get_option_conid(expiry, long_strike, leg2_put_call, trading_class)
            if not c1 or not c2:
                continue

            eval_rows.append((short_strike, long_strike, short_delta, c1, c2))
            all_contracts.extend([c1, c2])

        except Exception:
            logger.exception("NDX steering contract qualification error")
            continue

    if not eval_rows:
        logger.warning("No valid contract pairs to evaluate")
        return None

    # ------------------------------------------------------------
    # 2) Batch request tickers ONCE for all legs
    # ------------------------------------------------------------
    # Deduplicate contracts by conId to reduce load
    uniq = {}
    for c in all_contracts:
        cid = getattr(c, "conId", None)
        if isinstance(cid, int) and cid > 0:
            uniq[cid] = c
    all_contracts = list(uniq.values())

    tickers = ib.reqTickers(*all_contracts)

    # wait once
    if not wait_for_ticker_data(tickers, timeout=1.5):
        logger.warning("NDX steering: batch ticker timeout")
        return None

    # map conId -> ticker
    ticker_map: Dict[int, object] = {}
    for t in tickers:
        cid = _ticker_conid(t)
        if cid is not None:
            ticker_map[cid] = t

    # ------------------------------------------------------------
    # 3) Evaluate candidates without further waiting / IB calls
    # ------------------------------------------------------------
    for short_strike, long_strike, short_delta, c1, c2 in eval_rows:
        t1 = ticker_map.get(getattr(c1, "conId", None))
        t2 = ticker_map.get(getattr(c2, "conId", None))

        if not (t1 and t2):
            continue
        if not (_has_ba(t1) and _has_ba(t2)):
            continue

        short_mid = (t1.bid + t1.ask) / 2.0
        long_mid = (t2.bid + t2.ask) / 2.0
        credit = short_mid - long_mid  # positive credit

        logger.debug(
            f"Evaluated {int(short_strike)}/{int(long_strike)} - "
            f"ShortMid=${short_mid:.2f}, Credit=${credit:.2f}, Delta={short_delta:.4f}"
        )

        # credit window
        if not (pos_credit_min <= credit <= pos_credit_max):
            continue

        # short mid window
        if not (mid_min <= short_mid <= mid_max):
            continue

        if rescan == 0:
            cand = (
                abs(short_delta - target),
                -credit,
                short_delta,
                short_strike,
                long_strike,
                short_mid,
                long_mid,
            )
        else:
            cand = (
                -short_delta,
                -credit,
                short_delta,
                short_strike,
                long_strike,
                short_mid,
                long_mid,
            )

        if best is None or cand < best:
            best = cand

    if best is None:
        logger.warning("No valid spread found (delta ok, but none matched credit+mid constraints)")
        return None

    _, neg_credit, short_delta, short_strike, long_strike, short_mid, long_mid = best
    credit = -neg_credit

    logger.info(
        f"✅ Selected spread {int(short_strike)}/{int(long_strike)} - "
        f"Credit ${credit:.2f}, ShortMid ${short_mid:.2f}, Delta {short_delta:.4f}"
    )

    return {
        "short_strike": short_strike,
        "long_strike": long_strike,
        "short_mid": float(short_mid),
        "long_mid": float(long_mid),
        "market_credit": float(credit),
        "short_delta": float(short_delta),
        "delta_min": float(delta_min),
        "delta_max": float(delta_max_eff),
        "selection_method": method,
        "anchor_strike": float(anchor_s),
        "anchor_delta": float(anchor_d),
    }