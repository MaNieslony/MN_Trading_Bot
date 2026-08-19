# trade/metrics.py
from dataclasses import dataclass
from typing import Optional


@dataclass
class TradeMetrics:
    """
    Container for all optional analytics / reporting metrics
    collected during trade selection & pricing.
    """

    # Selection metrics
    short_delta: Optional[float] = None
    short_leg_mid: Optional[float] = None

    # Pricing metrics (combo-level)
    combo_mid: Optional[float] = None
    combo_natural: Optional[float] = None

    # PBW-specific (optional, future-safe)
    pbw_lower_wing: Optional[int] = None
    pbw_upper_wing: Optional[int] = None