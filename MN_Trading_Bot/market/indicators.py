# market/indicators.py

from typing import List, Optional


def calculate_rsi(
    *,
    closes: List[float],
    period: int,
) -> Optional[float]:
    """
    Calculate RSI using Wilder's smoothing.
    Symbol-agnostic indicator logic.
    """

    if not closes or len(closes) < period + 1:
        return None

    # Price deltas
    deltas = [closes[i] - closes[i - 1] for i in range(1, len(closes))]

    gains = [d if d > 0 else 0.0 for d in deltas]
    losses = [abs(d) if d < 0 else 0.0 for d in deltas]

    # Initial averages
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    # Wilder smoothing
    for i in range(period, len(deltas)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period

    if avg_loss == 0:
        return 100.0

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return round(rsi, 2)

def calculate_sma(
    *,
    closes: List[float],
    period: int,
) -> Optional[float]:
    """
    Calculate Simple Moving Average (SMA).
    """
    if not closes or len(closes) < period:
        return None

    return round(sum(closes[-period:]) / period, 2)