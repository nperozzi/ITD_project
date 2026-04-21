"""Happy-path integration test for GatewayRuntimeService.

Wires all real services with MockTagAdapter and an in-memory fake backend,
then verifies that a backend-originated payload reaches the tag and that the
ack flows back out.
"""

from __future__ import annotations

import asyncio

import pytest

from adapters.backend.backend_adapter import (
    AbstractBackendAdapter,
    IncomingPayloadHandler,
)
from adapters.tag.implementation.mock_tag_adapter import MockTagAdapter
from adapters.types import IncomingPayload, TagAdvertisement
from config import GatewayConfig
from db.base import Base
from db.session import build_engine, build_session_factory
from features.gateway_runtime.service import GatewayRuntimeService
from features.gateway_runtime.types import GatewayStatus
from features.payload_delivery.repository import PayloadDeliveryRepository
from features.payload_delivery.service import PayloadDeliveryService
from features.payload_delivery import schema as _payload_delivery_schema  # noqa: F401
from features.tag_registry.input import RegisterTagInput, UpdateTagLinkInput
from features.tag_registry.repository import TagRegistryRepository
from features.tag_registry.service import TagRegistryService
from features.tag_registry import schema as _tag_registry_schema  # noqa: F401
from features.telemetry.service import TelemetryService


class _FakeBackendAdapter(AbstractBackendAdapter):
    def __init__(self) -> None:
        self.handler: IncomingPayloadHandler | None = None
        self.acknowledged_tag_ids: list[int] = []
        self.advertisements: list[TagAdvertisement] = []
        self.started = False

    async def start(self) -> None:
        self.started = True

    async def stop(self) -> None:
        self.started = False

    def set_incoming_payload_handler(self, handler: IncomingPayloadHandler) -> None:
        self.handler = handler

    async def publish_acknowledge(self, tag_id: int) -> None:
        self.acknowledged_tag_ids.append(tag_id)

    async def publish_advertisement(self, advertisement: TagAdvertisement) -> None:
        self.advertisements.append(advertisement)

    async def simulate_incoming(self, payload: IncomingPayload) -> None:
        assert self.handler is not None
        await self.handler(payload)


async def test_backend_payload_flows_through_to_tag_and_ack_returns() -> None:
    engine = build_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_factory = build_session_factory(engine)

    tag_registry_repository = TagRegistryRepository(session_factory=session_factory)
    tag_registry_service = TagRegistryService(repository=tag_registry_repository)
    payload_delivery_repository = PayloadDeliveryRepository(
        session_factory=session_factory
    )

    mock_tag_adapter = MockTagAdapter()
    mock_tag_adapter.seed_tag("AA:BB:CC:DD:EE:FF")
    fake_backend = _FakeBackendAdapter()

    payload_delivery_service = PayloadDeliveryService(
        repository=payload_delivery_repository,
        tag_adapter=mock_tag_adapter,
        backend_adapter=fake_backend,
        tag_registry_service=tag_registry_service,
    )
    telemetry_service = TelemetryService(
        tag_adapter=mock_tag_adapter,
        backend_adapter=fake_backend,
        tag_registry_service=tag_registry_service,
    )

    # Pre-register the tag with its BLE mapping so the delivery loop can reach it
    # without waiting for the scan loop.
    tag_registry_service.register_tag(RegisterTagInput(tag_id=1))
    tag_registry_service.link_ble_identifier(
        UpdateTagLinkInput(tag_id=1, ble_identifier="AA:BB:CC:DD:EE:FF")
    )

    # Tight loop intervals so the test finishes quickly.
    config = GatewayConfig(
        ble_scan_interval_seconds=0.05,
        payload_delivery_retry_seconds=0.05,
        heartbeat_interval_seconds=0.05,
    )

    runtime = GatewayRuntimeService(
        config=config,
        backend_adapter=fake_backend,
        tag_adapter=mock_tag_adapter,
        tag_registry_service=tag_registry_service,
        payload_delivery_service=payload_delivery_service,
        telemetry_service=telemetry_service,
    )

    await runtime.start()
    try:
        assert runtime.state.status is GatewayStatus.ONLINE

        await fake_backend.simulate_incoming(
            IncomingPayload(tag_id=1, title="Milk", final_price=199)
        )

        # Give the runtime a tick or two to process.
        for _ in range(20):
            if fake_backend.acknowledged_tag_ids:
                break
            await asyncio.sleep(0.05)

        assert fake_backend.acknowledged_tag_ids == [1]
        stored_bytes = mock_tag_adapter.state.tags_by_identifier[
            "AA:BB:CC:DD:EE:FF"
        ].last_payload_bytes
        assert stored_bytes is not None
        assert b"Milk" in stored_bytes
    finally:
        await runtime.stop()
        assert runtime.state.status is GatewayStatus.STOPPED
