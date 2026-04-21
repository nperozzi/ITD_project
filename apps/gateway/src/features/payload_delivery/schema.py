"""ORM schema for payload delivery."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum as SQLEnum, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base
from features.payload_delivery.types import DeliveryState


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class PayloadDeliveryRow(Base):
    """Persisted queue entry for a payload destined for a tag."""

    __tablename__ = "payload_delivery"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tag_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(127), nullable=False)
    final_price: Mapped[float] = mapped_column(Float, nullable=False)
    delivery_state: Mapped[DeliveryState] = mapped_column(
        SQLEnum(DeliveryState),
        nullable=False,
        default=DeliveryState.PENDING,
    )
    attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_attempted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_utc_now,
    )
