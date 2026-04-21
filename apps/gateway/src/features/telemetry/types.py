"""Domain types for telemetry."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class TelemetrySnapshot:
    """Most-recent battery + rssi reading taken for a tag."""

    battery_percent: int | None
    rssi: int | None
    taken_at: datetime
