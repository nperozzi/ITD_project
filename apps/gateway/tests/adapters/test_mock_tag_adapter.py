"""Contract tests for MockTagAdapter.

These double as a reference implementation of AbstractTagAdapter behavior.
Any new concrete tag adapter can reuse these cases as a sanity check.
"""

from __future__ import annotations

import pytest

from adapters.tag.implementation.mock_tag_adapter import MockTagAdapter


@pytest.fixture()
def adapter() -> MockTagAdapter:
    mock_tag_adapter = MockTagAdapter()
    mock_tag_adapter.seed_tag("AA:BB:CC:DD:EE:FF", battery_percent=77, rssi=-42)
    return mock_tag_adapter


async def test_scan_returns_seeded_tags(adapter: MockTagAdapter) -> None:
    await adapter.start()
    discovered_tags = await adapter.scan_once(scan_duration_seconds=0.01)
    assert len(discovered_tags) == 1
    assert discovered_tags[0].ble_identifier == "AA:BB:CC:DD:EE:FF"
    assert discovered_tags[0].rssi == -42


async def test_connect_write_ack_flow(adapter: MockTagAdapter) -> None:
    identifier = "AA:BB:CC:DD:EE:FF"
    assert await adapter.connect(identifier) is True
    assert await adapter.is_connected(identifier) is True
    assert await adapter.write_payload(identifier, b'{"title":"Milk","price":199}') is True
    assert await adapter.read_acknowledge(identifier) is True


async def test_forced_connect_failure_is_one_shot(adapter: MockTagAdapter) -> None:
    adapter.force_next_connect_failure()
    assert await adapter.connect("AA:BB:CC:DD:EE:FF") is False
    # Next attempt succeeds because the flag was consumed.
    assert await adapter.connect("AA:BB:CC:DD:EE:FF") is True


async def test_unknown_identifier_cannot_connect(adapter: MockTagAdapter) -> None:
    assert await adapter.connect("ZZ:ZZ:ZZ:ZZ:ZZ:ZZ") is False


async def test_read_battery_percent(adapter: MockTagAdapter) -> None:
    assert await adapter.read_battery_percent("AA:BB:CC:DD:EE:FF") == 77
    assert await adapter.read_battery_percent("ZZ:ZZ:ZZ:ZZ:ZZ:ZZ") is None


async def test_disconnect_handler_is_invoked(adapter: MockTagAdapter) -> None:
    disconnected_identifiers: list[str] = []

    async def handler(ble_identifier: str) -> None:
        disconnected_identifiers.append(ble_identifier)

    adapter.set_disconnect_handler(handler)
    await adapter.connect("AA:BB:CC:DD:EE:FF")
    await adapter.disconnect("AA:BB:CC:DD:EE:FF")
    assert disconnected_identifiers == ["AA:BB:CC:DD:EE:FF"]
