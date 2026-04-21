"""Domain contracts for payload delivery."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from adapters.types import TagId


class DeliveryState(str, Enum):
    """Lifecycle of a single payload destined for a tag."""

    PENDING = "pending"
    DELIVERING = "delivering"
    ACKNOWLEDGED = "acknowledged"
    FAILED = "failed"


@dataclass(frozen=True)
class PendingPayload:
    """A payload queued for delivery to a tag."""

    id: int
    tag_id: TagId
    title: str
    final_price: float
    delivery_state: DeliveryState
    attempt_count: int
    last_attempted_at: datetime | None
    created_at: datetime
