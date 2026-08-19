# market/option_chain.py

from typing import List, Optional, Tuple
from datetime import datetime
import pytz

def get_option_chain(
    *,
    ib,
    expiry: str,
    underlying_price: Optional[float],
    get_index_contract_callable,
    logger,
    debug_mode: bool,
    strike_window_override: Optional[int] = None,
) -> Tuple[Optional[str], List[float]]:
    """
    Retrieve the option-chain tradingClass plus a filtered strike list.

    Notes
    -----
    - IB returns multiple option chains per index (exchange + tradingClass).
    - SPX  -> SPXW
    - NDX  -> NDXP (forced, no fallback to NDX)
    - RUT  -> RUTW (fallback RUT, dann erste SMART-Chain – bitte im DEBUG-Log verifizieren!)
    - Strike filtering is symbol-dependent (NDX needs a much wider window).
    """
    try:
        contract = get_index_contract_callable()
        ib.qualifyContracts(contract)

        logger.debug(
            f"Requesting option chains for {contract.symbol} (conId={contract.conId})"
        )

        chains = ib.reqSecDefOptParams(
            contract.symbol,
            "",
            contract.secType,
            contract.conId,
        )

        if not chains:
            logger.error("No option chains received")
            return None, []

        logger.debug(f"Received {len(chains)} option chains")

        if debug_mode:
            for chain in chains:
                logger.debug(
                    f"Chain: exchange={chain.exchange}, "
                    f"tradingClass={chain.tradingClass}, "
                    f"expirations={len(chain.expirations)}"
                )

        # ------------------------------------------------------------
        # Select matching SMART chain (symbol-specific)
        # ------------------------------------------------------------
        symbol = contract.symbol
        matching_chain = None

        # --- SPX: SPXW ---
        if symbol == "SPX":
            for chain in chains:
                if chain.exchange == "SMART" and chain.tradingClass == "SPXW":
                    matching_chain = chain
                    logger.debug("Selected SPXW option chain for SPX")
                    break

            if not matching_chain:
                logger.error("No SMART SPXW option chain found for SPX")
                return None, []

        # --- NDX: NDXP ONLY ---
        elif symbol == "NDX":
            for chain in chains:
                if chain.exchange == "SMART" and chain.tradingClass == "NDXP":
                    matching_chain = chain
                    logger.debug("Selected NDXP option chain for NDX")
                    break

            if not matching_chain:
                logger.error(
                    "No SMART NDXP option chain found for NDX "
                    "(NDXP required, fallback to NDX disabled)"
                )
                return None, []

        # --- RUT: RUTW, fallback RUT, fallback erste SMART-Chain   ---
        elif symbol == "RUT":
            for preferred_class in ("RUTW", "RUT"):
                for chain in chains:
                    if chain.exchange == "SMART" and chain.tradingClass == preferred_class:
                        matching_chain = chain
                        logger.debug(f"Selected {preferred_class} option chain for RUT")
                        break
                if matching_chain:
                    break

            if not matching_chain:
                for chain in chains:
                    if chain.exchange == "SMART":
                        matching_chain = chain
                        logger.warning(
                            f"No RUTW/RUT SMART chain found – falling back to "
                            f"tradingClass={chain.tradingClass} (bitte verifizieren!)"
                        )
                        break

            if not matching_chain:
                logger.error("No SMART option chain found for RUT")
                return None, []

        else:
            logger.error(f"Unsupported symbol for option chain: {symbol}")
            return None, []

        # ------------------------------------------------------------
        # Optional: expiry availability check
        # ------------------------------------------------------------
        if expiry not in getattr(matching_chain, "expirations", set()):
            logger.error(
                f"Expiry {expiry} not available in tradingClass "
                f"{matching_chain.tradingClass}"
            )
            exps = sorted(list(getattr(matching_chain, "expirations", [])))
            if exps:
                logger.debug(f"Available expirations (first 10): {exps[:10]}")
            return None, []

        # ------------------------------------------------------------
        # Strike filtering (symbol-aware)
        # ------------------------------------------------------------
        current_price = underlying_price

        def strike_window(sym: str) -> int:
            if strike_window_override is not None:
                return int(strike_window_override)
            if sym == "NDX":
                return 800
            if sym == "SPX":
                return 150
            if sym == "RUT":
                return 150
            return 50

        if current_price:
            window = strike_window(symbol)
            filtered_strikes = [
                s for s in matching_chain.strikes
                if abs(float(s) - float(current_price)) <= window
            ]
        else:
            filtered_strikes = list(matching_chain.strikes)


        logger.debug(
            f"Selected chain: exchange={matching_chain.exchange}, "
            f"tradingClass={matching_chain.tradingClass}, "
            f"strikes={len(filtered_strikes)} "
            f"(filtered from {len(matching_chain.strikes)})"
        )

        return matching_chain.tradingClass, filtered_strikes

    except Exception as e:
        logger.error(f"Error getting option chain: {e}", exc_info=True)
        return None, []

