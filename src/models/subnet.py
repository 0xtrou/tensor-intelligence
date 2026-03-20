from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float, Boolean, DateTime, func
from datetime import datetime


class Base(DeclarativeBase):
    pass


class Subnet(Base):
    __tablename__ = "subnets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    netuid: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), default="")
    symbol: Mapped[str] = mapped_column(String(64), default="")
    price: Mapped[float] = mapped_column(Float, default=0.0)
    market_cap: Mapped[float] = mapped_column(Float, default=0.0)
    emission: Mapped[float] = mapped_column(Float, default=0.0)
    emission_share: Mapped[float] = mapped_column(Float, default=0.0)
    active_miners: Mapped[int] = mapped_column(Integer, default=0)
    active_validators: Mapped[int] = mapped_column(Integer, default=0)
    liquidity: Mapped[float] = mapped_column(Float, default=0.0)
    total_tao: Mapped[float] = mapped_column(Float, default=0.0)
    total_alpha: Mapped[float] = mapped_column(Float, default=0.0)
    alpha_staked: Mapped[float] = mapped_column(Float, default=0.0)
    tao_volume_24h: Mapped[float] = mapped_column(Float, default=0.0)
    alpha_volume_24h: Mapped[float] = mapped_column(Float, default=0.0)
    category: Mapped[str] = mapped_column(String(64), default="")
    fundamental_score: Mapped[float] = mapped_column(Float, nullable=True)
    risk_score: Mapped[float] = mapped_column(Float, nullable=True)
    ssi_score: Mapped[float] = mapped_column(Float, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
