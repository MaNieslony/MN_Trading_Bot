# market/market_data.py
from typing import Optional
from market.indicators import calculate_rsi

def ensure_live_data_if_market_open(
    *,
    ib,
    is_market_open_callable,
    is_paper_trading
):
    if not ib.isConnected() or is_paper_trading:
        return

    if is_market_open_callable():
        ib.reqMarketDataType(1)

def get_open_price(
    *,
    ib,
    symbol: str,
    get_index_contract_callable,
    logger,
    attempts: int = 3,
    retry_sleep: float = 2.0,
) -> Optional[float]:
    """Fetch today's symbol opening price with retry against transient IB errors like Error 162"""
    try:
        contract = get_index_contract_callable()
        ib.qualifyContracts(contract)
    except Exception as e:
        logger.error(f"Error qualifying contract for open price: {e}")
        return None

    for attempt in range(1, attempts + 1):
        try:
            bars = ib.reqHistoricalData(
                contract,
                endDateTime='',
                durationStr='1 D',
                barSizeSetting='1 day',
                whatToShow='TRADES',
                useRTH=True,
                formatDate=1
            )

            if bars and len(bars) > 0:
                open_price = bars[-1].open
                logger.info(f"{symbol} open price: {open_price:.2f}")
                return open_price

            logger.warning(
                f"No historical data received for open price (attempt {attempt}/{attempts})"
            )

        except Exception as e:
            logger.error(
                f"Error getting open price (attempt {attempt}/{attempts}): {e}"
            )

        if attempt < attempts:
            ib.sleep(retry_sleep)

    logger.error(f"Failed to get open price for {symbol} after {attempts} attempts")
    return None

def get_current_price(
    *,
    ib,
    symbol: str,
    get_index_contract_callable,
    logger,
    attempts: int = 3,
    retry_sleep: float = 1.5,
) -> Optional[float]:
    """Fetch the current index price with retry"""
    try:
        contract = get_index_contract_callable()
        ib.qualifyContracts(contract)
    except Exception as e:
        logger.error(f"Error qualifying contract for current price: {e}")
        return None

    for attempt in range(1, attempts + 1):
        try:
            ticker = ib.reqMktData(contract, '', False, False)
            ib.sleep(1.5)

            price = None
            if ticker.last and ticker.last > 0:
                price = ticker.last
            elif ticker.close and ticker.close > 0:
                price = ticker.close
            else:
                try:
                    mp = ticker.marketPrice()
                    if mp and mp > 0:
                        price = mp
                except Exception:
                    pass

            ib.cancelMktData(contract)

            if price:
                logger.info(f"{symbol} current price: {price:.2f}")
                return price

            logger.warning(
                f"No valid price data received (attempt {attempt}/{attempts})"
            )

        except Exception as e:
            logger.error(
                f"Error getting current price (attempt {attempt}/{attempts}): {e}"
            )
            try:
                ib.cancelMktData(contract)
            except Exception:
                pass

        if attempt < attempts:
            ib.sleep(retry_sleep)

    logger.error(f"Failed to get current price for {symbol} after {attempts} attempts")
    return None

def get_rsi(
    *,
    ib,
    symbol: str,
    get_index_contract_callable,
    period: int,
    bar_size: str,
    logger,
) -> Optional[float]:
    """
    Fetch historical bars via IB and calculate RSI.
    Drop-in replacement for get_spx_rsi.
    """
    try:
        contract = get_index_contract_callable()
        ib.qualifyContracts(contract)

        bars = ib.reqHistoricalData(
            contract,
            endDateTime='',
            durationStr='60 D',
            barSizeSetting=bar_size,
            whatToShow='TRADES',
            useRTH=True,
            formatDate=1
        )

        if not bars or len(bars) < period + 1:
            logger.warning(
                f"Insufficient bars for RSI: got {len(bars) if bars else 0}, "
                f"need {period + 1}"
            )
            return None

        closes = [bar.close for bar in bars]

        rsi = calculate_rsi(closes=closes, period=period)

        if rsi is None:
            return None

        logger.info(
            f"{symbol} RSI({period}) on {bar_size}: {rsi:.2f} "
            f"(last close: {closes[-1]:.2f})"
        )

        return rsi

    except Exception as e:
        logger.error(f"Error calculating RSI: {e}", exc_info=True)
        return None

from market.indicators import calculate_sma


def get_sma(
    *,
    ib,
    symbol: str,
    get_index_contract_callable,
    period: int,
    bar_size: str = "1 day",
    logger,
):
    """
    Get SMA based on historical bars (same data source as RSI).
    """

    try:
        contract = get_index_contract_callable()

        bars = ib.reqHistoricalData(
            contract,
            endDateTime="",
            durationStr=f"{period + 2} D",
            barSizeSetting=bar_size,
            whatToShow="TRADES",
            useRTH=True,
            formatDate=1,
        )

        if not bars:
            logger.warning("No bars returned for SMA")
            return None

        closes = [bar.close for bar in bars if bar.close is not None]

        return calculate_sma(closes=closes, period=period)

    except Exception as e:
        logger.error(f"Failed to calculate SMA: {e}")
        return None

