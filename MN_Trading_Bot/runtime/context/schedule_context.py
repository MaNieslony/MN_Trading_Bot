# runtime/context/schedule_context.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict


@dataclass(frozen=True)
class ScheduleContext:
    """
    Build runtime-ready bot attributes from a raw schedule dict.

    This is a 1:1 extraction of the schedule parsing / normalization logic
    that previously lived in Bot.__init__ (bot.py).
    """
    trade_cfg: Dict[str, Any]

    def apply(self, bot) -> None:
        cfg = self.trade_cfg

        # ------------------------------------------------------------
        # Identity / schedule metadata
        # ------------------------------------------------------------
        bot.trade_cfg = cfg
        bot.STRATEGY_NAME = cfg["NAME"]
        bot.logger.info(f"✅ Selected schedule: {bot.STRATEGY_NAME}")

        bot.TRADE_TYPE = cfg.get("TRADE_TYPE")
        if not bot.TRADE_TYPE:
            raise ValueError(
                f"❌ Missing TRADE_TYPE in template for schedule '{cfg.get('NAME')}'"
            )

        # ------------------------------------------------------------
        # Apply selected schedule config (flat / legacy compatible)
        # ------------------------------------------------------------
        bot.SYMBOL = cfg["SYMBOL"]
        bot.COMMISSION_PER_CONTRACT = cfg["COMMISSION_PER_CONTRACT"]

        bot.LEG1_ACTION = cfg["LEG1_ACTION"]
        bot.LEG1_PUT_CALL = cfg["LEG1_PUT_CALL"]
        bot.LEG1_QTY = cfg["LEG1_QTY"]
        bot.LEG1_TARGET = cfg["LEG1_TARGET"]
        bot.LEG1_TARGET_TYPE = cfg["LEG1_TARGET_TYPE"]
        bot.LEG1_DTE = cfg["LEG1_DTE"]

        bot.LEG2_ACTION = cfg["LEG2_ACTION"]
        bot.LEG2_PUT_CALL = cfg["LEG2_PUT_CALL"]
        bot.LEG2_QTY = cfg["LEG2_QTY"]
        bot.LEG2_TARGET = cfg["LEG2_TARGET"]
        bot.LEG2_TARGET_TYPE = cfg["LEG2_TARGET_TYPE"]
        bot.LEG2_DTE = cfg["LEG2_DTE"]

        bot.MIN_SWEEP_PRICE = cfg["MIN_SWEEP_PRICE"]
        bot.MAX_SWEEP_PRICE = cfg["MAX_SWEEP_PRICE"]
        # Normalize credit range (templates are negative; ensure MIN <= MAX)
        bot.MIN_SWEEP_PRICE, bot.MAX_SWEEP_PRICE = sorted(
            [float(bot.MIN_SWEEP_PRICE), float(bot.MAX_SWEEP_PRICE)]
        )
        bot.MAX_SWEEP_ATTEMPTS = cfg["MAX_SWEEP_ATTEMPTS"]
        bot.SWEEP_WAIT_SECONDS = cfg["SWEEP_WAIT_SECONDS"]
        bot.SWEEP_STEP = cfg["SWEEP_STEP"]

        # ------------------------------------------------------------
        # Optional NDX scan parameters (present only in some templates)
        # ------------------------------------------------------------
        bot.STRIKE_UPPER_OFFSET = cfg.get("STRIKE_UPPER_OFFSET")
        bot.STRIKE_LOWER_OFFSET = cfg.get("STRIKE_LOWER_OFFSET")
        bot.STRIKE_STEP = cfg.get("STRIKE_STEP")

        bot.MAX_STRIKE_SCAN = cfg.get("MAX_STRIKE_SCAN")
        if bot.MAX_STRIKE_SCAN is None:
            bot.MAX_STRIKE_SCAN = 40

        bot.DELTA_TARGET_OFFSET = cfg.get("DELTA_TARGET_OFFSET")
        bot.DELTA_MAX_ABS = cfg.get("DELTA_MAX_ABS")
        bot.DELTA_RESCAN_EXPANSION = cfg.get("DELTA_RESCAN_EXPANSION")
        bot.SHORT_LEG_MID_MIN = cfg.get("SHORT_LEG_MID_MIN")
        bot.SHORT_LEG_MID_MAX = cfg.get("SHORT_LEG_MID_MAX")
        bot.SHORT_LEG_MID_EXPANSION = cfg.get("SHORT_LEG_MID_EXPANSION")
        bot.MAX_RESCAN_ATTEMPTS = cfg.get("MAX_RESCAN_ATTEMPTS")

        # ------------------------------------------------------------
        # Optional 3-leg scan parameters (present only in some templates)
        # ------------------------------------------------------------
        bot.LEG3_ACTION = cfg.get("LEG3_ACTION")
        bot.LEG3_PUT_CALL = cfg.get("LEG3_PUT_CALL")
        bot.LEG3_QTY = cfg.get("LEG3_QTY")
        bot.LEG3_TARGET = cfg.get("LEG3_TARGET")
        bot.LEG3_TARGET_TYPE = cfg.get("LEG3_TARGET_TYPE")
        bot.LEG3_DTE = cfg.get("LEG3_DTE")

        # ------------------------------------------------------------
        # Normalize optional 3-leg parameters (PBW / Iron Condor safety)
        # ------------------------------------------------------------
        if bot.LEG3_QTY is None:
            bot.LEG3_QTY = 0
        else:
            try:
                bot.LEG3_QTY = int(bot.LEG3_QTY)
                if bot.LEG3_QTY <= 0:
                    raise ValueError
            except Exception:
                raise ValueError(
                    f"❌ LEG3_QTY must be a positive integer "
                    f"(schedule={bot.STRATEGY_NAME}, value={cfg.get('LEG3_QTY')})"
                )

        if bot.LEG3_TARGET is not None:
            try:
                bot.LEG3_TARGET = float(bot.LEG3_TARGET)
            except Exception:
                raise ValueError(
                    f"❌ LEG3_TARGET must be numeric "
                    f"(schedule={bot.STRATEGY_NAME}, value={cfg.get('LEG3_TARGET')})"
                )

        if bot.LEG3_QTY > 0:
            if not bot.LEG3_ACTION or not bot.LEG3_PUT_CALL:
                raise ValueError(
                    f"❌ LEG3_ACTION and LEG3_PUT_CALL required for PBW/Iron Condor "
                    f"(schedule={bot.STRATEGY_NAME})"
                )

        # ------------------------------------------------------------
        # Optional 4-leg scan parameters (present only for Iron Condor)
        # ------------------------------------------------------------
        bot.LEG4_ACTION = cfg.get("LEG4_ACTION")
        bot.LEG4_PUT_CALL = cfg.get("LEG4_PUT_CALL")
        bot.LEG4_QTY = cfg.get("LEG4_QTY")
        bot.LEG4_TARGET = cfg.get("LEG4_TARGET")
        bot.LEG4_TARGET_TYPE = cfg.get("LEG4_TARGET_TYPE")
        bot.LEG4_DTE = cfg.get("LEG4_DTE")

        if bot.LEG4_QTY is None:
            bot.LEG4_QTY = 0
        else:
            try:
                bot.LEG4_QTY = int(bot.LEG4_QTY)
                if bot.LEG4_QTY <= 0:
                    raise ValueError
            except Exception:
                raise ValueError(
                    f"❌ LEG4_QTY must be a positive integer "
                    f"(schedule={bot.STRATEGY_NAME}, value={cfg.get('LEG4_QTY')})"
                )

        if bot.LEG4_TARGET is not None:
            try:
                bot.LEG4_TARGET = float(bot.LEG4_TARGET)
            except Exception:
                raise ValueError(
                    f"❌ LEG4_TARGET must be numeric "
                    f"(schedule={bot.STRATEGY_NAME}, value={cfg.get('LEG4_TARGET')})"
                )

        if bot.LEG4_QTY > 0:
            if not bot.LEG4_ACTION or not bot.LEG4_PUT_CALL:
                raise ValueError(
                    f"❌ LEG4_ACTION and LEG4_PUT_CALL required for Iron Condor "
                    f"(schedule={bot.STRATEGY_NAME})"
                )

        # ------------------------------------------------------------
        # Optional RUT Iron Condor steering parameters
        # ------------------------------------------------------------
        bot.IV_RANK_MATRIX = cfg.get("IV_RANK_MATRIX")
        bot.IV_RANK_LOOKBACK_DAYS = cfg.get("IV_RANK_LOOKBACK_DAYS", 365)
        bot.LATE_ENTRY_CUTOFF_ET = cfg.get("LATE_ENTRY_CUTOFF_ET", "12:00:00")
        bot.MIN_SPREAD_WIDTH = cfg.get("MIN_SPREAD_WIDTH")
        bot.MAX_SPREAD_WIDTH = cfg.get("MAX_SPREAD_WIDTH")
        bot.PUT_DELTA_WINDOW = cfg.get("PUT_DELTA_WINDOW", 300)
        bot.CALL_DELTA_WINDOW = cfg.get("CALL_DELTA_WINDOW", 300)

        if bot.TRADE_TYPE == "IRON_CONDOR":
            if not bot.IV_RANK_MATRIX:
                raise ValueError(
                    f"❌ IRON_CONDOR requires IV_RANK_MATRIX in template "
                    f"(schedule={bot.STRATEGY_NAME})"
                )
            if bot.MIN_SPREAD_WIDTH is None or bot.MAX_SPREAD_WIDTH is None:
                raise ValueError(
                    f"❌ IRON_CONDOR requires MIN_SPREAD_WIDTH/MAX_SPREAD_WIDTH "
                    f"(schedule={bot.STRATEGY_NAME})"
                )

        # ------------------------------------------------------------
        # Quantity / Position Sizing (from Schedule)
        # ------------------------------------------------------------
        qty_cfg = cfg.get("QUANTITY", {})

        bot.QUANTITY_MODE = qty_cfg.get("MODE", "PremAllocation")

        if "QUANTITY" not in cfg:
            bot.logger.warning(
                "⚠️ No QUANTITY section in schedule – defaulting to PremAllocation"
            )

        if bot.QUANTITY_MODE == "FixedQty":
            bot.FIXED_QTY = int(qty_cfg.get("QTY", 1))
            if bot.FIXED_QTY <= 0:
                raise ValueError(
                    f"❌ FixedQty requires QTY > 0 (schedule={bot.STRATEGY_NAME})"
                )

            bot.ALLOCATION = bot.FIXED_QTY
            bot.MIN_QTY = bot.FIXED_QTY
            bot.MAX_QTY = bot.FIXED_QTY

            bot.logger.info(f"✅ Quantity mode: FixedQty ({bot.FIXED_QTY})")

        elif bot.QUANTITY_MODE == "PremAllocation":
            bot.ALLOCATION = float(qty_cfg.get("ALLOCATION", 0))
            if bot.ALLOCATION <= 0:
                raise ValueError(
                    f"❌ PremAllocation requires ALLOCATION > 0 "
                    f"(schedule={bot.STRATEGY_NAME})"
                )

            bot.MIN_QTY = int(qty_cfg.get("MIN_QTY", 1))
            bot.MAX_QTY = int(qty_cfg.get("MAX_QTY", bot.MIN_QTY))
            bot.FIXED_QTY = None

            bot.logger.info(
                f"✅ Quantity mode: PremAllocation "
                f"(alloc={bot.ALLOCATION}, min={bot.MIN_QTY}, max={bot.MAX_QTY})"
            )
        else:
            raise ValueError(f"❌ Unknown QUANTITY.MODE: {bot.QUANTITY_MODE}")

        # ------------------------------------------------------------
        # Execution / expiration params from schedule
        # ------------------------------------------------------------
        raw_exec_time = str(cfg["EXECUTION_TIME"])
        h, m, s = [int(x) for x in raw_exec_time.split(":")]
        bot.EXECUTION_TIME = datetime.strptime(
            f"{h:02d}:{m:02d}:{s:02d}", "%H:%M:%S"
        ).time()

        bot.EXPIRATION_MINUTES = cfg.get("EXPIRATION_MINUTES", 5)

        # ------------------------------------------------------------
        # Profit Target parameters from trade template
        # ------------------------------------------------------------
        bot.PROFIT_TARGET_ENABLED = bool(cfg.get("PROFIT_TARGET_ENABLED", False))
        bot.PROFIT_TARGET_PCT = float(cfg.get("PROFIT_TARGET_PCT", 50))
        bot.PROFIT_TARGET_ETH = bool(cfg.get("PROFIT_TARGET_ETH", False))

        if bot.PROFIT_TARGET_ENABLED:
            bot.logger.info(
                f"✅ Profit Target enabled: {bot.PROFIT_TARGET_PCT:.0f}% "
                f"(ETH={bot.PROFIT_TARGET_ETH})"
            )
        else:
            bot.logger.debug("ℹ️ Profit Target disabled for this template")