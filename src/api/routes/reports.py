"""Report API endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.db.session import get_db
from src.models.report import Report

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/latest")
async def get_latest_report(db: AsyncSession = Depends(get_db)):
    """Get the most recent daily intelligence report."""
    result = await db.execute(
        select(Report).order_by(Report.created_at.desc()).limit(1)
    )
    report = result.scalar_one_or_none()
    if not report:
        return {"detail": "No reports generated yet"}
    return report


@router.get("/")
async def list_reports(
    db: AsyncSession = Depends(get_db),
    report_type: Optional[str] = None,
    limit: int = 10,
):
    """List reports."""
    query = select(Report).order_by(Report.created_at.desc()).limit(limit)
    if report_type:
        query = query.where(Report.report_type == report_type)
    result = await db.execute(query)
    return result.scalars().all()