def get_vix_price(
    *,
    ib,
    logger,
) -> Optional[float]:
    """
    Fetch current VIX price (robust for IB quirks).
    """

    try:
        from ib_insync import Index

        contract = Index(symbol="VIX", exchange="CBOE")
        ib.qualifyContracts(contract)

        ticker = ib.reqMktData(contract, '', False, False)

        for attempt in range(3):
            ib.sleep(1)

            # 1) last
            if getattr(ticker, "last", None) and ticker.last > 0:
                price = float(ticker.last)
                ib.cancelMktData(contract)
                logger.info(f"VIX price (last): {price:.2f}")
                return price

            # 2) marketPrice
            try:
                mp = ticker.marketPrice()
                if mp and mp > 0:
                    price = float(mp)
                    ib.cancelMktData(contract)
                    logger.info(f"VIX price (marketPrice): {price:.2f}")
                    return price
            except Exception:
                pass

            # 3) midpoint (WICHTIG für VIX!)
            bid = getattr(ticker, "bid", None)
            ask = getattr(ticker, "ask", None)

            if bid and ask and bid > 0 and ask > 0:
                price = round((bid + ask) / 2, 2)
                ib.cancelMktData(contract)
                logger.info(f"VIX price (midpoint): {price:.2f}")
                return price

            # 4) fallback close
            if getattr(ticker, "close", None) and ticker.close > 0:
                price = float(ticker.close)
                ib.cancelMktData(contract)
                logger.info(f"VIX price (close): {price:.2f}")
                return price

        ib.cancelMktData(contract)

        logger.error("No valid VIX data received after retries")
        return None

    except Exception as e:
        logger.error(f"Error getting VIX price: {e}")
        return None

def get_iv_rank(
    *,
    ib,
    symbol: str,
    get_index_contract_callable,
    lookback_days: int = 252,
    logger,
) -> Optional[float]:
    """
    Calculate IV Rank using IV Percentile method (more robust).
    
    IV Percentile = % of days where historical IV < current IV
    Less sensitive to extreme IV spikes than traditional IV Rank.
    
    Args:
        ib: IB connection
        symbol: Underlying symbol (e.g., "SPX", "RUT")
        get_index_contract_callable: Callable that returns the index contract
        lookback_days: Number of days for historical range (252 = 52 weeks)
        logger: Logger instance
    
    Returns:
        IV-Rank as percentage (0-100) or None if calculation fails
    """
    try:
        contract = get_index_contract_callable()
        ib.qualifyContracts(contract)

        duration_str = '1 Y' if lookback_days >= 365 else f'{lookback_days} D'

        bars = ib.reqHistoricalData(
            contract,
            endDateTime='',
            durationStr=duration_str,
            barSizeSetting='1 day',
            whatToShow='OPTION_IMPLIED_VOLATILITY',
            useRTH=True,
            formatDate=1,
        )

        if not bars or len(bars) < 20:
            logger.warning(
                f"Insufficient IV history for {symbol}: "
                f"got {len(bars) if bars else 0} bars, need at least 20"
            )
            return None

        # Extract IV values (convert to percentage)
        iv_values = [
            bar.close * 100 
            for bar in bars 
            if bar.close is not None and bar.close > 0
        ]

        if len(iv_values) < 20:
            logger.warning(f"Insufficient valid IV values for {symbol}")
            return None

        current_iv = iv_values[-1]
        
        # IV Percentile: count how many days had IV lower than current
        days_below = sum(1 for v in iv_values if v < current_iv)
        iv_rank = (days_below / len(iv_values)) * 100.0
        iv_rank = max(0.0, min(100.0, iv_rank))

        # Calculate traditional IV Rank for logging
        iv_min = min(iv_values)
        iv_max = max(iv_values)
        traditional_iv_rank = ((current_iv - iv_min) / (iv_max - iv_min)) * 100.0 if iv_max != iv_min else None

        logger.info(
            f"{symbol} IV-Rank({lookback_days}d): {iv_rank:.1f}% (percentile method) "
            f"[traditional={traditional_iv_rank:.1f}% if traditional_iv_rank else 'N/A'] "
            f"(current={current_iv:.2f}%, range={iv_min:.2f}%-{iv_max:.2f}%, samples={len(iv_values)})"
        )

        return round(iv_rank, 1)

    except Exception as e:
        logger.error(f"Error calculating IV-Rank for {symbol}: {e}", exc_info=True)
        return None