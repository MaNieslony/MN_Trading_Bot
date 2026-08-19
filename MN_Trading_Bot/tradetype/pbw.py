from __future__ import annotations
from typing import List, Optional, Tuple
from trade.strike_targets import select_nearest_atm_strike,select_percentage_otm_strike

class PutBrokenWingTradeType:
    display_name = "Put Broken Wing"

    def __init__(
        self,
        *,
        leg1_target: float,
        leg1_target_type: str,
        leg2_target: float,
        leg2_target_type: str,
        leg3_target: float,
        leg3_target_type: str,
        logger,
    ):
        self.leg1_target = float(leg1_target)
        self.leg1_target_type = (leg1_target_type or "").strip()
        self.leg2_target = float(leg2_target)
        self.leg2_target_type = (leg2_target_type or "").strip()
        self.leg3_target = float(leg3_target)
        self.leg3_target_type = (leg3_target_type or "").strip()
        self.logger = logger

    @staticmethod
    def _estimate_strike_step(strikes: List[float]) -> float:
        s = sorted(set(float(x) for x in strikes))
        if len(s) < 2:
            return 0.0
        diffs = [s[i + 1] - s[i] for i in range(len(s) - 1)]
        diffs = [d for d in diffs if d > 0]
        return min(diffs) if diffs else 0.0

    @staticmethod
    def _nearest(strikes: List[float], target: float) -> float:
        return float(min(strikes, key=lambda s: abs(float(s) - float(target))))

    def select_strikes(
        self,
        *,
        strikes: List[float],
        underlying_price: float,
        deltas=None,
        expiry=None,
    ) -> Optional[Tuple[float, float, float]]:

        if not strikes:
            return None

        # ------------------------------------------------------------------------
        # LEG1 selection
        # Supported:
        #   - NearestATM
        #   - PercentageOTM
        # ------------------------------------------------------------------------
        if self.leg1_target_type == "NearestATM":
            leg1 = select_nearest_atm_strike(strikes, underlying_price)
            if leg1 is None:
                self.logger.warning("PBW: failed to select ATM strike")
                return None

            self.logger.debug(
                f"PBW LEG1 NearestATM selected | underlying={underlying_price:.2f}, "
                f"leg1={leg1:.0f}, distance={leg1 - underlying_price:+.2f} pts"
            )

        elif self.leg1_target_type == "PercentageOTM":
            leg1 = select_percentage_otm_strike(
                strikes,
                underlying_price,
                self.leg1_target,
            )

            if leg1 is None:
                self.logger.warning("PBW: failed to select PercentageOTM strike")
                return None

            actual_pct = ((leg1 - underlying_price) / underlying_price) * 100.0

            self.logger.debug(
                f"PBW LEG1 PercentageOTM selected | underlying={underlying_price:.2f}, "
                f"target_pct={self.leg1_target:+.2f}%, "
                f"leg1={leg1:.0f}, actual_pct={actual_pct:+.2f}%"
            )

        else:
            self.logger.error(f"PBW: Unsupported LEG1_TARGET_TYPE={self.leg1_target_type}")
            return None

        # --- LEG2/LEG3 must be offsets from leg1 ---
        if self.leg2_target_type.lower() != "strikeoffset_leg1":
            self.logger.error("PBW: LEG2_TARGET_TYPE must be StrikeOffset_Leg1")
            return None
        if self.leg3_target_type.lower() != "strikeoffset_leg1":
            self.logger.error("PBW: LEG3_TARGET_TYPE must be StrikeOffset_Leg1")
            return None

        step = self._estimate_strike_step(strikes) or 5.0  # SPX typ. 5
        leg2_target = leg1 + self.leg2_target
        leg3_target = leg1 + self.leg3_target

        smin, smax = float(min(strikes)), float(max(strikes))

        # Hard guard: target must be inside available strike range
        if leg2_target < smin or leg3_target > smax:
            self.logger.warning(
                f"PBW: target strikes outside available range "
                f"(range={smin:.0f}..{smax:.0f}, "
                f"leg2_target={leg2_target:.0f}, leg3_target={leg3_target:.0f}). "
                f"Increase SPX strike window in option_chain filtering."
            )
            return None

        # Choose nearest strikes to the targets with correct direction constraints
        lower_candidates = [s for s in strikes if float(s) < float(leg1)]
        upper_candidates = [s for s in strikes if float(s) > float(leg1)]

        if not lower_candidates or not upper_candidates:
            self.logger.warning("PBW: insufficient strikes around LEG1")
            return None

        leg2 = self._nearest(lower_candidates, leg2_target)
        leg3 = self._nearest(upper_candidates, leg3_target)

        # Extra sanity: ensure we didn't land far away from target
        if abs(leg2 - leg2_target) > step * 1.1 or abs(leg3 - leg3_target) > step * 1.1:
            self.logger.warning(
                f"PBW: nearest strikes too far from targets "
                f"(leg2={leg2:.0f} vs {leg2_target:.0f}, "
                f"leg3={leg3:.0f} vs {leg3_target:.0f}, step≈{step}). "
                f"Increase strike window."
            )
            return None

        if not (leg2 < leg1 < leg3):
            self.logger.warning(
                f"PBW invalid strike order: {leg2} < {leg1} < {leg3} not satisfied"
            )
            return None

        self.logger.debug(
            f"PBW targets: leg2_target={leg2_target:.0f}, leg3_target={leg3_target:.0f} | "
            f"selected: {leg2:.0f}/{leg1:.0f}/{leg3:.0f}"
        )

        return float(leg1), float(leg2), float(leg3)