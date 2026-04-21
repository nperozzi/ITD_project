"""Domain contracts for the tag registry feature."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from adapters.types import BleIdentifier, TagId


class TagConnectionState(str, Enum):
    """Where a tag sits in the connect/deliver state machine."""

    UNKNOWN = "unknown"
    DISCOVERED = "discovered"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"


@dataclass(frozen=True)
class RegisteredTag:
    """A tag the gateway knows about, plus its latest state."""

    tag_id: TagId
    ble_identifier: BleIdentifier | None
    connection_state: TagConnectionState
    last_battery_percent: int | None
    last_rssi: int | None
