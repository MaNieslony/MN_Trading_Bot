# market/contracts.py

from typing import Optional
from ib_insync import Option, Contract, Index
from market.index_metadata import INDEX_METADATA

def get_option_conid(
    *,
    ib,
    symbol: str,
    expiry: str,
    strike: float,
    right: str,
    trading_class: Optional[str],
    logger,
    debug_mode: bool,
) -> Optional[Contract]:
    """
    Qualify an option contract using IB reqContractDetails.

    Drop-in extraction of Bot._get_option_conid.
    """
    try:
        opt = Option(
            symbol=symbol,
            lastTradeDateOrContractMonth=expiry,
            strike=float(strike),
            right=right,
            exchange='SMART',
            currency='USD',
            multiplier='100',
            tradingClass='SPXW'
        )

        # Override trading class if provided
        if trading_class:
            opt.tradingClass = trading_class

        contract_details = ib.reqContractDetails(opt)

        if not contract_details:
            if debug_mode:
                logger.debug(
                    f"No contract details found for {strike}{right} expiry {expiry}"
                )
            return None

        # Return first fully-qualified contract
        return contract_details[0].contract

    except Exception as e:
        if debug_mode:
            logger.debug(
                f"Error getting contract details for {strike}{right}: {e}"
            )
        return None

def get_index_contract(symbol: str) -> Index:
    """
    Build an IB index contract using central index metadata.

    The exchange here refers to the index issuer / listing venue,
    not order execution routing.
    """
    meta = INDEX_METADATA.get(symbol)

    if not meta:
        raise ValueError(f"No index metadata configured for symbol '{symbol}'")

    return Index(
        symbol=meta.symbol,
        exchange=meta.primary_exchange,
        currency=meta.currency,
    )
