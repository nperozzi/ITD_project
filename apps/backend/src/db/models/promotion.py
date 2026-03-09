from __future__ import annotations
from typing import Optional

from sqlalchemy import Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import CheckConstraint

from db.base import Base
from db.models.product import Product

class Promotion(Base):
    __tablename__ = "promotion"

    __table_args__ = (
    CheckConstraint("discount_percentage >= 0 AND discount_percentage <= 100"),
    )

    #Attributes
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[Optional[int]] = mapped_column(Integer,
        ForeignKey("product.id"),
        nullable=True
    )
    discount_percentage: Mapped [int] = mapped_column (integer)
    start_at: Mapped [DateTime] = mapped_column (DateTime)
    end_at: Mapped [DateTime] = mapped_column (DateTime)

    #Relationships
    product: Mapped [Optional[Product]] = relationship (
        back_populates="promotions"
    )


