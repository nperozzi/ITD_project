"""Abstract adapter for backend communication.

Implementations handle how the gateway talks to the central backend (MQTT, REST,
Socket.IO, ...). The gateway runtime only knows about this interface.
"""

from __future__ import annotations

import abc
from typing import Awaitable, Callable

from adapters.types import IncomingPayload, TagAdvertisement, TagId


IncomingPayloadHandler = Callable[[IncomingPayload], Awaitable[None]]


class AbstractBackendAdapter(abc.ABC):
    """Bidirectional channel to the backend."""

    @abc.abstractmethod
    async def start(self) -> None:
        """Open the channel and begin receiving incoming payloads."""

    @abc.abstractmethod
    async def stop(self) -> None:
        """Close the channel and release resources."""

    @abc.abstractmethod
    def set_incoming_payload_handler(self, handler: IncomingPayloadHandler) -> None:
        """Register the async callback invoked for each payload from the backend."""

    @abc.abstractmethod
    async def publish_acknowledge(self, tag_id: TagId) -> None:
        """Tell the backend that the tag successfully received its payload."""

    @abc.abstractmethod
    async def publish_advertisement(self, advertisement: TagAdvertisement) -> None:
        """Forward tag telemetry (battery, rssi) to the backend."""
