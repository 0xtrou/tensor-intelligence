"""Risk scoring for Bittensor subnet investment decisions."""

from dataclasses import dataclass, field
from typing import List
import numpy as np
from src.models.subnet import Subnet
from src.models.flow_snapshot import FlowSnapshot


@dataclass
class RiskScore:
    """Result of risk analysis."""

    total: float  # 0-100, where 100 = safest
    breakdown: dict = field(default_factory=dict)
    flags: list = field(default_factory=list)


class RiskScorer:
    """Scores investment risk for Bittensor subnets."""

    def score(self, subnet: Subnet, snapshots: List[FlowSnapshot]) -> RiskScore:
        """Score risk 0-100 (100 = safest).

        Factors:
        - Flow volatility (high volatility = risky)
        - Liquidity depth (shallow = risky)
        - Emission concentration risk
        - Historical flow crashes
        - Systemic risk proxies (emission_share too high or too low)
        """
        breakdown = {}
        flags = []

        if not snapshots:
            return RiskScore(total=50.0, breakdown={}, flags=["Insufficient data"])

        # Flow volatility score (low volatility = safe)
        flow_vol = self._score_flow_volatility(snapshots)
        breakdown["flow_volatility"] = flow_vol
        if flow_vol < 30:
            flags.append("High flow volatility")

        # Liquidity score
        liquidity = self._score_liquidity(subnet)
        breakdown["liquidity"] = liquidity
        if liquidity < 30:
            flags.append("Shallow liquidity - high slippage risk")

        # Emission sustainability
        emission = self._score_emission_sustainability(subnet)
        breakdown["emission_sustainability"] = emission

        # Concentration risk
        concentration = self._score_concentration_risk(subnet)
        breakdown["concentration"] = concentration

        # Historical crash detection
        crash = self._score_crash_risk(snapshots)
        breakdown["crash_risk"] = crash
        if crash < 30:
            flags.append("Recent flow crash detected")

        # Weighted total (all dimensions equally weighted for now)
        weights = {
            "flow_volatility": 0.25,
            "liquidity": 0.25,
            "emission_sustainability": 0.20,
            "concentration": 0.15,
            "crash_risk": 0.15,
        }
        total = sum(breakdown[k] * weights[k] for k in weights)
        total = max(0.0, min(100.0, total))

        return RiskScore(total=total, breakdown=breakdown, flags=flags)

    def _score_flow_volatility(self, snapshots: List[FlowSnapshot]) -> float:
        """Score flow stability. High volatility = low score (risky)."""
        if len(snapshots) < 5:
            return 50.0

        flows = [s.flow_ema for s in snapshots]
        mean_flow = np.mean(flows)

        if mean_flow == 0:
            return 50.0  # Can't measure volatility of zero

        # Coefficient of variation (lower = more stable)
        cv = np.std(flows) / abs(mean_flow)

        if cv < 0.1:
            return 90.0  # Very stable
        elif cv < 0.3:
            return 70.0
        elif cv < 0.5:
            return 50.0
        elif cv < 1.0:
            return 30.0
        else:
            return 10.0  # Extremely volatile

    def _score_liquidity(self, subnet: Subnet) -> float:
        """Score liquidity depth. Shallow = low score."""
        if not subnet.market_cap or subnet.market_cap == 0:
            return 50.0

        # Volume / Market Cap ratio (higher = more liquid)
        if subnet.tao_volume_24h and subnet.tao_volume_24h > 0:
            turnover_ratio = subnet.tao_volume_24h / subnet.market_cap
            if turnover_ratio > 0.1:
                return 90.0
            elif turnover_ratio > 0.05:
                return 70.0
            elif turnover_ratio > 0.01:
                return 50.0
            else:
                return 30.0  # Low turnover = illiquid

        # Check liquidity field
        if subnet.liquidity and subnet.market_cap > 0:
            liq_ratio = subnet.liquidity / subnet.market_cap
            if liq_ratio > 0.1:
                return 80.0
            elif liq_ratio > 0.05:
                return 60.0
            elif liq_ratio > 0.01:
                return 40.0
            else:
                return 20.0

        return 50.0  # No data

    def _score_emission_sustainability(self, subnet: Subnet) -> float:
        """Score emission sustainability. Very high or very low emission = risk."""
        emission = subnet.emission_share or 0

        if emission <= 0:
            return 20.0  # No emission = subnet dying
        elif emission < 0.001:  # < 0.1%
            return 40.0  # Very low emission
        elif emission < 0.01:  # < 1%
            return 60.0
        elif emission < 0.05:  # < 5%
            return 80.0
        elif emission < 0.15:  # < 15%
            return 70.0  # High emission but sustainable
        else:
            return 40.0  # Very high emission = possible inflation pressure

    def _score_concentration_risk(self, subnet: Subnet) -> float:
        """Score concentration risk. Few miners/validators = risky."""
        score = 100.0

        if subnet.active_miners and subnet.active_miners < 5:
            score -= 50.0  # Very concentrated
        elif subnet.active_miners and subnet.active_miners < 10:
            score -= 25.0

        if subnet.active_validators and subnet.active_validators < 3:
            score -= 30.0
        elif subnet.active_validators and subnet.active_validators < 5:
            score -= 15.0

        return max(0.0, min(100.0, score))

    def _score_crash_risk(self, snapshots: List[FlowSnapshot]) -> float:
        """Detect recent flow crashes. Returns low score if crash detected."""
        if len(snapshots) < 10:
            return 50.0

        recent = [s.flow_ema for s in snapshots[-10:]]

        # Check for sudden drops (>50% decline in recent period)
        peak = max(recent)
        current = recent[-1]

        if peak > 0 and current < peak * 0.5:
            return 10.0  # Crash detected
        elif peak > 0 and current < peak * 0.7:
            return 30.0  # Significant decline
        elif peak > 0 and current < peak * 0.85:
            return 60.0
        else:
            return 80.0  # Stable
