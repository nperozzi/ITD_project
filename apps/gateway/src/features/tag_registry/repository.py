"""Persistence for the tag registry.

Receives a session factory via constructor injection so short-lived sessions
can be opened per call (safe for the paho-mqtt and bleak callback threads).
"""

from __future__ import annotations

from sqlalchemy import select

from adapters.types import BleIdentifier, TagId
from db.session import SessionFactory
from features.tag_registry.schema import TagRegistryRow
from features.tag_registry.types import RegisteredTag, TagConnectionState
from logger import Logger


class TagRegistryRepository:
    """Reads and writes `tag_registry` rows."""

    def __init__(
        self,
        session_factory: SessionFactory,
        logger: Logger | None = None,
    ) -> None:
        self._session_factory = session_factory
        self._logger = logger or Logger("TagRegistryRepository")

    def upsert_tag(
        self,
        tag_id: TagId,
        ble_identifier: BleIdentifier | None,
    ) -> RegisteredTag:
        """Insert a tag if unseen, otherwise update its BLE mapping."""

        with self._session_factory() as session:
            row = session.get(TagRegistryRow, tag_id)
            if row is None:
                row = TagRegistryRow(
                    tag_id=tag_id,
                    ble_identifier=ble_identifier,
                    connection_state=TagConnectionState.UNKNOWN,
                )
                session.add(row)
            elif ble_identifier is not None:
                row.ble_identifier = ble_identifier
            session.commit()
            session.refresh(row)
            return self._to_domain(row)

    def set_connection_state(
        self,
        tag_id: TagId,
        connection_state: TagConnectionState,
    ) -> None:
        with self._session_factory() as session:
            row = session.get(TagRegistryRow, tag_id)
            if row is None:
                self._logger.warning("set_connection_state: tag %s not registered", tag_id)
                return
            row.connection_state = connection_state
            session.commit()

    def set_telemetry(
        self,
        tag_id: TagId,
        battery_percent: int | None,
        rssi: int | None,
    ) -> None:
        with self._session_factory() as session:
            row = session.get(TagRegistryRow, tag_id)
            if row is None:
                self._logger.warning("set_telemetry: tag %s not registered", tag_id)
                return
            if battery_percent is not None:
                row.last_battery_percent = battery_percent
            if rssi is not None:
                row.last_rssi = rssi
            session.commit()

    def find_by_id(self, tag_id: TagId) -> RegisteredTag | None:
        with self._session_factory() as session:
            row = session.get(TagRegistryRow, tag_id)
            return self._to_domain(row) if row is not None else None

    def find_by_ble_identifier(
        self, ble_identifier: BleIdentifier
    ) -> RegisteredTag | None:
        with self._session_factory() as session:
            statement = select(TagRegistryRow).where(
                TagRegistryRow.ble_identifier == ble_identifier
            )
            row = session.execute(statement).scalar_one_or_none()
            return self._to_domain(row) if row is not None else None

    def list_all(self) -> list[RegisteredTag]:
        with self._session_factory() as session:
            rows = session.execute(select(TagRegistryRow)).scalars().all()
            return [self._to_domain(row) for row in rows]

    @staticmethod
    def _to_domain(row: TagRegistryRow) -> RegisteredTag:
        return RegisteredTag(
            tag_id=row.tag_id,
            ble_identifier=row.ble_identifier,
            connection_state=row.connection_state,
            last_battery_percent=row.last_battery_percent,
            last_rssi=row.last_rssi,
        )
