"""Gateway configuration loaded from environment variables.

Uses Pydantic Settings so values can be overridden in Docker, on a Pi host, or in tests
without code changes. Defaults match the existing docker-compose / mosquitto setup.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


TagAdapterKind = Literal["mock", "ble"]


class GatewayConfig(BaseSettings):
    """Runtime configuration for the gateway daemon."""

    model_config = SettingsConfigDict(
        env_prefix="GATEWAY_",
        env_file=".env",
        extra="ignore",
    )

    gateway_id: int = Field(
        default=1,
        description="Backend-assigned gateway id used for heartbeats and logs.",
    )

    mqtt_broker_host: str = Field(default="mosquitto")
    mqtt_broker_port: int = Field(default=1883)
    mqtt_client_id: str = Field(default="gateway-1")

    database_url: str = Field(
        default="sqlite:///./gateway.db",
        description="SQLAlchemy URL. SQLite by default; can be pointed elsewhere.",
    )

    tag_adapter: TagAdapterKind = Field(
        default="mock",
        description="Which AbstractTagAdapter implementation to wire at runtime.",
    )

    ble_scan_interval_seconds: float = Field(default=5.0)
    payload_delivery_retry_seconds: float = Field(default=3.0)
    heartbeat_interval_seconds: float = Field(default=30.0)

    log_level: str = Field(default="INFO")
