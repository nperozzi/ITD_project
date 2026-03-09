from __future__ import annotations

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base
from db.models.store import Store

class ShelfLocation(Base):
    __tablename__ = "shelfLocation"

    #Attributes
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    store_id: Mapped[int] = mapped_column(ForeignKey("store.id"), nullable=False)
    aisle: Mapped[int] = mapped_column(Integer, nullable=False)
    level: Mapped[int] = mapped_column(Integer, nullable=False)

    #Relationships
    store: Mapped["Store"] = relationship(
        back_populates="shelfLocation"
    )
