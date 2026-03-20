"""Subnet API endpoints."""

from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.db.session import get_db
from src.models.subnet import Subnet
from src.models.flow_snapshot import FlowSnapshot
from src.models.signal import Signal

router = APIRouter(prefix="/subnets", tags=["subnets"])


class SubnetResponse(BaseModel):
    netuid: int
    name: str
    price: float
    market_cap: float
    emission: float
    emission_share: float
    active_miners: int
    active_validators: int
    fundamental_score: Optional[float]
    risk_score: Optional[float]
    ssi_score: Optional[float]
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class FlowSnapshotResponse(BaseModel):
    timestamp: str
    flow_ema: float
    emission_share: float
    miners_count: int
    validators_count: int
    price: float

    class Config:
        from_attributes = True


class SignalBriefResponse(BaseModel):
    signal_type: str
    flow_signal: Optional[str]
    confidence: float
    composite_score: float
    created_at: str

    class Config:
        from_attributes = True


class SubnetDetailResponse(BaseModel):
    subnet: SubnetResponse
    recent_flow: list[FlowSnapshotResponse]
    recent_signals: list[SignalBriefResponse]


@router.get("/", response_model=list[SubnetResponse])
async def list_subnets(
    db: AsyncSession = Depends(get_db),
    sort_by: str = "emission_share",
    limit: int = 50,
):
    """List all tracked subnets."""
    valid_sorts = {
        "emission_share",
        "price",
        "market_cap",
        "fundamental_score",
        "risk_score",
    }
    if sort_by not in valid_sorts:
        sort_by = "emission_share"

    result = await db.execute(
        select(Subnet)
        .where(Subnet.is_active == True)
        .order_by(getattr(Subnet, sort_by).desc())
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/{netuid}")
async def get_subnet(netuid: int, db: AsyncSession = Depends(get_db)):
    """Get subnet detail with recent flow and signals."""
    result = await db.execute(select(Subnet).where(Subnet.netuid == netuid))
    subnet = result.scalar_one_or_none()
    if not subnet:
        raise HTTPException(status_code=404, detail=f"Subnet {netuid} not found")

    # Get recent flow snapshots
    flow_result = await db.execute(
        select(FlowSnapshot)
        .where(FlowSnapshot.subnet_netuid == netuid)
        .order_by(FlowSnapshot.timestamp.desc())
        .limit(672)  # ~7 days
    )
    flow_snapshots = list(flow_result.scalars().all())

    # Get recent signals
    signal_result = await db.execute(
        select(Signal)
        .where(Signal.subnet_netuid == netuid)
        .order_by(Signal.created_at.desc())
        .limit(10)
    )
    signals = list(signal_result.scalars().all())

    return {"subnet": subnet, "recent_flow": flow_snapshots, "recent_signals": signals}


@router.get("/{netuid}/flow")
async def get_flow_history(
    netuid: int, db: AsyncSession = Depends(get_db), hours: int = 168
):
    """Get flow history for a subnet."""
    from datetime import datetime, timedelta

    since = datetime.utcnow() - timedelta(hours=hours)
    result = await db.execute(
        select(FlowSnapshot)
        .where(FlowSnapshot.subnet_netuid == netuid, FlowSnapshot.timestamp >= since)
        .order_by(FlowSnapshot.timestamp.desc())
    )
    return result.scalars().all()


@router.get("/{netuid}/signals")
async def get_subnet_signals(
    netuid: int, db: AsyncSession = Depends(get_db), limit: int = 20
):
    """Get recent signals for a subnet."""
    result = await db.execute(
        select(Signal)
        .where(Signal.subnet_netuid == netuid)
        .order_by(Signal.created_at.desc())
        .limit(limit)
    )
    return result.scalars().all()
