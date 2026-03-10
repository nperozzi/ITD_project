from __future__ import annotations

from sqlalchemy import Integer, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base

class TagPayload(Base):
    __tablename__ = "tagpayload"

    # Attributes
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    tag_id: Mapped[int] = mapped_column(
        ForeignKey("tag.id"),
        nullable=False
    )

    payload_json: Mapped[dict] = mapped_column(JSON, nullable=False)

    # Relationships
    tag: Mapped["Tag"] = relationship(
        back_populates="payloads"
    )  

