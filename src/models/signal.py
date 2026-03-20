from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, Float, String, DateTime, JSON, ForeignKey, func
from datetime import datetime

from src.models.subnet import Base


class Signal(Base):
    __tablename__ = "signals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    subnet_netuid: Mapped[int] = mapped_column(
        Integer, ForeignKey("subnets.netuid"), index=True
    )
    signal_type: Mapped[str] = mapped_column(
        String(32)
    )  # BUY, ACCUMULATE, HOLD, REDUCE, AVOID
    flow_signal: Mapped[str] = mapped_column(String(32), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    composite_score: Mapped[float] = mapped_column(Float, default=0.0)
    flow_score: Mapped[float] = mapped_column(Float, default=0.0)
    fundamental_score: Mapped[float] = mapped_column(Float, default=0.0)
    risk_score: Mapped[float] = mapped_column(Float, default=0.0)
    evidence: Mapped[dict] = mapped_column(JSON, default=dict)
    reasoning: Mapped[str] = mapped_column(String(2000), default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), index=True
    )
