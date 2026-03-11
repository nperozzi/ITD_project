from __future__ import annotations

from typing import Optional
from enum import Enum

from sqlalchemy import ForeignKey, Integer, Enum as SQLEnum , DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base
from db.models.store import Store

class Status(Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    DISABLED = "disabled"

class Gateway(Base):
    __tablename__ = "gateway"

    #Attributes
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    store_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("store.id"),
        nullable = True,
    )
    status: Mapped[Status] = mapped_column(SQLEnum(Status), nullable=False)
    last_heartbeat_at: Mapped[DateTime] = mapped_column(DateTime, nullable=True)

    #Relationships
    store: Mapped[Optional[Store]] = relationship(
        back_populates="gateways"
    )

