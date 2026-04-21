"""DI composition root.

One place where concrete types are wired together. Every other module receives
its dependencies via constructor injection, matching the service guide.

Exposes `build_container(config)` which returns a `Container` with fully wired
services. `main.py` picks the tag adapter based on `config.tag_adapter`.
"""

from __future__ import annotations

from dataclasses import dataclass

from adapters.backend.backend_adapter import AbstractBackendAdapter
from adapters.backend.implementation.mqtt_backend_adapter import MVPBackendAdapter
from adapters.tag.implementation.mock_tag_adapter import MockTagAdapter
from adapters.tag.tag_adapter import AbstractTagAdapter
from config import GatewayConfig
from db.session import build_engine, build_session_factory
from features.gateway_runtime.service import GatewayRuntimeService
from features.payload_delivery.repository import PayloadDeliveryRepository
from features.payload_delivery.service import PayloadDeliveryService
from features.payload_delivery import schema as _payload_delivery_schema  # noqa: F401
from features.tag_registry.repository import TagRegistryRepository
from features.tag_registry.service import TagRegistryService
from features.tag_registry import schema as _tag_registry_schema  # noqa: F401
from features.telemetry.service import TelemetryService
from logger import Logger


@dataclass
class Container:
    """Fully-wired application graph."""

    config: GatewayConfig
    backend_adapter: AbstractBackendAdapter
    tag_adapter: AbstractTagAdapter
    tag_registry_service: TagRegistryService
    payload_delivery_service: PayloadDeliveryService
    telemetry_service: TelemetryService
    gateway_runtime_service: GatewayRuntimeService


def _build_tag_adapter(config: GatewayConfig) -> AbstractTagAdapter:
    if config.tag_adapter == "ble":
        # Imported lazily so `bleak` isn't required for `mock` runs.
        from adapters.tag.implementation.ble_tag_adapter import MVPTagAdapter

        return MVPTagAdapter()
    return MockTagAdapter()


def build_container(config: GatewayConfig) -> Container:
    """Wire up the entire application graph from a config object."""

    root_logger = Logger("gateway", level=config.log_level)

    engine = build_engine(config.database_url)
    session_factory = build_session_factory(engine)

    tag_registry_repository = TagRegistryRepository(session_factory=session_factory)
    tag_registry_service = TagRegistryService(repository=tag_registry_repository)

    payload_delivery_repository = PayloadDeliveryRepository(
        session_factory=session_factory
    )

    backend_adapter = MVPBackendAdapter(
        broker_host=config.mqtt_broker_host,
        broker_port=config.mqtt_broker_port,
        client_id=config.mqtt_client_id,
    )
    tag_adapter = _build_tag_adapter(config)

    payload_delivery_service = PayloadDeliveryService(
        repository=payload_delivery_repository,
        tag_adapter=tag_adapter,
        backend_adapter=backend_adapter,
        tag_registry_service=tag_registry_service,
    )
    telemetry_service = TelemetryService(
        tag_adapter=tag_adapter,
        backend_adapter=backend_adapter,
        tag_registry_service=tag_registry_service,
    )
    gateway_runtime_service = GatewayRuntimeService(
        config=config,
        backend_adapter=backend_adapter,
        tag_adapter=tag_adapter,
        tag_registry_service=tag_registry_service,
        payload_delivery_service=payload_delivery_service,
        telemetry_service=telemetry_service,
    )

    root_logger.info(
        "container built (tag_adapter=%s, broker=%s:%s, db=%s)",
        config.tag_adapter,
        config.mqtt_broker_host,
        config.mqtt_broker_port,
        config.database_url,
    )

    return Container(
        config=config,
        backend_adapter=backend_adapter,
        tag_adapter=tag_adapter,
        tag_registry_service=tag_registry_service,
        payload_delivery_service=payload_delivery_service,
        telemetry_service=telemetry_service,
        gateway_runtime_service=gateway_runtime_service,
    )
