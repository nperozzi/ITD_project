"""Payload delivery service.

Coordinates the "ship this payload to a tag" flow:
1. Queue incoming payloads.
2. For each pending payload, ask the tag adapter to connect + write.
3. Confirm acknowledgement.
4. Notify the backend adapter on success; retry or fail on error.
"""

from __future__ import annotations

import json

from adapters.backend.backend_adapter import AbstractBackendAdapter
from adapters.tag.tag_adapter import AbstractTagAdapter
from features.payload_delivery.input import EnqueuePayloadInput
from features.payload_delivery.repository import PayloadDeliveryRepository
from features.payload_delivery.types import PendingPayload
from features.tag_registry.service import TagRegistryService
from logger import Logger


MAX_PAYLOAD_BYTES = 127


def encode_payload_bytes(title: str, final_price: float) -> bytes:
    """Serialize payload into the bytes the firmware writes to its e-paper.

    Format kept intentionally simple and human-readable for MVP. The firmware
    truncates at 127 bytes so we truncate proactively here.
    """

    encoded = json.dumps(
        {"title": title, "price": final_price},
        separators=(",", ":"),
    ).encode("utf-8")
    return encoded[:MAX_PAYLOAD_BYTES]


class PayloadDeliveryService:
    """Ships queued payloads from the backend to tag devices."""

    def __init__(
        self,
        repository: PayloadDeliveryRepository,
        tag_adapter: AbstractTagAdapter,
        backend_adapter: AbstractBackendAdapter,
        tag_registry_service: TagRegistryService,
        logger: Logger | None = None,
    ) -> None:
        self._repository = repository
        self._tag_adapter = tag_adapter
        self._backend_adapter = backend_adapter
        self._tag_registry_service = tag_registry_service
        self._logger = logger or Logger("PayloadDeliveryService")

    def enqueue(self, params: EnqueuePayloadInput) -> PendingPayload:
        """Store an incoming payload so the delivery loop can pick it up."""

        pending_payload = self._repository.enqueue(
            tag_id=params.tag_id,
            title=params.title,
            final_price=params.final_price,
        )
        self._logger.debug(
            "enqueue(tag_id=%s, price=%s) -> id=%s",
            params.tag_id,
            params.final_price,
            pending_payload.id,
        )
        return pending_payload

    async def attempt_next_delivery_for_tag(self, tag_id: int) -> bool:
        """Try to deliver the next pending payload for a given tag.

        Returns True if a payload was acknowledged in this attempt.
        """

        pending_payload = self._repository.find_next_pending_for_tag(tag_id)
        if pending_payload is None:
            return False

        registered_tag = self._tag_registry_service.get(tag_id)
        if registered_tag is None or registered_tag.ble_identifier is None:
            self._logger.debug(
                "attempt_next_delivery_for_tag(%s): no BLE mapping yet", tag_id
            )
            return False

        self._repository.mark_delivering(pending_payload.id)
        self._tag_registry_service.mark_connecting(tag_id)

        connected_ok = await self._tag_adapter.connect(registered_tag.ble_identifier)
        if not connected_ok:
            self._logger.warning("connect failed for tag %s", tag_id)
            self._repository.reset_to_pending(pending_payload.id)
            self._tag_registry_service.mark_disconnected(tag_id)
            return False

        self._tag_registry_service.mark_connected(tag_id)

        payload_bytes = encode_payload_bytes(
            title=pending_payload.title,
            final_price=pending_payload.final_price,
        )

        write_ok = await self._tag_adapter.write_payload(
            registered_tag.ble_identifier, payload_bytes
        )
        if not write_ok:
            self._logger.warning("write failed for tag %s", tag_id)
            self._repository.reset_to_pending(pending_payload.id)
            return False

        acknowledged = await self._tag_adapter.read_acknowledge(
            registered_tag.ble_identifier
        )
        if not acknowledged:
            self._logger.warning("no ack from tag %s", tag_id)
            self._repository.reset_to_pending(pending_payload.id)
            return False

        self._repository.mark_acknowledged(pending_payload.id)
        await self._backend_adapter.publish_acknowledge(tag_id)
        self._logger.info("delivered payload id=%s to tag %s", pending_payload.id, tag_id)
        return True
