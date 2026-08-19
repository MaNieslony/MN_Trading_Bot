# market/index_metadata.py

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class IndexMetadata:
    """
    Conceptual metadata for an index.

    IMPORTANT:
    - primary_exchange = index issuer / listing venue
    - NOT an execution exchange
    """
    symbol: str
    primary_exchange: str
    currency: str = "USD"
    sec_type: str = "IND"   # IBKR security type for indices


# ----------------------------------------------------------------------
# INDEX REGISTRY
# ----------------------------------------------------------------------

INDEX_METADATA: Dict[str, IndexMetadata] = {
    # S&P 500 Index
    "SPX": IndexMetadata(
        symbol="SPX",
        primary_exchange="CBOE",
    ),

    # Volatility Index
    "VIX": IndexMetadata(
        symbol="VIX",
        primary_exchange="CBOE",
    ),

    # Nasdaq 100 Index
    "NDX": IndexMetadata(
        symbol="NDX",
        primary_exchange="NASDAQ",
    ),

    # Russell 2000 Index
    "RUT": IndexMetadata(
        symbol="RUT",
        primary_exchange="CBOE",
    ),
}