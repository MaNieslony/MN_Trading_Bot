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
                useRTH=False,
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

from typing import Optional, Callable, Dict, Any
from ib_insync import Contract

from typing import Optional, Callable, Dict, Any
from ib_insync import Contract


from typing import Optional, Callable, Dict, Any
from ib_insync import Contract


def _extract_iv_extremes(config: Optional[Any], symbol: str) -> Optional[Dict[str, float]]:
    """Extrahiert 52W-Extremwerte (low/high) für ein Symbol aus der Template-Konfiguration."""
    if not config:
        return None

    symbol_key = symbol.upper()
    templates = config.values() if isinstance(config, dict) else (config if isinstance(config, list) else [])

    for template in templates:
        if not isinstance(template, dict):
            continue

        # 1. Strukturiert: "IV_52W_EXTREMES": {"RUT": {"low": ..., "high": ...}}
        extremes = template.get("IV_52W_EXTREMES")
        if isinstance(extremes, dict):
            if symbol_key in extremes:
                return extremes[symbol_key]
            if "low" in extremes and "high" in extremes:
                return extremes

        # 2. Flach: "IV_52W_LOW" / "IV_52W_HIGH"
        if template.get("SYMBOL", "").upper() == symbol_key:
            if "IV_52W_LOW" in template and "IV_52W_HIGH" in template:
                return {
                    "low": float(template["IV_52W_LOW"]),
                    "high": float(template["IV_52W_HIGH"]),
                }

    return None


def get_iv_rank(
    *,
    ib,
    symbol: str,
    get_index_contract_callable: Callable[[], Contract],
    logger,
    config: Optional[Any] = None,
) -> Optional[int]:
    """
    Berechnet den IV Rank = (aktuelle IV - Min IV) / (Max IV - Min IV) * 100
    Gibt den IV Rank als ganze Zahl (Integer) zurück.
    """
    try:
        contract = get_index_contract_callable()
        ib.qualifyContracts(contract)

        bars = ib.reqHistoricalData(
            contract,
            endDateTime='',
            durationStr='30 D',
            barSizeSetting='1 day',
            whatToShow='OPTION_IMPLIED_VOLATILITY',
            useRTH=True,
            formatDate=1,
        )

        valid = [b for b in (bars or []) if b.close is not None and b.close > 0]
        if not valid:
            logger.warning(f"Keine validen IV-Daten für {symbol} erhalten")
            return None

        current_iv = valid[-1].close
        extremes = _extract_iv_extremes(config, symbol)

        if extremes and "low" in extremes and "high" in extremes:
            lo_52w, hi_52w = extremes["low"], extremes["high"]
            source_info = "JSON-Calibration"
        else:
            closes = [b.close for b in valid]
            lo_52w, hi_52w = min(closes), max(closes)
            source_info = "API-Fallback"

        if hi_52w <= lo_52w:
            logger.warning(f"Ungültige IV-Spanne für {symbol} (lo={lo_52w}, hi={hi_52w})")
            return None

        # Als Integer runden
        iv_rank = int(round((current_iv - lo_52w) / (hi_52w - lo_52w) * 100.0))

        logger.info(
            f"{symbol} IV Rank ({source_info}): {iv_rank} | "
            f"current={current_iv:.4f} ({current_iv*100:.2f}%) | "
            f"52W-lo={lo_52w:.4f} 52W-hi={hi_52w:.4f}"
        )

        return iv_rank

    except Exception as e:
        logger.error(f"Fehler bei IV-Rank-Berechnung für {symbol}: {e}", exc_info=True)
        return None

def diagnose_iv_history(
    *,
    ib,
    symbol: str,
    get_index_contract_callable: Callable[[], Contract],
    logger,
    config: Optional[Any] = None,
):
    """Diagnose-Funktion zum manuellen Testen des IV Ranks via tools/diagnose_iv.py."""
    logger.info(f"=== Starte IV-Diagnose für {symbol} ===")

    try:
        contract = get_index_contract_callable()
        ib.qualifyContracts(contract)

        bars = ib.reqHistoricalData(
            contract,
            endDateTime='',
            durationStr='1 Y',
            barSizeSetting='1 day',
            whatToShow='OPTION_IMPLIED_VOLATILITY',
            useRTH=True,
            formatDate=1,
        )

        valid = [b for b in (bars or []) if b.close is not None and b.close > 0]
        if not valid:
            logger.error("Keine IV-Daten von IB API empfangen")
            return

        current_iv = valid[-1].close

        # 1. Reine API-Spanne (365 Tage)
        closes = [b.close for b in valid]
        lows = [b.low for b in valid if b.low is not None and b.low > 0]
        highs = [b.high for b in valid if b.high is not None and b.high > 0]

        api_lo = min(lows + closes) if lows else min(closes)
        api_hi = max(highs + closes) if highs else max(closes)
        api_rank = (current_iv - api_lo) / (api_hi - api_lo) * 100.0 if api_hi > api_lo else 0.0

        logger.info(
            f"[API UNMODIFIED]  bars={len(valid)} | current={current_iv*100:.2f}% | "
            f"lo={api_lo*100:.2f}% hi={api_hi*100:.2f}% -> IV Rank = {api_rank:.1f}%"
        )

        # 2. Kalibrierte Spanne aus Konfiguration
        extremes = _extract_iv_extremes(config, symbol)
        if extremes and "low" in extremes and "high" in extremes:
            json_lo, json_hi = extremes["low"], extremes["high"]
            json_rank = int(round((current_iv - json_lo) / (json_hi - json_lo) * 100.0)) if json_hi > json_lo else 0

            logger.info(
                f"[JSON CALIBRATED] current={current_iv*100:.2f}% | "
                f"lo={json_lo*100:.2f}% hi={json_hi*100:.2f}% -> IV Rank = {json_rank} (MATCH TWS)"
            )
        else:
            logger.warning(f"Keine Kalibrierungswerte für {symbol} in trade_templates.json gefunden.")

    except Exception as e:
        logger.error(f"Fehler bei der IV-Diagnose: {e}", exc_info=True)

    logger.info("=== IV-Diagnose Beendet ===")