def get_best_expiry_by_dte(
    *,
    ib,
    target_dte: int,
    min_dte: int,
    max_dte: int,
    get_index_contract_callable,
    logger,
    debug_mode: bool,
) -> Optional[str]:
    """
    Select the best available expiration within [min_dte, max_dte]
    closest to target_dte. Falls back to closest overall expiration
    if none in range.

    Returns:
        expiry string YYYYMMDD or None if chains not available.
    """
    try:
        contract = get_index_contract_callable()
        ib.qualifyContracts(contract)

        logger.debug(
            f"Requesting option chains for {contract.symbol} (conId={contract.conId})"
        )

        chains = ib.reqSecDefOptParams(
            contract.symbol,
            "",
            contract.secType,
            contract.conId,
        )

        if not chains:
            logger.error("No option chains received")
            return None

        if debug_mode:
            logger.debug(f"Received {len(chains)} option chains")

        # ------------------------------------------------------------
        # Select matching SMART chain (symbol-specific)
        # (same logic as get_option_chain)
        # ------------------------------------------------------------
        symbol = contract.symbol
        matching_chain = None

        if symbol == "SPX":
            for chain in chains:
                if chain.exchange == "SMART" and chain.tradingClass == "SPXW":
                    matching_chain = chain
                    break
            if not matching_chain:
                logger.error("No SMART SPXW option chain found for SPX")
                return None

        elif symbol == "NDX":
            for chain in chains:
                if chain.exchange == "SMART" and chain.tradingClass == "NDXP":
                    matching_chain = chain
                    break
            if not matching_chain:
                logger.error("No SMART NDXP option chain found for NDX")
                return None

        elif symbol == "RUT":
            for preferred_class in ("RUTW", "RUT"):
                for chain in chains:
                    if chain.exchange == "SMART" and chain.tradingClass == preferred_class:
                        matching_chain = chain
                        break
                if matching_chain:
                    break

            if not matching_chain:
                for chain in chains:
                    if chain.exchange == "SMART":
                        matching_chain = chain
                        logger.warning(
                            f"No RUTW/RUT SMART chain found – falling back to "
                            f"tradingClass={chain.tradingClass} (bitte verifizieren!)"
                        )
                        break

            if not matching_chain:
                logger.error("No SMART option chain found for RUT")
                return None

        else:
            logger.error(f"Unsupported symbol for option chain: {symbol}")
            return None

        expirations = sorted(list(getattr(matching_chain, "expirations", []) or []))
        if not expirations:
            logger.error("No expirations found in matching chain")
            return None

        # ------------------------------------------------------------
        # DTE selection (Standalone-style)
        # ------------------------------------------------------------
        et_tz = pytz.timezone("US/Eastern")
        today = datetime.now(et_tz).date()

        best_in_range = None
        best_in_range_diff = float("inf")

        best_overall = None
        best_overall_diff = float("inf")

        logger.debug(
            f"Searching expirations {min_dte}-{max_dte} DTE (target={target_dte}) "
            f"in tradingClass {matching_chain.tradingClass}"
        )

        for exp in expirations:
            try:
                exp_date = datetime.strptime(exp, "%Y%m%d").date()
                dte = (exp_date - today).days

                if dte < 0:
                    continue

                diff = abs(dte - int(target_dte))

                if diff < best_overall_diff:
                    best_overall_diff = diff
                    best_overall = exp

                if int(min_dte) <= dte <= int(max_dte):
                    if diff < best_in_range_diff:
                        best_in_range_diff = diff
                        best_in_range = exp

                    if debug_mode:
                        logger.debug(f"  {exp}: {dte} DTE (diff={diff})")

            except Exception as e:
                if debug_mode:
                    logger.debug(f"Error parsing expiration {exp}: {e}")
                continue

        if best_in_range:
            best_dte = (datetime.strptime(best_in_range, "%Y%m%d").date() - today).days
            logger.info(
                f"✓ Selected expiration in range: {best_in_range} "
                f"({best_dte} DTE, {abs(best_dte - int(target_dte))} days from target)"
            )
            return best_in_range

        if best_overall:
            best_dte = (datetime.strptime(best_overall, "%Y%m%d").date() - today).days
            logger.warning(
                f"No expirations found between {min_dte}-{max_dte} DTE. "
                f"Using closest available: {best_overall} ({best_dte} DTE)"
            )
            return best_overall

        logger.error("No usable expiration found after filtering")
        return None

    except Exception as e:
        logger.error(f"Error selecting best expiry by DTE: {e}", exc_info=True)
        return None