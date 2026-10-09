# tools/diagnose_iv.py
import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ib_insync import IB
from config.loader import load_broker_settings, load_trade_templates
from market.contracts import get_index_contract
from market.market_data import diagnose_iv_history

SYMBOL = "RUT"
CLIENT_ID = 997

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("IVDiag")

cfg = load_broker_settings()
template_cfg = load_trade_templates()  # <-- LÄDT DIE trade_templates.json

port = cfg["IB_PORT_PAPER"] if cfg["USE_PAPER_TRADING"] else cfg["IB_PORT_LIVE"]

ib = IB()
try:
    ib.connect(cfg["IB_HOST"], int(port), clientId=CLIENT_ID, timeout=30)
    logger.info(f"Verbunden mit {cfg['IB_HOST']}:{port}")

    diagnose_iv_history(
        ib=ib,
        symbol=SYMBOL,
        get_index_contract_callable=lambda: get_index_contract(SYMBOL),
        logger=logger,
        config=template_cfg,
    )
finally:
    if ib.isConnected():
        ib.disconnect()