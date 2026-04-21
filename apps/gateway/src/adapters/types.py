"""Shared domain types exchanged across adapters and features."""

from __future__ import annotations

from dataclasses import dataclass


# Backend-assigned tag id (matches `Tag.id` in the backend's Postgres database).
TagId = int

# Opaque BLE identifier; usually a MAC address string on Linux or a UUID string
# on macOS. Treated as a string so adapters don't leak bleak/bluez types.
BleIdentifier = str


@dataclass(frozen=True)
class IncomingPayload:
    """Payload received from the backend, destined for a specific tag."""

    tag_id: TagId
    title: str
    final_price: int


@dataclass(frozen=True)
class DiscoveredTag:
    """A tag device observed during BLE scanning."""

    ble_identifier: BleIdentifier
    advertised_name: str
    rssi: int


@dataclass(frozen=True)
class TagAdvertisement:
    """Telemetry snapshot reported back to the backend for a tag."""

    tag_id: TagId
    battery_percent: int
    rssi: int
