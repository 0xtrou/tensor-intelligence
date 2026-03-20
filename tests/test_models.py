"""Test models and database interactions."""

import pytest
from datetime import datetime, timedelta
from sqlalchemy import select

from src.models.subnet import Subnet
from src.models.flow_snapshot import FlowSnapshot
from src.models.signal import Signal
from src.models.report import Report


async def test_subnet_creation(db_session):
    """Test Subnet model creation with all fields."""
    subnet = Subnet(
        netuid=1,
        name="Apex",
        symbol="APEX",
        price=100.0,
        market_cap=1000000.0,
        emission=0.001,
        emission_share=0.1,
        active_miners=100,
        active_validators=50,
        liquidity=100000.0,
        total_tao=10000000.0,
        total_alpha=5000000.0,
        alpha_staked=4000000.0,
        tao_volume_24h=500000.0,
        alpha_volume_24h=250000.0,
        category="ai_inference",
        fundamental_score=75.0,
        risk_score=60.0,
        ssi_score=65.0,
        is_active=True,
    )

    db_session.add(subnet)
    await db_session.commit()
    await db_session.refresh(subnet)

    assert subnet.netuid == 1
    assert subnet.name == "Apex"
    assert subnet.symbol == "APEX"
    assert subnet.price == 100.0
    assert subnet.market_cap == 1000000.0
    assert subnet.emission == 0.001
    assert subnet.emission_share == 0.1
    assert subnet.active_miners == 100
    assert subnet.active_validators == 50
    assert subnet.liquidity == 100000.0
    assert subnet.total_tao == 10000000.0
    assert subnet.total_alpha == 5000000.0
    assert subnet.alpha_staked == 4000000.0
    assert subnet.tao_volume_24h == 500000.0
    assert subnet.alpha_volume_24h == 250000.0
    assert subnet.category == "ai_inference"
    assert subnet.fundamental_score == 75.0
    assert subnet.risk_score == 60.0
    assert subnet.ssi_score == 65.0
    assert subnet.is_active is True
    assert subnet.created_at is not None
    assert subnet.updated_at is not None
async def test_subnet_creation_with_defaults(db_session):
    """Test Subnet model creation with default values."""
    subnet = Subnet(
        netuid=2,
        name="Test Subnet",
    )

    db_session.add(subnet)
    await db_session.commit()
    await db_session.refresh(subnet)

    assert subnet.netuid == 2
    assert subnet.name == "Test Subnet"
    assert subnet.symbol == ""
    assert subnet.price == 0.0
    assert subnet.market_cap == 0.0
    assert subnet.emission == 0.0
    assert subnet.emission_share == 0.0
    assert subnet.active_miners == 0
    assert subnet.active_validators == 0
    assert subnet.liquidity == 0.0
    assert subnet.total_tao == 0.0
    assert subnet.total_alpha == 0.0
    assert subnet.alpha_staked == 0.0
    assert subnet.tao_volume_24h == 0.0
    assert subnet.alpha_volume_24h == 0.0
    assert subnet.category == ""
    assert subnet.fundamental_score is None
    assert subnet.risk_score is None
    assert subnet.ssi_score is None
    assert subnet.is_active is True
async def test_flow_snapshot_creation(db_session):
    """Test FlowSnapshot model creation."""
    subnet = Subnet(netuid=1)
    db_session.add(subnet)
    await db_session.commit()

    snapshot = FlowSnapshot(
        subnet_netuid=1,
        timestamp=datetime.utcnow(),
        flow_ema=1e12,
        emission_share=0.1,
        miners_count=100,
        validators_count=50,
        price=100.0,
        market_cap=1000000.0,
        tao_volume_24h=500000.0,
        alpha_volume_24h=250000.0,
    )

    db_session.add(snapshot)
    await db_session.commit()
    await db_session.refresh(snapshot)

    assert snapshot.id is not None
    assert snapshot.subnet_netuid == 1
    assert snapshot.timestamp is not None
    assert snapshot.flow_ema == 1e12
    assert snapshot.emission_share == 0.1
    assert snapshot.miners_count == 100
    assert snapshot.validators_count == 50
    assert snapshot.price == 100.0
    assert snapshot.market_cap == 1000000.0
    assert snapshot.tao_volume_24h == 500000.0
    assert snapshot.alpha_volume_24h == 250000.0
