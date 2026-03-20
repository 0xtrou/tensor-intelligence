"""Composite signal generation for investment decisions."""

from dataclasses import dataclass
from typing import List
from src.models.subnet import Subnet
from src.models.flow_snapshot import FlowSnapshot
from .flow_detector import FlowDetector, FlowAnalysis
from .fundamental_scorer import FundamentalScorer, FundamentalScore
from .risk_scorer import RiskScorer, RiskScore


@dataclass
class SignalResult:
    """Complete investment signal with evidence."""

    signal_type: str  # BUY, ACCUMULATE, HOLD, REDUCE, AVOID
    flow_signal: str  # FLOW_SURGE, etc.
    confidence: float  # 0-100
    composite_score: float  # 0-100
    flow_score: float
    fundamental_score: float
    risk_score: float
    evidence: dict
    reasoning: str


class SignalGenerator:
    """Generates composite investment signals from multiple analyses."""

    WEIGHTS = {
        "flow": 0.35,
        "fundamentals": 0.35,
        "trend_alignment": 0.15,
        "risk": 0.15,
    }

    # Signal thresholds from PRODUCT.md
    SIGNAL_THRESHOLDS = {
        "BUY": 70.0,
        "ACCUMULATE": 50.0,
        "HOLD": 30.0,
        "REDUCE": 15.0,
        "AVOID": 0.0,
    }

    def __init__(self):
        self.flow_detector = FlowDetector()
        self.fundamental_scorer = FundamentalScorer()
        self.risk_scorer = RiskScorer()

    def generate(
        self,
        subnet: Subnet,
        snapshots: List[FlowSnapshot],
        flow_analysis: FlowAnalysis | None = None,
        fundamental_score: FundamentalScore | None = None,
        risk_score: RiskScore | None = None,
    ) -> SignalResult:
        """Generate a composite investment signal.

        Args:
            subnet: Subnet model instance
            snapshots: Recent flow snapshots
            flow_analysis: Optional pre-computed flow analysis
            fundamental_score: Optional pre-computed fundamental score
            risk_score: Optional pre-computed risk score

        Returns:
            SignalResult with signal type, scores, evidence, and reasoning
        """
        # Run analyses if not provided
        if flow_analysis is None:
            flow_analysis = self.flow_detector.analyze(snapshots)

        if fundamental_score is None:
            fundamental_score = self.fundamental_scorer.score(subnet, snapshots)

        if risk_score is None:
            risk_score = self.risk_scorer.score(subnet, snapshots)

        # Calculate trend alignment
        trend_alignment = self._calculate_trend_alignment(
            flow_analysis, fundamental_score, risk_score
        )

        # Compute composite score
        composite_score = self._compute_composite_score(
            flow_analysis.flow_score,
            fundamental_score.total,
            trend_alignment,
            risk_score.total,
        )

        # Determine signal type
        signal_type = self._map_score_to_signal(composite_score)

        # Build evidence chain
        evidence = self._build_evidence(
            subnet,
            snapshots,
            flow_analysis,
            fundamental_score,
            risk_score,
            trend_alignment,
        )

        # Generate reasoning
        reasoning = self._generate_reasoning(
            signal_type,
            composite_score,
            flow_analysis,
            fundamental_score,
            risk_score,
            evidence,
        )

        return SignalResult(
            signal_type=signal_type,
            flow_signal=flow_analysis.signal,
            confidence=self._calculate_confidence(
                flow_analysis, fundamental_score, risk_score
            ),
            composite_score=composite_score,
            flow_score=flow_analysis.flow_score,
            fundamental_score=fundamental_score.total,
            risk_score=risk_score.total,
            evidence=evidence,
            reasoning=reasoning,
        )

    def _calculate_trend_alignment(
        self,
        flow_analysis: FlowAnalysis,
        fundamental_score: FundamentalScore,
        risk_score: RiskScore,
    ) -> float:
        """Calculate trend alignment score (0-100).

        Alignment is high when:
        - Flow trend is positive (RISING, SURGING, STEADY)
        - Fundamentals are strong (>60)
        - Risk is low (>60)
        """
        # Flow direction component
        flow_dir = 0.0
        if flow_analysis.trend in ["RISING", "SURGING"]:
            flow_dir = 1.0
        elif flow_analysis.trend == "STEADY":
            flow_dir = 0.5
        elif flow_analysis.trend in ["FALLING", "DECLINING"]:
            flow_dir = -1.0

        # Fundamental strength
        fund_strength = (
            1.0
            if fundamental_score.total >= 60
            else 0.5
            if fundamental_score.total >= 40
            else 0.0
        )

        # Risk safety
        risk_safety = (
            1.0 if risk_score.total >= 60 else 0.5 if risk_score.total >= 40 else 0.0
        )

        # Weighted alignment
        alignment = (flow_dir * 0.4 + fund_strength * 0.3 + risk_safety * 0.3) * 100.0

        return max(0.0, min(100.0, alignment))

    def _compute_composite_score(
        self,
        flow_score: float,
        fundamental_score: float,
        trend_alignment: float,
        risk_score: float,
    ) -> float:
        """Compute weighted composite score.

        Formula:
            score = flow * 0.35 + fundamentals * 0.35 + trend_alignment * 0.15 + risk * 0.15

        Note: risk score is already 0-100 where 100 = safest
        """
        composite = (
            flow_score * self.WEIGHTS["flow"]
            + fundamental_score * self.WEIGHTS["fundamentals"]
            + trend_alignment * self.WEIGHTS["trend_alignment"]
            + risk_score * self.WEIGHTS["risk"]
        )
        return max(0.0, min(100.0, composite))

    def _map_score_to_signal(self, score: float) -> str:
        """Map composite score to signal type using thresholds."""
        if score >= self.SIGNAL_THRESHOLDS["BUY"]:
            return "BUY"
        elif score >= self.SIGNAL_THRESHOLDS["ACCUMULATE"]:
            return "ACCUMULATE"
        elif score >= self.SIGNAL_THRESHOLDS["HOLD"]:
            return "HOLD"
        elif score >= self.SIGNAL_THRESHOLDS["REDUCE"]:
            return "REDUCE"
        else:
            return "AVOID"

    def _build_evidence(
        self,
        subnet: Subnet,
        snapshots: List[FlowSnapshot],
        flow_analysis: FlowAnalysis,
        fundamental_score: FundamentalScore,
        risk_score: RiskScore,
        trend_alignment: float,
    ) -> dict:
        """Build evidence dictionary for the signal."""
        evidence = {
            "subnet": {
                "netuid": subnet.netuid,
                "name": subnet.name,
                "price": subnet.price,
                "market_cap": subnet.market_cap,
                "emission_share": subnet.emission_share,
            },
            "flow": {
                "current_ema": flow_analysis.current_flow,
                "momentum": flow_analysis.flow_momentum,
                "trend": flow_analysis.trend,
                "signal": flow_analysis.signal,
                "score": flow_analysis.flow_score,
            },
            "fundamentals": {
                "total_score": fundamental_score.total,
                "breakdown": fundamental_score.breakdown,
                "notes": fundamental_score.notes,
            },
            "risk": {
                "total_score": risk_score.total,
                "breakdown": risk_score.breakdown,
                "flags": risk_score.flags,
            },
            "trend_alignment": trend_alignment,
            "snapshots_analyzed": len(snapshots),
            "data_timespan_days": self._calculate_timespan(snapshots),
        }
        return evidence

    def _calculate_timespan(self, snapshots: List[FlowSnapshot]) -> float:
        """Calculate timespan of snapshots in days."""
        if len(snapshots) < 2:
            return 0.0

        first = snapshots[0].timestamp
        last = snapshots[-1].timestamp
        delta = last - first
        return delta.total_seconds() / 86400.0

    def _calculate_confidence(
        self,
        flow_analysis: FlowAnalysis,
        fundamental_score: FundamentalScore,
        risk_score: RiskScore,
    ) -> float:
        """Calculate confidence in the signal (0-100).

        Confidence is high when:
        - We have sufficient data (many snapshots)
        - Flow signal is clear (not FLOW_NEUTRAL)
        - Fundamental score is not borderline (not 40-60)
        - Risk score is not ambiguous (not 40-60)
        """
        confidence = 50.0  # Base confidence

        # Data quantity
        # More snapshots = higher confidence (up to a point)
        # This would need snapshot count as input, using placeholder

        # Flow clarity
        clear_flow_signals = ["FLOW_SURGE", "FLOW_STEADY", "FLOW_NEGATIVE"]
        if flow_analysis.signal in clear_flow_signals:
            confidence += 15.0
        elif flow_analysis.signal == "FLOW_NEUTRAL":
            confidence -= 10.0

        # Fundamental clarity
        if fundamental_score.total >= 70 or fundamental_score.total <= 30:
            confidence += 10.0
        elif 40 <= fundamental_score.total <= 60:
            confidence -= 5.0

        # Risk clarity
        if risk_score.total >= 70 or risk_score.total <= 30:
            confidence += 10.0
        elif 40 <= risk_score.total <= 60:
            confidence -= 5.0

        # Clamp to 0-100
        return max(0.0, min(100.0, confidence))

    def _generate_reasoning(
        self,
        signal_type: str,
        composite_score: float,
        flow_analysis: FlowAnalysis,
        fundamental_score: FundamentalScore,
        risk_score: RiskScore,
        evidence: dict,
    ) -> str:
        """Generate human-readable reasoning for the signal."""
        parts = []

        # Opening
        parts.append(f"Signal: {signal_type} (score: {composite_score:.1f}/100)")

        # Flow summary
        flow_desc = {
            "FLOW_SURGE": "surging flow indicating strong conviction",
            "FLOW_STEADY": "steady positive flow showing sustained interest",
            "FLOW_PEAK": "flow at peak but momentum slowing",
            "FLOW_REVERSAL": "flow reversal detected - capital may be exiting",
            "FLOW_NEGATIVE": "negative flow - capital outflow",
            "FLOW_NEUTRAL": "neutral flow - no clear direction",
        }.get(flow_analysis.signal, f"flow signal: {flow_analysis.signal}")
        parts.append(f"• Flow: {flow_desc} (score: {flow_analysis.flow_score:.1f}/100)")

        # Fundamental summary
        fund_qual = (
            "strong"
            if fundamental_score.total >= 70
            else "moderate"
            if fundamental_score.total >= 40
            else "weak"
        )
        parts.append(f"• Fundamentals: {fund_qual} ({fundamental_score.total:.1f}/100)")

        # Top fundamental factors
        top_factors = sorted(
            fundamental_score.breakdown.items(), key=lambda x: x[1], reverse=True
        )[:2]
        for factor, score in top_factors:
            parts.append(f"  - {factor.replace('_', ' ').title()}: {score:.1f}/100")

        # Risk summary
        risk_level = (
            "low"
            if risk_score.total >= 70
            else "moderate"
            if risk_score.total >= 40
            else "high"
        )
        parts.append(f"• Risk: {risk_level} ({risk_score.total:.1f}/100)")

        # Risk flags
        if risk_score.flags:
            parts.append(f"  - Flags: {', '.join(risk_score.flags[:3])}")

        # Trend alignment
        ta = evidence.get("trend_alignment", 50)
        alignment_desc = (
            "aligned" if ta >= 70 else "mixed" if ta >= 40 else "conflicting"
        )
        parts.append(
            f"• Trend alignment: {alignment_desc} ({evidence['trend_alignment']:.1f}/100)"
        )

        # Conclusion
        if signal_type in ["BUY", "ACCUMULATE"]:
            parts.append(
                "\nConclusion: Positive setup with rising flow and solid fundamentals. Consider building position."
            )
        elif signal_type == "HOLD":
            parts.append(
                "\nConclusion: Neutral signal - monitor for clearer direction."
            )
        elif signal_type in ["REDUCE", "AVOID"]:
            parts.append(
                "\nConclusion: Warning signs detected - reduce exposure or avoid."
            )

        return "\n".join(parts)
