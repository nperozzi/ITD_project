"""Tests for MVPBackendAdapter focusing on topic parsing + schema validation.

We avoid spinning up a real broker. Instead we construct the adapter and
invoke its paho-mqtt `on_message` callback directly with synthetic MQTTMessage
instances.
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass

import pytest

from adapters.backend.implementation.mqtt_backend_adapter import MVPBackendAdapter
from adapters.types import IncomingPayload


@dataclass
class _FakeMessage:
    """Shaped like paho.mqtt.client.MQTTMessage for our purposes."""

    topic: str
    payload: bytes


@pytest.fixture()
def adapter() -> MVPBackendAdapter:
    return MVPBackendAdapter(
        broker_host="localhost",
        broker_port=1883,
        client_id="test-gateway",
    )


async def test_on_message_dispatches_valid_payload(adapter: MVPBackendAdapter) -> None:
    received_payloads: list[IncomingPayload] = []

    async def handler(incoming: IncomingPayload) -> None:
        received_payloads.append(incoming)

    adapter.set_incoming_payload_handler(handler)
    adapter._asyncio_loop = asyncio.get_running_loop()  # noqa: SLF001

    message = _FakeMessage(
        topic="b-g/tag3/payload",
        payload=json.dumps({"tagId": 3, "title": "Milk", "finalPrice": 199}).encode(),
    )
    adapter._on_message(client=None, userdata=None, message=message)  # noqa: SLF001

    for _ in range(10):
        if received_payloads:
            break
        await asyncio.sleep(0.01)

    assert received_payloads == [
        IncomingPayload(tag_id=3, title="Milk", final_price=199)
    ]


async def test_on_message_drops_topic_tag_id_mismatch(
    adapter: MVPBackendAdapter,
) -> None:
    received_payloads: list[IncomingPayload] = []

    async def handler(incoming: IncomingPayload) -> None:
        received_payloads.append(incoming)

    adapter.set_incoming_payload_handler(handler)
    adapter._asyncio_loop = asyncio.get_running_loop()  # noqa: SLF001

    message = _FakeMessage(
        topic="b-g/tag3/payload",
        payload=json.dumps({"tagId": 99, "title": "Bread", "finalPrice": 299}).encode(),
    )
    adapter._on_message(client=None, userdata=None, message=message)  # noqa: SLF001
    await asyncio.sleep(0.05)
    assert received_payloads == []


async def test_on_message_drops_malformed_payload(
    adapter: MVPBackendAdapter,
) -> None:
    received_payloads: list[IncomingPayload] = []

    async def handler(incoming: IncomingPayload) -> None:
        received_payloads.append(incoming)

    adapter.set_incoming_payload_handler(handler)
    adapter._asyncio_loop = asyncio.get_running_loop()  # noqa: SLF001

    message = _FakeMessage(
        topic="b-g/tag3/payload",
        payload=b"not-json",
    )
    adapter._on_message(client=None, userdata=None, message=message)  # noqa: SLF001
    await asyncio.sleep(0.05)
    assert received_payloads == []


def test_on_message_ignores_unrelated_topic(adapter: MVPBackendAdapter) -> None:
    # Should just return; no handler invoked even if wired.
    message = _FakeMessage(
        topic="g-b/tag3/ack",
        payload=json.dumps({"tagId": 3, "ack": True}).encode(),
    )
    adapter._on_message(client=None, userdata=None, message=message)  # noqa: SLF001
