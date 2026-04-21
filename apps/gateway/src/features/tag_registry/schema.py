"""ORM schema for the tag registry feature."""

from __future__ import annotations

from sqlalchemy import Enum as SQLEnum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base
from features.tag_registry.types import TagConnectionState


class TagRegistryRow(Base):
    """Persisted registry record for a tag known to the gateway."""

    __tablename__ = "tag_registry"

    tag_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ble_identifier: Mapped[str | None] = mapped_column(String(64), nullable=True, unique=True)
    connection_state: Mapped[TagConnectionState] = mapped_column(
        SQLEnum(TagConnectionState),
        nullable=False,
        default=TagConnectionState.UNKNOWN,
    )
    last_battery_percent: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_rssi: Mapped[int | None] = mapped_column(Integer, nullable=True)
