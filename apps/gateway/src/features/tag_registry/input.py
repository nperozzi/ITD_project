"""Pydantic inputs for the tag registry feature."""

from __future__ import annotations

from pydantic import BaseModel, Field

from adapters.types import BleIdentifier, TagId


class RegisterTagInput(BaseModel):
    """Input for first-time registration of a tag with the gateway."""

    tag_id: TagId = Field(ge=1)
    ble_identifier: BleIdentifier | None = None


class UpdateTagLinkInput(BaseModel):
    """Input for associating an observed BLE device with an existing tag."""

    tag_id: TagId = Field(ge=1)
    ble_identifier: BleIdentifier


class UpdateTelemetryInput(BaseModel):
    """Input for storing latest telemetry snapshot for a tag."""

    tag_id: TagId = Field(ge=1)
    battery_percent: int | None = Field(default=None, ge=0, le=100)
    rssi: int | None = None
