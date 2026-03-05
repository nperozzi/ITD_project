from __future__ import annotations


from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base

class Store(Base):
    __tablename__ = "store"

    #Attributes
    id: Mapped[int] = mapped_column(Integer, primary_key = True)
    name: Mapped[str] = mapped_column(String, nullable=False)
