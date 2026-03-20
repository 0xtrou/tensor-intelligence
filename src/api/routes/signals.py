"""Signal API endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.db.session import get_db
from src.models.signal import Signal
from src.models.subnet import Subnet

router = APIRouter(prefix="/signals", tags=["signals"])


@router.get("/latest")
async def get_latest_signals(
    db: AsyncSession = Depends(get_db),
    signal_type: Optional[str] = None,
    min_confidence: float = 0,
    limit: int = 20,
):
    """Get latest signals across all subnets."""
    query = select(Signal).order_by(Signal.created_at.desc()).limit(limit)

    if signal_type:
        query = query.where(Signal.signal_type == signal_type.upper())
    if min_confidence > 0:
        query = query.where(Signal.confidence >= min_confidence)

    result = await db.execute(query)
    signals = list(result.scalars().all())

    # Enrich with subnet name
    enriched = []
    for signal in signals:
        subnet_result = await db.execute(
            select(Subnet).where(Subnet.netuid == signal.subnet_netuid)
        )
        subnet = subnet_result.scalar_one_or_none()
        enriched.append(
            {
                **signal.__dict__,
                "subnet_name": subnet.name if subnet else "Unknown",
            }
        )

    return enriched


@router.get("/summary")
async def get_signal_summary(db: AsyncSession = Depends(get_db)):
    """Get count of signals by type."""
    from datetime import datetime, timedelta

    since = datetime.utcnow() - timedelta(hours=24)

    result = await db.execute(
        select(Signal.signal_type, func.count(Signal.id))
        .where(Signal.created_at >= since)
        .group_by(Signal.signal_type)
    )
    return {row[0]: row[1] for row in result.all()}


@router.get("/top")
async def get_top_opportunities(db: AsyncSession = Depends(get_db), limit: int = 10):
    """Get top BUY/ACCUMULATE signals ranked by confidence."""
    subquery = (
        select(Signal.subnet_netuid, func.max(Signal.created_at).label("latest"))
        .where(Signal.signal_type.in_(["BUY", "ACCUMULATE"]))
        .group_by(Signal.subnet_netuid)
        .subquery()
    )

    result = await db.execute(
        select(Signal)
        .join(
            subquery,
            (Signal.subnet_netuid == subquery.c.subnet_netuid)
            & (Signal.created_at == subquery.c.latest),
        )
        .order_by(Signal.confidence.desc())
        .limit(limit)
    )
    signals = list(result.scalars().all())

    return [
        {
            "netuid": s.subnet_netuid,
            "signal_type": s.signal_type,
            "confidence": s.confidence,
            "composite_score": s.composite_score,
            "reasoning": s.reasoning,
        }
        for s in signals
    ]
