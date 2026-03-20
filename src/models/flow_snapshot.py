from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, Float, DateTime, ForeignKey
from datetime import datetime

from src.models.subnet import Base


class FlowSnapshot(Base):
    __tablename__ = "flow_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    subnet_netuid: Mapped[int] = mapped_column(
        Integer, ForeignKey("subnets.netuid"), index=True
    )
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)
    flow_ema: Mapped[float] = mapped_column(Float, default=0.0)
    flow_raw: Mapped[float] = mapped_column(Float, default=0.0)
    emission_share: Mapped[float] = mapped_column(Float, default=0.0)
    miners_count: Mapped[int] = mapped_column(Integer, default=0)
    validators_count: Mapped[int] = mapped_column(Integer, default=0)
    price: Mapped[float] = mapped_column(Float, default=0.0)
    market_cap: Mapped[float] = mapped_column(Float, default=0.0)
    tao_volume_24h: Mapped[float] = mapped_column(Float, default=0.0)
    alpha_volume_24h: Mapped[float] = mapped_column(Float, default=0.0)
