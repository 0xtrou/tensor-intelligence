"""Signal pipeline trace endpoint — shows how a signal was generated."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from src.db.session import get_db
from src.models.subnet import Subnet
from src.models.flow_snapshot import FlowSnapshot
from src.engine.analysis.flow_detector import FlowDetector
from src.engine.analysis.fundamental_scorer import FundamentalScorer
from src.engine.analysis.risk_scorer import RiskScorer
from src.engine.analysis.signal_generator import SignalGenerator

router = APIRouter(prefix="/signal-flow", tags=["signal-flow"])


class FlowStage(BaseModel):
    name: str
    score: float
    output: Dict[str, Any]
    description: str


class SignalFlowResponse(BaseModel):
    subnet: Dict[str, Any]
    pipeline: List[FlowStage]
    composite: Dict[str, Any]
    signal: Dict[str, Any]
    evidence: Dict[str, Any]
    formula: str
    snapshots_analyzed: int
    data_timespan_days: float


@router.get("/{netuid}", response_model=SignalFlowResponse)
async def get_signal_flow(netuid: int, db: AsyncSession = Depends(get_db)):
    """Get the full signal generation pipeline trace for a subnet."""
    # Fetch subnet
    result = await db.execute(select(Subnet).where(Subnet.netuid == netuid))
    subnet = result.scalar_one_or_none()
    if not subnet:
        raise HTTPException(status_code=404, detail=f"Subnet {netuid} not found")

    # Fetch recent flow snapshots (up to 672 = ~7 days at 15min)
    snap_result = await db.execute(
        select(FlowSnapshot)
        .where(FlowSnapshot.subnet_netuid == netuid)
        .order_by(FlowSnapshot.timestamp.desc())
        .limit(672)
    )
    snapshots = list(snap_result.scalars().all())
    snapshots.reverse()  # ascending for analysis

    if len(snapshots) < 3:
        raise HTTPException(
            status_code=422,
            detail=f"Not enough data for subnet {netuid} "
            f"({len(snapshots)} snapshots, need 3+)",
        )

    # Run the full pipeline
    detector = FlowDetector()
    fund_scorer = FundamentalScorer()
    risk_scorer_obj = RiskScorer()
    generator = SignalGenerator()

    # Stage 1: Flow Detection
    flow_analysis = detector.analyze(snapshots)

    # Stage 2: Fundamental Scoring
    fund_score = fund_scorer.score(subnet, snapshots)

    # Stage 3: Risk Scoring
    risk_score = risk_scorer_obj.score(subnet, snapshots)

    # Stage 4: Trend Alignment
    trend_alignment = generator._calculate_trend_alignment(
        flow_analysis, fund_score, risk_score
    )

    # Stage 5: Composite Score
    composite_score = generator._compute_composite_score(
        flow_analysis.flow_score,
        fund_score.total,
        trend_alignment,
        risk_score.total,
    )

    # Stage 6: Signal Type
    signal_type = generator._map_score_to_signal(composite_score)

    # Stage 7: Confidence
    confidence = generator._calculate_confidence(flow_analysis, fund_score, risk_score)

    # Stage 8: Evidence
    evidence = generator._build_evidence(
        subnet, snapshots, flow_analysis, fund_score, risk_score, trend_alignment
    )

    # Build pipeline response
    pipeline = [
        FlowStage(
            name="1. Flow Detection",
            score=flow_analysis.flow_score,
            output={
                "trend": flow_analysis.trend,
                "signal": flow_analysis.signal,
                "momentum": round(flow_analysis.flow_momentum, 1),
                "current_flow": flow_analysis.current_flow,
            },
            description="EMA analysis of flow trends: short (3d), medium (7d), "
            "long (30d). Detects SURGE, STEADY, PEAK, REVERSAL, "
            "NEGATIVE patterns.",
        ),
        FlowStage(
            name="2. Fundamental Analysis",
            score=fund_score.total,
            output={
                "breakdown": fund_score.breakdown,
                "notes": fund_score.notes[:5] if fund_score.notes else [],
            },
            description="Durbin Framework: team (20%), use_case (15%), "
            "execution (20%), network (15%), community (10%), "
            "tokenomics (10%), moat (10%).",
        ),
        FlowStage(
            name="3. Risk Assessment",
            score=risk_score.total,
            output={
                "breakdown": risk_score.breakdown,
                "flags": risk_score.flags,
            },
            description="Flow volatility (25%), liquidity (25%), emission "
            "sustainability (20%), concentration (15%), crash risk (15%).",
        ),
        FlowStage(
            name="4. Trend Alignment",
            score=round(trend_alignment, 1),
            output={
                "flow_direction": (
                    "RISING"
                    if flow_analysis.trend in ["RISING", "SURGING", "STEADY"]
                    else "FALLING"
                ),
                "fundamental_strength": (
                    "strong"
                    if fund_score.total >= 60
                    else "moderate"
                    if fund_score.total >= 40
                    else "weak"
                ),
                "risk_safety": (
                    "safe"
                    if risk_score.total >= 60
                    else "moderate"
                    if risk_score.total >= 40
                    else "risky"
                ),
            },
            description="Are flow, fundamentals, and risk all pointing the same "
            "direction? Weighted: flow_dir*0.4 + fund*0.3 + risk*0.3.",
        ),
    ]

    formula = (
        "flow \u00d7 0.35 + fundamentals \u00d7 0.35 "
        "+ trend_alignment \u00d7 0.15 + risk \u00d7 0.15"
    )

    composite = {
        "score": round(composite_score, 1),
        "formula": formula,
        "weights": {
            "flow": 0.35,
            "fundamentals": 0.35,
            "trend_alignment": 0.15,
            "risk": 0.15,
        },
        "inputs": {
            "flow": round(flow_analysis.flow_score, 1),
            "fundamentals": round(fund_score.total, 1),
            "trend_alignment": round(trend_alignment, 1),
            "risk": round(risk_score.total, 1),
        },
        "thresholds": {
            "BUY": "\u2265 70",
            "ACCUMULATE": "\u2265 50",
            "HOLD": "\u2265 30",
            "REDUCE": "\u2265 15",
            "AVOID": "< 15",
        },
    }

    signal = {
        "type": signal_type,
        "confidence": round(confidence, 1),
        "reasoning": generator._generate_reasoning(
            signal_type,
            composite_score,
            flow_analysis,
            fund_score,
            risk_score,
            evidence,
        ),
    }

    # Calculate timespan
    if len(snapshots) >= 2:
        delta = snapshots[-1].timestamp - snapshots[0].timestamp
        timespan_days = max(0.1, delta.total_seconds() / 86400)
    else:
        timespan_days = 0.1

    return SignalFlowResponse(
        subnet={
            "netuid": subnet.netuid,
            "name": subnet.name,
            "price": subnet.price,
            "market_cap": subnet.market_cap,
            "emission_share": subnet.emission_share,
            "active_miners": subnet.active_miners,
            "active_validators": subnet.active_validators,
        },
        pipeline=pipeline,
        composite=composite,
        signal=signal,
        evidence=evidence,
        formula=formula,
        snapshots_analyzed=len(snapshots),
        data_timespan_days=round(timespan_days, 1),
    )
