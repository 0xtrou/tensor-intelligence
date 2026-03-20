"""Flow trend detection using EMA analysis."""

from dataclasses import dataclass
from typing import List
import numpy as np
from src.models.flow_snapshot import FlowSnapshot


@dataclass
class FlowAnalysis:
    """Result of flow trend analysis."""

    current_flow: float
    flow_momentum: float
    trend: str  # RISING, STEADY, FALLING, SURGING, REVERSING
    signal: str  # FLOW_SURGE, FLOW_STEADY, FLOW_PEAK, FLOW_REVERSAL, FLOW_NEGATIVE, FLOW_NEUTRAL
    flow_score: float  # 0-100, how bullish the flow is


class FlowDetector:
    """Analyzes flow trends from historical snapshots using EMAs."""

    def __init__(self):
        self.ema_short = 3  # 3-day EMA
        self.ema_medium = 7  # 7-day EMA
        self.ema_long = 30  # 30-day EMA

    def analyze(self, snapshots: List[FlowSnapshot]) -> FlowAnalysis:
        """Analyze flow trends from historical snapshots.

        Args:
            snapshots: List of FlowSnapshot ordered by timestamp ascending

        Returns:
            FlowAnalysis with current flow, momentum, trend, signal, and score
        """
        if not snapshots:
            return FlowAnalysis(
                current_flow=0.0,
                flow_momentum=0.0,
                trend="UNKNOWN",
                signal="NO_DATA",
                flow_score=0.0,
            )

        # Extract flow values (use flow_ema field)
        flows = [s.flow_ema for s in snapshots]

        # Calculate EMAs
        ema_short_vals = self._calculate_ema(flows, self.ema_short)
        ema_medium_vals = self._calculate_ema(flows, self.ema_medium)
        ema_long_vals = self._calculate_ema(flows, self.ema_long)

        # Get latest values
        current_flow = flows[-1] if flows else 0.0
        current_short = ema_short_vals[-1] if ema_short_vals else current_flow
        current_medium = ema_medium_vals[-1] if ema_medium_vals else current_flow
        current_long = ema_long_vals[-1] if ema_long_vals else current_flow

        # Calculate momentum (slope of short EMA)
        momentum = self._calculate_slope(
            ema_short_vals[-min(10, len(ema_short_vals)) :]
        )

        # Normalize momentum to 0-100 scale
        # Typical slope range: -1e12 to 1e12 (rao units per snapshot)
        # Normalize: (momentum - min) / (max - min) where typical max ~ 2e12
        normalized_momentum = min(100.0, max(0.0, (momentum + 1e12) / 2e12 * 100))

        # Determine trend
        trend = self._determine_trend(
            current_short, current_medium, current_long, ema_short_vals, ema_medium_vals
        )

        # Determine signal
        signal = self._detect_signal(
            flows, ema_short_vals, ema_medium_vals, ema_long_vals
        )

        # Calculate flow score (0-100)
        flow_score = self._calculate_flow_score(
            current_flow, normalized_momentum, trend, signal, ema_short_vals
        )

        return FlowAnalysis(
            current_flow=current_flow,
            flow_momentum=normalized_momentum,
            trend=trend,
            signal=signal,
            flow_score=flow_score,
        )

    def _calculate_ema(self, values: List[float], span: int) -> List[float]:
        """Calculate Exponential Moving Average.

        Args:
            values: List of numeric values
            span: EMA period (e.g., 3, 7, 30)

        Returns:
            List of EMA values (same length as input)
        """
        if not values:
            return []

        alpha = 2.0 / (span + 1)
        ema = [values[0]]

        for i in range(1, len(values)):
            ema.append(alpha * values[i] + (1 - alpha) * ema[-1])

        return ema

    def _calculate_slope(self, values: List[float]) -> float:
        """Calculate linear regression slope of recent values.

        Args:
            values: List of numeric values (typically last 10 EMA points)

        Returns:
            Slope (change per period)
        """
        if len(values) < 2:
            return 0.0

        n = len(values)
        x = np.arange(n)
        y = np.array(values)

        # Linear regression: y = mx + b
        x_mean = np.mean(x)
        y_mean = np.mean(y)

        numerator = np.sum((x - x_mean) * (y - y_mean))
        denominator = np.sum((x - x_mean) ** 2)

        if denominator == 0:
            return 0.0

        slope = numerator / denominator
        return float(slope)

    def _determine_trend(
        self,
        short: float,
        medium: float,
        long: float,
        short_vals: List[float],
        medium_vals: List[float],
    ) -> str:
        """Determine the flow trend based on EMA relationships."""
        # Check if we have enough data
        if not short_vals or not medium_vals:
            return "UNKNOWN"

        # EMA ordering
        if short > medium > long:
            # Strong uptrend
            # Check if momentum is accelerating
            if (
                len(short_vals) >= 3
                and short_vals[-1] > short_vals[-2] > short_vals[-3]
            ):
                return "SURGING"
            return "RISING"
        elif short < medium < long:
            # Downtrend
            if (
                len(short_vals) >= 3
                and short_vals[-1] < short_vals[-2] < short_vals[-3]
            ):
                return "FALLING"
            return "DECLINING"
        else:
            # Mixed signals - check for recent crossover
            if len(short_vals) >= 2 and len(medium_vals) >= 2:
                if (
                    short_vals[-2] <= medium_vals[-2]
                    and short_vals[-1] > medium_vals[-1]
                ):
                    return "REVERSING"  # Bullish crossover
                elif (
                    short_vals[-2] >= medium_vals[-2]
                    and short_vals[-1] < medium_vals[-1]
                ):
                    return "REVERSING"  # Bearish crossover
            return "STEADY"

    def _detect_signal(
        self,
        flows: List[float],
        short_vals: List[float],
        medium_vals: List[float],
        long_vals: List[float],
    ) -> str:
        """Detect specific flow signals based on rules."""
        if len(flows) < 7:
            return "INSUFFICIENT_DATA"

        current_flow = flows[-1]
        recent_flows = flows[-7:]  # Last 7 snapshots (~1.75 days at 15min intervals)

        # FLOW_NEGATIVE: flow < 0 for 7+ consecutive snapshots
        if all(f < 0 for f in recent_flows):
            return "FLOW_NEGATIVE"

        # Need positive flow for other signals
        if current_flow <= 0:
            return "FLOW_NEUTRAL"

        # FLOW_SURGE: 3d EMA slope > 2x the 30d average slope AND current flow > 0
        if len(short_vals) >= 10 and len(long_vals) >= 10:
            recent_short_slope = self._calculate_slope(short_vals[-10:])
            long_slope_avg = (
                self._calculate_slope(long_vals[-30:]) if len(long_vals) >= 30 else 0
            )

            if recent_short_slope > 2 * abs(long_slope_avg) and recent_short_slope > 0:
                return "FLOW_SURGE"

        # FLOW_STEADY: flow positive for 14+ consecutive snapshots (~3.5 days)
        if len(flows) >= 14 and all(f > 0 for f in flows[-14:]):
            return "FLOW_STEADY"

        # FLOW_PEAK: 7d EMA at 7-day high but 3d EMA slope declining
        if len(short_vals) >= 7 and len(medium_vals) >= 7:
            short_recent = short_vals[-7:]
            if max(short_recent) == short_vals[-1]:
                short_slope = self._calculate_slope(short_vals[-5:])
                if short_slope < 0:
                    return "FLOW_PEAK"

        # FLOW_REVERSAL: 3d EMA crosses below 7d EMA from above
        if len(short_vals) >= 2 and len(medium_vals) >= 2:
            if short_vals[-2] > medium_vals[-2] and short_vals[-1] < medium_vals[-1]:
                return "FLOW_REVERSAL"

        return "FLOW_NEUTRAL"

    def _calculate_flow_score(
        self,
        current_flow: float,
        normalized_momentum: float,
        trend: str,
        signal: str,
        short_vals: List[float],
    ) -> float:
        """Calculate overall flow score 0-100."""
        score = 0.0

        # Base score from momentum (0-50 points)
        score += normalized_momentum * 0.5

        # Signal bonuses
        signal_bonuses = {
            "FLOW_SURGE": 30.0,
            "FLOW_STEADY": 20.0,
            "FLOW_REVERSAL": -10.0,  # Penalty for reversal (uncertainty)
            "FLOW_PEAK": -5.0,  # Small penalty (possible top)
            "FLOW_NEGATIVE": -50.0,
            "FLOW_NEUTRAL": 0.0,
        }
        score += signal_bonuses.get(signal, 0.0)

        # Trend bonuses
        trend_bonuses = {
            "SURGING": 20.0,
            "RISING": 10.0,
            "STEADY": 5.0,
            "REVERSING": 0.0,
            "FALLING": -10.0,
            "DECLINING": -20.0,
        }
        score += trend_bonuses.get(trend, 0.0)

        # Flow magnitude bonus (if flow is large positive)
        if current_flow > 1e12:  # > 1T rao
            score += 10.0
        elif current_flow > 1e11:  # > 100B rao
            score += 5.0

        # Clamp to 0-100
        return min(100.0, max(0.0, score))
