from __future__ import annotations

from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


class Product(Base):
    __tablename__ = "product"

    # Attributes
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)

    # Relationships
    tags: Mapped[list["Tag"]] = relationship(
        back_populates="product"
    )