async def test_flow_snapshot_with_foreign_key(db_session):
    """Test FlowSnapshot creation with valid foreign key."""
    subnet = Subnet(netuid=3, name="Test")
    db_session.add(subnet)
    await db_session.commit()

    snapshot = FlowSnapshot(
        subnet_netuid=3,
        timestamp=datetime.utcnow(),
        flow_ema=1e11,
    )

    db_session.add(snapshot)
    await db_session.commit()

    assert snapshot.subnet_netuid == 3
async def test_signal_creation_with_defaults(db_session):
    """Test Signal model creation with default values."""
    subnet = Subnet(netuid=1)
    db_session.add(subnet)
    await db_session.commit()

    signal = Signal(
        subnet_netuid=1,
        signal_type="BUY",
        flow_score=80.0,
        fundamental_score=75.0,
        risk_score=70.0,
    )

    db_session.add(signal)
    await db_session.commit()
    await db_session.refresh(signal)

    assert signal.id is not None
    assert signal.subnet_netuid == 1
    assert signal.signal_type == "BUY"
    assert signal.flow_signal is None
    assert signal.confidence == 0.0
    assert signal.composite_score == 0.0
    assert signal.flow_score == 80.0
    assert signal.fundamental_score == 75.0
    assert signal.risk_score == 70.0
    assert signal.evidence == {}
    assert signal.reasoning == ""
    assert signal.created_at is not None
async def test_signal_with_full_data(db_session):
    """Test Signal model creation with all fields."""
    subnet = Subnet(netuid=2)
    db_session.add(subnet)
    await db_session.commit()

    signal = Signal(
        subnet_netuid=2,
        signal_type="ACCUMULATE",
        flow_signal="FLOW_SURGE",
        confidence=85.0,
        composite_score=65.0,
        flow_score=70.0,
        fundamental_score=70.0,
        risk_score=65.0,
        evidence={"test": "data"},
        reasoning="Test reasoning",
    )

    db_session.add(signal)
    await db_session.commit()
    await db_session.refresh(signal)

    assert signal.subnet_netuid == 2
    assert signal.signal_type == "ACCUMULATE"
    assert signal.flow_signal == "FLOW_SURGE"
    assert signal.confidence == 85.0
    assert signal.composite_score == 65.0
    assert signal.flow_score == 70.0
    assert signal.fundamental_score == 70.0
    assert signal.risk_score == 65.0
    assert signal.evidence == {"test": "data"}
    assert signal.reasoning == "Test reasoning"
async def test_signal_foreign_key(db_session):
    """Test Signal creation with valid foreign key."""
    subnet = Subnet(netuid=4)
    db_session.add(subnet)
    await db_session.commit()

    signal = Signal(subnet_netuid=4, signal_type="HOLD")
    db_session.add(signal)
    await db_session.commit()

    assert signal.subnet_netuid == 4
async def test_subnet_model_netuid_uniqueness(db_session):
    """Test that Subnet.netuid is unique."""
    subnet1 = Subnet(netuid=5, name="First")
    subnet2 = Subnet(netuid=5, name="Second")

    db_session.add(subnet1)
    await db_session.commit()

    db_session.add(subnet2)
    with pytest.raises(Exception):  # Will raise IntegrityError
        await db_session.commit()
async def test_flow_snapshot_foreign_key_constraint(db_session):
    """Test FlowSnapshot foreign key constraint."""
    snapshot = FlowSnapshot(subnet_netuid=999)  # Non-existent subnet

    db_session.add(snapshot)
    with pytest.raises(Exception):  # Will raise IntegrityError
        await db_session.commit()