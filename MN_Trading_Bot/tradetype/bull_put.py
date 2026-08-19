# tradetype/bull_put.py

from typing import Dict, List, Optional, Tuple


class BullPutTradeType:
    """
    Bull Put Spread trade type

    Responsibilities:
    - Select short and long put strikes
    - Stateless (no sizing, no execution, no scheduling)

    """
    display_name = "Bull-Put"

    def __init__(
        self,
        leg1_target: float,
        leg1_target_type: str,
        leg2_target: float,
        leg2_target_type: str,
        logger=None,
    ):
        self.leg1_target = leg1_target
        self.leg1_target_type = leg1_target_type
        self.leg2_target = leg2_target
        self.leg2_target_type = leg2_target_type
        self.logger = logger

    def select_strikes(
        self,
        *,
        expiry: str = None,               # bewusst ignoriert
        strikes: List[float],
        deltas: Dict[float, float],
        underlying_price: float = None,   # bewusst ignoriert
        **_,                               # future‑proof
    ) -> Optional[Tuple[float, float]]:

        if not strikes or not deltas:
            return None

        # ---------------------------
        # Short Put (Delta-based)
        # ---------------------------
        short_strike = None

        if self.leg1_target_type.lower() == "delta":
            # Allow both 0.45 and 45 to mean "45-delta"
            raw_target = abs(self.leg1_target)

            if raw_target > 1:
                target = raw_target / 100.0
            else:
                target = raw_target

            if self.logger:
                self.logger.debug(
                    f"Delta target normalized: raw={self.leg1_target} -> {target:.4f}"
                )

            for strike, delta in sorted(
                deltas.items(),
                key=lambda x: abs(abs(x[1]) - target),
            ):
                if strike in strikes:
                    short_strike = strike
                    break

        if short_strike is None:
            if self.logger:
                self.logger.warning("No valid short strike found")
            return None

        # ---------------------------
        # Long Put (Offset)
        # ---------------------------
        if self.leg2_target_type.lower() == "strikeoffset_leg1":
            long_strike = short_strike + self.leg2_target
        else:
            long_strike = self.leg2_target

        if long_strike >= short_strike:
            if self.logger:
                self.logger.warning(
                    f"Invalid Bull Put: long {long_strike} >= short {short_strike}"
                )
            return None

        if long_strike not in strikes:
            if self.logger:
                self.logger.warning(
                    f"Long strike {long_strike} not in option chain"
                )
            return None

        return short_strike, long_strike