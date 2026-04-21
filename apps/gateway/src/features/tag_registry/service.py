"""Tag registry service: owns the lifecycle of tag records and their state."""

from __future__ import annotations

from adapters.types import BleIdentifier, TagId
from features.tag_registry.input import (
    RegisterTagInput,
    UpdateTagLinkInput,
    UpdateTelemetryInput,
)
from features.tag_registry.repository import TagRegistryRepository
from features.tag_registry.types import RegisteredTag, TagConnectionState
from logger import Logger


class TagRegistryService:
    """Business logic for registering tags and tracking their connection state."""

    def __init__(
        self,
        repository: TagRegistryRepository,
        logger: Logger | None = None,
    ) -> None:
        self._repository = repository
        self._logger = logger or Logger("TagRegistryService")

    def register_tag(self, params: RegisterTagInput) -> RegisteredTag:
        """Ensure a tag exists in the registry, optionally with a BLE mapping."""

        registered_tag = self._repository.upsert_tag(
            tag_id=params.tag_id,
            ble_identifier=params.ble_identifier,
        )
        self._logger.debug("register_tag(tag_id=%s) -> ok", params.tag_id)
        return registered_tag

    def link_ble_identifier(self, params: UpdateTagLinkInput) -> RegisteredTag:
        """Attach an observed BLE identifier to an existing tag id."""

        registered_tag = self._repository.upsert_tag(
            tag_id=params.tag_id,
            ble_identifier=params.ble_identifier,
        )
        self._repository.set_connection_state(
            tag_id=params.tag_id,
            connection_state=TagConnectionState.DISCOVERED,
        )
        self._logger.debug(
            "link_ble_identifier(tag_id=%s, ble=%s)",
            params.tag_id,
            params.ble_identifier,
        )
        return self._repository.find_by_id(params.tag_id) or registered_tag

    def mark_connecting(self, tag_id: TagId) -> None:
        self._repository.set_connection_state(tag_id, TagConnectionState.CONNECTING)

    def mark_connected(self, tag_id: TagId) -> None:
        self._repository.set_connection_state(tag_id, TagConnectionState.CONNECTED)

    def mark_disconnected(self, tag_id: TagId) -> None:
        self._repository.set_connection_state(tag_id, TagConnectionState.DISCONNECTED)

    def record_telemetry(self, params: UpdateTelemetryInput) -> None:
        self._repository.set_telemetry(
            tag_id=params.tag_id,
            battery_percent=params.battery_percent,
            rssi=params.rssi,
        )

    def resolve_tag_id_from_ble(
        self, ble_identifier: BleIdentifier
    ) -> TagId | None:
        """Look up which backend tag id belongs to a given BLE identifier."""

        registered_tag = self._repository.find_by_ble_identifier(ble_identifier)
        return registered_tag.tag_id if registered_tag is not None else None

    def get(self, tag_id: TagId) -> RegisteredTag | None:
        return self._repository.find_by_id(tag_id)

    def list_all(self) -> list[RegisteredTag]:
        return self._repository.list_all()
