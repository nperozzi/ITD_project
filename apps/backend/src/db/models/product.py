from __future__ import annotations

from typing import Any

from sqlalchemy import JSON, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


class Product(Base):
    __tablename__ = "product"

    # Attributes
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sku: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    attributes_json: Mapped[dict[str, Any]] = mapped_column(JSON,
        nullable=False,
        default=dict
    )
    price: Mapped[float] = mapped_column(Float, nullable=False)

    # Relationships
    tags: Mapped[list["Tag"]] = relationship(
        back_populates="product"
    )
