"""MVPBackendAdapter: MQTT implementation of AbstractBackendAdapter.

Topic contract (matches existing backend `mqtt_client.py`):

    backend -> gateway : b-g/tag{tag_id}/payload         { tagId, title, finalPrice }
    gateway -> backend : g-b/tag{tag_id}/ack             { tagId, ack: true }
    gateway -> backend : b-g/tag{tag_id}/advertisement   { battery, rssi }

paho-mqtt callbacks run on a worker thread owned by the client. We bridge them
onto the asyncio loop used by the gateway so features stay purely async.
"""

from __future__ import annotations

import asyncio
import json
import re
from typing import cast

import paho.mqtt.client as mqtt
from pydantic import BaseModel, Field, ValidationError

from adapters.backend.backend_adapter import (
    AbstractBackendAdapter,
    IncomingPayloadHandler,
)
from adapters.types import IncomingPayload, TagAdvertisement, TagId
from logger import Logger


PAYLOAD_TOPIC_PATTERN = re.compile(r"^b-g/tag(?P<tag_id>\d+)/payload$")
PAYLOAD_TOPIC_SUBSCRIPTION = "b-g/tag+/payload"


class _IncomingPayloadWireFormat(BaseModel):
    """What the backend publishes on `b-g/tag{id}/payload`."""

    tag_id: TagId = Field(alias="tagId")
    title: str
    final_price: int = Field(alias="finalPrice")

    model_config = {"populate_by_name": True}


class MVPBackendAdapter(AbstractBackendAdapter):
    """Backend adapter using MQTT as the transport."""

    def __init__(
        self,
        broker_host: str,
        broker_port: int,
        client_id: str,
        logger: Logger | None = None,
    ) -> None:
        self._broker_host = broker_host
        self._broker_port = broker_port
        self._client_id = client_id
        self._logger = logger or Logger("MVPBackendAdapter")

        self._mqtt_client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=client_id,
        )
        self._mqtt_client.on_connect = self._on_connect
        self._mqtt_client.on_message = self._on_message

        self._incoming_payload_handler: IncomingPayloadHandler | None = None
        self._asyncio_loop: asyncio.AbstractEventLoop | None = None

    async def start(self) -> None:
        self._asyncio_loop = asyncio.get_running_loop()
        self._logger.info(
            "connecting to mqtt broker %s:%s", self._broker_host, self._broker_port
        )
        self._mqtt_client.connect(self._broker_host, self._broker_port, keepalive=60)
        self._mqtt_client.loop_start()

    async def stop(self) -> None:
        self._mqtt_client.loop_stop()
        self._mqtt_client.disconnect()

    def set_incoming_payload_handler(self, handler: IncomingPayloadHandler) -> None:
        self._incoming_payload_handler = handler

    async def publish_acknowledge(self, tag_id: TagId) -> None:
        topic = f"g-b/tag{tag_id}/ack"
        payload_json = json.dumps({"tagId": tag_id, "ack": True})
        self._mqtt_client.publish(topic, payload_json, qos=1)

    async def publish_advertisement(self, advertisement: TagAdvertisement) -> None:
        topic = f"b-g/tag{advertisement.tag_id}/advertisement"
        payload_json = json.dumps(
            {"battery": advertisement.battery_percent, "rssi": advertisement.rssi}
        )
        self._mqtt_client.publish(topic, payload_json, qos=1, retain=True)

    # ---- paho-mqtt callbacks (run on mqtt worker thread) ----

    def _on_connect(
        self,
        client: mqtt.Client,
        userdata: object,
        flags: object,
        reason_code: object,
        properties: object = None,
    ) -> None:
        self._logger.info("mqtt connected; subscribing")
        client.subscribe(PAYLOAD_TOPIC_SUBSCRIPTION, qos=1)

    def _on_message(
        self, client: mqtt.Client, userdata: object, message: mqtt.MQTTMessage
    ) -> None:
        topic_match = PAYLOAD_TOPIC_PATTERN.match(message.topic)
        if topic_match is None:
            return
        expected_tag_id = int(topic_match.group("tag_id"))

        try:
            decoded_payload = _IncomingPayloadWireFormat.model_validate_json(
                message.payload.decode("utf-8")
            )
        except (UnicodeDecodeError, ValidationError) as validation_error:
            self._logger.warning(
                "dropping malformed payload on %s: %s",
                message.topic,
                validation_error,
            )
            return

        if decoded_payload.tag_id != expected_tag_id:
            self._logger.warning(
                "topic tag id %s does not match payload tag id %s; dropping",
                expected_tag_id,
                decoded_payload.tag_id,
            )
            return

        incoming_payload = IncomingPayload(
            tag_id=decoded_payload.tag_id,
            title=decoded_payload.title,
            final_price=decoded_payload.final_price,
        )
        self._dispatch_to_asyncio(incoming_payload)

    def _dispatch_to_asyncio(self, incoming_payload: IncomingPayload) -> None:
        if self._incoming_payload_handler is None or self._asyncio_loop is None:
            self._logger.debug("no handler wired yet; dropping payload")
            return
        handler = self._incoming_payload_handler
        asyncio.run_coroutine_threadsafe(
            cast(asyncio.Future, handler(incoming_payload)),
            self._asyncio_loop,
        )
