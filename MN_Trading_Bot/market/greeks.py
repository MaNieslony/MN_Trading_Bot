# market\greeks.py
from typing import Dict, List

def get_option_deltas(
    *,
    ib,
    expiry: str,
    strikes: List[float],
    put_call: str,
    trading_class: str,
    get_option_conid_callable,
    wait_for_ticker_data_callable,
    logger,
) -> Dict[float, float]:
    """
    Fetch delta values for a list of option strikes via IB.
    """

    MAX_SCAN_DELTA = 0.47
    GREEKS_TIMEOUT_SECONDS = 10.0

    deltas: Dict[float, float] = {}
    contracts = []
    tickers = []

    try:
        logger.debug(f"Fetching delta for {len(strikes)} strikes ({put_call})")

        # QUALIFY OPTION CONTRACTS
        for strike in strikes:
            try:
                contract = get_option_conid_callable(
                    expiry, strike, put_call, trading_class
                )
                if contract:
                    contracts.append((strike, contract))
            except Exception as e:
                logger.debug(f"Failed to qualify {put_call} ${strike}: {e}")
                continue

        if not contracts:
            logger.warning("No contracts successfully qualified for delta lookup")
            return deltas

        logger.debug(
            f"Qualified {len(contracts)} contracts, requesting market data..."
        )

        # REQUEST MARKET DATA WITH GREEKS
        for strike, contract in contracts:
            ticker = ib.reqMktData(contract, genericTickList="106")  # 106 = greeks
            tickers.append(ticker)

        if not wait_for_ticker_data_callable(
            tickers, timeout=GREEKS_TIMEOUT_SECONDS, wait_for_greeks=True
        ):
            logger.warning("Timeout waiting for Greeks data")
            return deltas

        # EXTRACT DELTA VALUES
        for (strike, contract), ticker in zip(contracts, tickers):
            if ticker.modelGreeks and hasattr(ticker.modelGreeks, "delta"):
                delta = ticker.modelGreeks.delta
                if delta is not None:
                    if abs(delta) <= MAX_SCAN_DELTA:
                        deltas[strike] = delta
                        logger.debug(
                            f"  ${strike:6.0f} {put_call}: delta = {delta:+.4f}"
                        )
                    else:
                        logger.debug(
                            f"  ${strike:6.0f} {put_call}: delta = {delta:+.4f} "
                            f"(ignored – ITM)"
                        )
                else:
                    logger.debug(
                        f"  ${strike:6.0f} {put_call}: delta = N/A"
                    )
            else:
                logger.debug(
                    f"  ${strike:6.0f} {put_call}: no Greeks available"
                )

        if not deltas:
            logger.warning(
                f"All candidate strikes filtered out "
                f"(|delta| > {MAX_SCAN_DELTA:.2f})"
            )

        logger.info(f"Retrieved delta for {len(deltas)} strikes")

    except Exception as e:
        logger.error(
            f"Error fetching option deltas: {e}", exc_info=True
        )

    finally:
        # Cancel subscriptions - reqMktData subscriptions are properly tracked
        for ticker in tickers:
            try:
                ib.cancelMktData(ticker.contract)
            except Exception:
                pass

    return deltas