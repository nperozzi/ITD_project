"""Tests for TagRegistryService state transitions and BLE <-> tag_id mapping."""

from __future__ import annotations

import pytest

from db.base import Base
from db.session import build_engine, build_session_factory
from features.tag_registry.input import (
    RegisterTagInput,
    UpdateTagLinkInput,
    UpdateTelemetryInput,
)
from features.tag_registry.repository import TagRegistryRepository
from features.tag_registry.service import TagRegistryService
from features.tag_registry.types import TagConnectionState
from features.tag_registry import schema as _tag_registry_schema  # noqa: F401


@pytest.fixture()
def service() -> TagRegistryService:
    engine = build_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_factory = build_session_factory(engine)
    repository = TagRegistryRepository(session_factory=session_factory)
    return TagRegistryService(repository=repository)


def test_register_tag_is_idempotent(service: TagRegistryService) -> None:
    first = service.register_tag(RegisterTagInput(tag_id=1))
    second = service.register_tag(RegisterTagInput(tag_id=1))
    assert first.tag_id == 1
    assert second.tag_id == 1
    assert service.list_all() == [second]


def test_connection_state_transitions(service: TagRegistryService) -> None:
    service.register_tag(RegisterTagInput(tag_id=7))
    service.mark_connecting(7)
    assert service.get(7).connection_state is TagConnectionState.CONNECTING
    service.mark_connected(7)
    assert service.get(7).connection_state is TagConnectionState.CONNECTED
    service.mark_disconnected(7)
    assert service.get(7).connection_state is TagConnectionState.DISCONNECTED


def test_link_ble_identifier_enables_reverse_lookup(service: TagRegistryService) -> None:
    service.register_tag(RegisterTagInput(tag_id=3))
    service.link_ble_identifier(
        UpdateTagLinkInput(tag_id=3, ble_identifier="AA:BB:CC:DD:EE:FF")
    )
    assert service.resolve_tag_id_from_ble("AA:BB:CC:DD:EE:FF") == 3
    assert service.resolve_tag_id_from_ble("not-seen") is None


def test_record_telemetry_persists_latest_snapshot(service: TagRegistryService) -> None:
    service.register_tag(RegisterTagInput(tag_id=9))
    service.record_telemetry(
        UpdateTelemetryInput(tag_id=9, battery_percent=73, rssi=-54)
    )
    registered_tag = service.get(9)
    assert registered_tag is not None
    assert registered_tag.last_battery_percent == 73
    assert registered_tag.last_rssi == -54
