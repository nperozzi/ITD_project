"""Pydantic inputs for telemetry."""

from __future__ import annotations

from pydantic import BaseModel, Field

from adapters.types import TagId


class ReportTelemetryInput(BaseModel):
    """One telemetry reading for a tag, ready to be pushed to the backend."""

    tag_id: TagId = Field(ge=1)
    battery_percent: int = Field(ge=0, le=100)
    rssi: int = Field(ge=-120, le=0)
