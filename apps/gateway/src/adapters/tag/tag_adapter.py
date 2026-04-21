"""Abstract adapter for tag devices.

Implementations handle how the gateway interacts with label devices (BLE, mock,
USB, ...). Kept high-level enough to support non-BLE future transports.
"""

from __future__ import annotations

import abc
from typing import Awaitable, Callable

from adapters.types import BleIdentifier, DiscoveredTag


TagDisconnectHandler = Callable[[BleIdentifier], Awaitable[None]]


class AbstractTagAdapter(abc.ABC):
    """Low-level channel to individual tag devices."""

    @abc.abstractmethod
    async def start(self) -> None:
        """Initialize the transport (start BLE stack, mock state, ...)."""

    @abc.abstractmethod
    async def stop(self) -> None:
        """Shut down the transport cleanly."""

    @abc.abstractmethod
    async def scan_once(self, scan_duration_seconds: float) -> list[DiscoveredTag]:
        """Return tags seen during a single scan window."""

    @abc.abstractmethod
    async def connect(self, ble_identifier: BleIdentifier) -> bool:
        """Open a connection to a specific tag. Returns True on success."""

    @abc.abstractmethod
    async def disconnect(self, ble_identifier: BleIdentifier) -> None:
        """Close the connection to a tag."""

    @abc.abstractmethod
    async def is_connected(self, ble_identifier: BleIdentifier) -> bool:
        """Return True if the adapter currently holds an open link to the tag."""

    @abc.abstractmethod
    async def write_payload(
        self, ble_identifier: BleIdentifier, payload_bytes: bytes
    ) -> bool:
        """Write the payload characteristic on the tag.

        Returns True when the write itself succeeded. Callers must separately
        confirm the tag's acknowledge characteristic.
        """

    @abc.abstractmethod
    async def read_acknowledge(self, ble_identifier: BleIdentifier) -> bool:
        """Read the acknowledge characteristic; True means the tag accepted."""

    @abc.abstractmethod
    async def read_battery_percent(self, ble_identifier: BleIdentifier) -> int | None:
        """Read a battery percentage (0-100) if the tag exposes one."""

    @abc.abstractmethod
    def set_disconnect_handler(self, handler: TagDisconnectHandler) -> None:
        """Register async callback invoked when a tag drops its connection."""
