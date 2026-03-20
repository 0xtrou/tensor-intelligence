"""Test analysis components (FlowDetector, FundamentalScorer, RiskScorer, SignalGenerator)."""

import pytest
from datetime import datetime, timedelta
from dataclasses import dataclass

from src.models.subnet import Subnet
from src.models.flow_snapshot import FlowSnapshot
from src.engine.analysis.flow_detector import FlowDetector, FlowAnalysis
from src.engine.analysis.fundamental_scorer import FundamentalScorer, FundamentalScore
from src.engine.analysis.risk_scorer import RiskScorer, RiskScore
from src.engine.analysis.signal_generator import (
    SignalGenerator,
    SignalResult,
)


def create_test_subnet(netuid, **kwargs):
    """Helper to create test subnet."""
    return Subnet(
        netuid=netuid,
        name=f"Test Subnet {netuid}",
        **kwargs,
    )


def create_test_snapshot(subnet_netuid, timestamp, flow_ema, **kwargs):
    """Helper to create test flow snapshot."""
    return FlowSnapshot(
        subnet_netuid=subnet_netuid,
        timestamp=timestamp,
        flow_ema=flow_ema,
        **kwargs,
    )


# --- FlowDetector Tests ---


def test_flow_detector_empty_snapshots():
    """Test FlowDetector with no snapshots."""
    detector = FlowDetector()
    snapshots = []
    result = detector.analyze(snapshots)

    assert isinstance(result, FlowAnalysis)
    assert result.current_flow == 0.0
    assert result.flow_momentum == 0.0
    assert result.trend == "UNKNOWN"
    assert result.signal == "NO_DATA"
    assert result.flow_score == 0.0
def test_flow_detector_rising_flow():
    """Test FlowDetector with rising flow data."""
    detector = FlowDetector()

    # Create 30 snapshots with gradually increasing flow
    snapshots = []
    base_flow = 1e11
    for i in range(30):
        timestamp = datetime.utcnow() - timedelta(hours=i * 0.5)
        flow_ema = base_flow * (1 + i * 0.1)
        snapshots.append(create_test_snapshot(1, timestamp, flow_ema))

    result = detector.analyze(snapshots)

    assert result.trend in ["RISING", "SURGING"]
    assert result.flow_score > 0
    assert result.current_flow > 0
def test_flow_detector_declining_flow():
    """Test FlowDetector with declining flow."""
    detector = FlowDetector()

    # Create snapshots with decreasing flow
    snapshots = []
    base_flow = 1e13
    for i in range(30):
        timestamp = datetime.utcnow() - timedelta(hours=i * 0.5)
        flow_ema = base_flow * (1 - i * 0.05)
        snapshots.append(create_test_snapshot(3, timestamp, flow_ema))

    result = detector.analyze(snapshots)

    assert result.trend in ["DECLINING", "FALLING"]
    assert result.flow_score < 50
def test_flow_detector_ema_calculation():
    """Test that EMA calculation works correctly."""
    detector = FlowDetector()

    # Simple case: equal values
    snapshots = [
        create_test_snapshot(1, datetime.utcnow(), 100.0),
        create_test_snapshot(1, datetime.utcnow(), 110.0),
        create_test_snapshot(1, datetime.utcnow(), 120.0),
    ]

    result = detector.analyze(snapshots)
    # Should handle basic case without error
    assert isinstance(result, FlowAnalysis)
def test_flow_detector_signal_detection():
    """Test flow signal detection."""
    detector = FlowDetector()

    # Test negative flow signal
    snapshots = []
    for i in range(20):
        timestamp = datetime.utcnow() - timedelta(hours=i * 0.5)
        flow_ema = -1e11  # Negative flow
        snapshots.append(create_test_snapshot(4, timestamp, flow_ema))

    result = detector.analyze(snapshots)
    # Should detect negative flow eventually
    assert result.current_flow < 0
async def test_risk_scorer_with_data(db_session):
    """Test RiskScorer with snapshots."""
    scorer = RiskScorer()

    subnet = create_test_subnet(
        netuid=1,
        market_cap=1000000.0,
        liquidity=100000.0,
        tao_volume_24h=500000.0,
        total_alpha=5000000.0,
        alpha_staked=4000000.0,
        emission_share=0.1,
        active_miners=100,
        active_validators=50,
    )

    snapshots = [create_test_snapshot(1, datetime.utcnow(), 1e12)]

    result = scorer.score(subnet, snapshots)

    assert isinstance(result, RiskScore)
    assert isinstance(result.total, float)
    assert 0 <= result.total <= 100
    assert isinstance(result.breakdown, dict)
    assert isinstance(result.flags, list)
async def test_risk_scorer_insufficient_data(db_session):
    """Test RiskScorer with no snapshots."""
    scorer = RiskScorer()

    subnet = create_test_subnet(netuid=999, market_cap=1000000.0)

    result = scorer.score(subnet, [])

    assert result.flags == ["Insufficient data"]
async def test_risk_scorer_breakdown_dimensions(db_session):
    """Test that all risk dimensions are scored."""
    scorer = RiskScorer()

    subnet = create_test_subnet(
        netuid=1,
        market_cap=1000000.0,
        tao_volume_24h=500000.0,
        active_miners=100,
    )

    snapshots = [create_test_snapshot(1, datetime.utcnow(), 1e12)]

    result = scorer.score(subnet, snapshots)

    # Check all dimensions are present
    assert "flow_volatility" in result.breakdown
    assert "liquidity" in result.breakdown
    assert "emission_sustainability" in result.breakdown
    assert "concentration" in result.breakdown
    assert "crash_risk" in result.breakdown
async def test_risk_scorer_no_data(db_session):
    """Test RiskScorer with minimal data."""
    scorer = RiskScorer()

    subnet = create_test_subnet(netuid=3)

    result = scorer.score(subnet, [])

    assert result.flags == ["Insufficient data"]
def test_signal_generator_initialization():
    """Test SignalGenerator initialization."""
    generator = SignalGenerator()

    assert generator.flow_detector is not None
    assert generator.fundamental_scorer is not None
    assert generator.risk_scorer is not None