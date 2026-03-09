# Tag(id, battery_pct, status, product_id, shelf_location_id)

from __future__ import annotations

from typing import Optional
from enum import Enum

from sqlalchemy import CheckConstraint, Enum as SQLEnum, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base
from db.models.product import Product

class Status(Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    DISABLED = "disabled"

class Tag(Base):
    __tablename__ = "tag"
    __table_args__ = (
        CheckConstraint(
            "battery_pct IS NULL OR (battery_pct >= 0 AND battery_pct <= 100)",
            name="ck_tag_battery_pct_0_100",
        ),
    )

    # Attributes
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    battery_pct: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status: Mapped[Status] = mapped_column(SQLEnum(Status), nullable=False)
    product_id: Mapped[Optional[int]] = mapped_column(Integer,
        ForeignKey("product.id"),
        nullable=True
    )
    shelf_location_id: Mapped[Optional[int]] = mapped_column(Integer,
        ForeignKey("shelfLocation.id"),
        nullable=True
    )

    # Relationships
    product: Mapped[Optional[Product]] = relationship(
        back_populates="tags"
    )

    payloads: Mapped[list["TagPayload"]] = relationship(
    back_populates="tag",
    cascade="all, delete-orphan"
    ) 
