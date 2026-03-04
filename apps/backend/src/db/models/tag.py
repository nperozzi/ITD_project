from __future__ import annotations

from typing import Optional

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base
from db.models.product import Product


class Tag(Base):
    __tablename__ = "tag"

    # Attributes
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    current_product_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("product.id"),
        nullable=True,
    )
    battery_level: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )

    # Relationships
    product: Mapped[Optional[Product]] = relationship(
        back_populates="tags"
    )
