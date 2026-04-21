"""Runtime-level types for the gateway orchestrator."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class GatewayStatus(str, Enum):
    STARTING = "starting"
    ONLINE = "online"
    DEGRADED = "degraded"
    STOPPED = "stopped"


@dataclass
class GatewayRuntimeState:
    status: GatewayStatus = GatewayStatus.STARTING
