"""In-memory tag adapter.

Behaves like a collection of well-behaved BLE tags that always accept payloads
and return an acknowledge. Used by the Docker compose dev flow (no host BLE
needed) and by tests as a reference implementation of AbstractTagAdapter.

Supports basic failure injection via `force_next_connect_failure` /
`force_next_write_failure` / `force_next_ack_failure` so tests can exercise
retry paths.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field

from adapters.tag.tag_adapter import AbstractTagAdapter, TagDisconnectHandler
from adapters.types import BleIdentifier, DiscoveredTag
from logger import Logger


@dataclass
class _MockTagState:
    """Per-tag state maintained by the mock adapter."""

    advertised_name: str
    rssi: int = -55
    battery_percent: int = 88
    is_connected: bool = False
    last_payload_bytes: bytes | None = None
    acknowledge_value: bool = False


@dataclass
class MockTagAdapterState:
    """Observable state for assertions in tests."""

    tags_by_identifier: dict[BleIdentifier, _MockTagState] = field(default_factory=dict)


class MockTagAdapter(AbstractTagAdapter):
    """In-memory AbstractTagAdapter for dev and tests."""

    def __init__(self, logger: Logger | None = None) -> None:
        self._logger = logger or Logger("MockTagAdapter")
        self._state = MockTagAdapterState()
        self._disconnect_handler: TagDisconnectHandler | None = None
        self._force_next_connect_failure = False
        self._force_next_write_failure = False
        self._force_next_ack_failure = False

    def seed_tag(
        self,
        ble_identifier: BleIdentifier,
        advertised_name: str = "TG_01",
        battery_percent: int = 88,
        rssi: int = -55,
    ) -> None:
        """Add a fake tag that will show up during scans."""

        self._state.tags_by_identifier[ble_identifier] = _MockTagState(
            advertised_name=advertised_name,
            battery_percent=battery_percent,
            rssi=rssi,
        )

    def force_next_connect_failure(self) -> None:
        self._force_next_connect_failure = True

    def force_next_write_failure(self) -> None:
        self._force_next_write_failure = True

    def force_next_ack_failure(self) -> None:
        self._force_next_ack_failure = True

    @property
    def state(self) -> MockTagAdapterState:
        return self._state

    async def start(self) -> None:
        self._logger.debug("start()")

    async def stop(self) -> None:
        self._logger.debug("stop()")

    async def scan_once(self, scan_duration_seconds: float) -> list[DiscoveredTag]:
        await asyncio.sleep(0)
        return [
            DiscoveredTag(
                ble_identifier=identifier,
                advertised_name=tag.advertised_name,
                rssi=tag.rssi,
            )
            for identifier, tag in self._state.tags_by_identifier.items()
        ]

    async def connect(self, ble_identifier: BleIdentifier) -> bool:
        if self._force_next_connect_failure:
            self._force_next_connect_failure = False
            return False
        tag = self._state.tags_by_identifier.get(ble_identifier)
        if tag is None:
            return False
        tag.is_connected = True
        return True

    async def disconnect(self, ble_identifier: BleIdentifier) -> None:
        tag = self._state.tags_by_identifier.get(ble_identifier)
        if tag is not None:
            tag.is_connected = False
        if self._disconnect_handler is not None:
            await self._disconnect_handler(ble_identifier)

    async def is_connected(self, ble_identifier: BleIdentifier) -> bool:
        tag = self._state.tags_by_identifier.get(ble_identifier)
        return tag is not None and tag.is_connected

    async def write_payload(
        self, ble_identifier: BleIdentifier, payload_bytes: bytes
    ) -> bool:
        if self._force_next_write_failure:
            self._force_next_write_failure = False
            return False
        tag = self._state.tags_by_identifier.get(ble_identifier)
        if tag is None or not tag.is_connected:
            return False
        tag.last_payload_bytes = payload_bytes
        tag.acknowledge_value = True
        return True

    async def read_acknowledge(self, ble_identifier: BleIdentifier) -> bool:
        if self._force_next_ack_failure:
            self._force_next_ack_failure = False
            return False
        tag = self._state.tags_by_identifier.get(ble_identifier)
        return tag is not None and tag.acknowledge_value

    async def read_battery_percent(self, ble_identifier: BleIdentifier) -> int | None:
        tag = self._state.tags_by_identifier.get(ble_identifier)
        return tag.battery_percent if tag is not None else None

    def set_disconnect_handler(self, handler: TagDisconnectHandler) -> None:
        self._disconnect_handler = handler
