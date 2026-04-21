"""Tests for PayloadDeliveryService end-to-end using MockTagAdapter."""

from __future__ import annotations

import pytest

from adapters.backend.backend_adapter import (
    AbstractBackendAdapter,
    IncomingPayloadHandler,
)
from adapters.tag.implementation.mock_tag_adapter import MockTagAdapter
from adapters.types import IncomingPayload, TagAdvertisement
from db.base import Base
from db.session import build_engine, build_session_factory
from features.payload_delivery.input import EnqueuePayloadInput
from features.payload_delivery.repository import PayloadDeliveryRepository
from features.payload_delivery.service import PayloadDeliveryService
from features.payload_delivery.types import DeliveryState
from features.payload_delivery import schema as _payload_delivery_schema  # noqa: F401
from features.tag_registry.input import RegisterTagInput, UpdateTagLinkInput
from features.tag_registry.repository import TagRegistryRepository
from features.tag_registry.service import TagRegistryService
from features.tag_registry import schema as _tag_registry_schema  # noqa: F401


class _RecordingBackendAdapter(AbstractBackendAdapter):
    """Captures acks/advertisements so tests can assert on them."""

    def __init__(self) -> None:
        self.acknowledged_tag_ids: list[int] = []
        self.advertisements: list[TagAdvertisement] = []

    async def start(self) -> None: ...
    async def stop(self) -> None: ...
    def set_incoming_payload_handler(self, handler: IncomingPayloadHandler) -> None: ...
    async def publish_acknowledge(self, tag_id: int) -> None:
        self.acknowledged_tag_ids.append(tag_id)
    async def publish_advertisement(self, advertisement: TagAdvertisement) -> None:
        self.advertisements.append(advertisement)


@pytest.fixture()
def wiring():
    engine = build_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_factory = build_session_factory(engine)

    tag_registry_repository = TagRegistryRepository(session_factory=session_factory)
    tag_registry_service = TagRegistryService(repository=tag_registry_repository)

    payload_delivery_repository = PayloadDeliveryRepository(
        session_factory=session_factory
    )

    mock_tag_adapter = MockTagAdapter()
    backend_adapter = _RecordingBackendAdapter()

    service = PayloadDeliveryService(
        repository=payload_delivery_repository,
        tag_adapter=mock_tag_adapter,
        backend_adapter=backend_adapter,
        tag_registry_service=tag_registry_service,
    )

    # Register one tag with a BLE mapping so delivery can find it.
    tag_registry_service.register_tag(RegisterTagInput(tag_id=1))
    tag_registry_service.link_ble_identifier(
        UpdateTagLinkInput(tag_id=1, ble_identifier="AA:BB:CC:DD:EE:FF")
    )
    mock_tag_adapter.seed_tag("AA:BB:CC:DD:EE:FF")

    return {
        "service": service,
        "mock_tag_adapter": mock_tag_adapter,
        "backend_adapter": backend_adapter,
        "repository": payload_delivery_repository,
    }


async def test_enqueue_then_deliver_happy_path(wiring) -> None:
    service: PayloadDeliveryService = wiring["service"]
    backend_adapter: _RecordingBackendAdapter = wiring["backend_adapter"]
    repository: PayloadDeliveryRepository = wiring["repository"]

    pending_payload = service.enqueue(
        EnqueuePayloadInput(tag_id=1, title="Milk", final_price=199)
    )
    delivered = await service.attempt_next_delivery_for_tag(tag_id=1)

    assert delivered is True
    assert backend_adapter.acknowledged_tag_ids == [1]
    stored = repository.get(pending_payload.id)
    assert stored is not None
    assert stored.delivery_state is DeliveryState.ACKNOWLEDGED


async def test_connect_failure_resets_to_pending_for_retry(wiring) -> None:
    service: PayloadDeliveryService = wiring["service"]
    repository: PayloadDeliveryRepository = wiring["repository"]
    mock_tag_adapter: MockTagAdapter = wiring["mock_tag_adapter"]

    pending_payload = service.enqueue(
        EnqueuePayloadInput(tag_id=1, title="Bread", final_price=250)
    )
    mock_tag_adapter.force_next_connect_failure()

    delivered = await service.attempt_next_delivery_for_tag(tag_id=1)
    assert delivered is False

    stored = repository.get(pending_payload.id)
    assert stored is not None
    assert stored.delivery_state is DeliveryState.PENDING
    assert stored.attempt_count == 1

    # Second attempt with no injected failure should succeed.
    delivered_retry = await service.attempt_next_delivery_for_tag(tag_id=1)
    assert delivered_retry is True
    stored = repository.get(pending_payload.id)
    assert stored is not None
    assert stored.delivery_state is DeliveryState.ACKNOWLEDGED
    assert stored.attempt_count == 2


async def test_missing_ble_mapping_skips_delivery(wiring) -> None:
    service: PayloadDeliveryService = wiring["service"]

    # A tag that exists in the registry but has no BLE mapping.
    from features.tag_registry.input import RegisterTagInput as _RegisterTagInput
    from features.payload_delivery.input import EnqueuePayloadInput as _EnqueueInput

    wiring["service"]  # keep linter happy
    registry = wiring["service"]._tag_registry_service  # noqa: SLF001
    registry.register_tag(_RegisterTagInput(tag_id=2))

    service.enqueue(_EnqueueInput(tag_id=2, title="Eggs", final_price=399))
    delivered = await service.attempt_next_delivery_for_tag(tag_id=2)
    assert delivered is False
