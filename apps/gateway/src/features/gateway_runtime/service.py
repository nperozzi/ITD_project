"""Gateway runtime orchestrator.

Wires together the backend adapter, tag adapter, and feature services into the
async loops that make the daemon do its job:

- payload_ingress: handler invoked when the backend adapter delivers a payload.
- scan_loop: periodically scans BLE to keep the tag registry fresh.
- delivery_loop: repeatedly tries to deliver pending payloads.
- telemetry_loop: periodically refreshes tag telemetry.

Each loop is cancellable so `stop()` leaves the daemon in a clean state.
"""

from __future__ import annotations

import asyncio

from adapters.backend.backend_adapter import AbstractBackendAdapter
from adapters.tag.tag_adapter import AbstractTagAdapter
from adapters.types import IncomingPayload
from config import GatewayConfig
from features.gateway_runtime.types import GatewayRuntimeState, GatewayStatus
from features.payload_delivery.input import EnqueuePayloadInput
from features.payload_delivery.service import PayloadDeliveryService
from features.tag_registry.input import RegisterTagInput, UpdateTagLinkInput
from features.tag_registry.service import TagRegistryService
from features.telemetry.service import TelemetryService
from logger import Logger


class GatewayRuntimeService:
    """Top-level orchestrator. Owns the event loops and lifecycle."""

    def __init__(
        self,
        config: GatewayConfig,
        backend_adapter: AbstractBackendAdapter,
        tag_adapter: AbstractTagAdapter,
        tag_registry_service: TagRegistryService,
        payload_delivery_service: PayloadDeliveryService,
        telemetry_service: TelemetryService,
        logger: Logger | None = None,
    ) -> None:
        self._config = config
        self._backend_adapter = backend_adapter
        self._tag_adapter = tag_adapter
        self._tag_registry_service = tag_registry_service
        self._payload_delivery_service = payload_delivery_service
        self._telemetry_service = telemetry_service
        self._logger = logger or Logger("GatewayRuntimeService")
        self._state = GatewayRuntimeState()
        self._background_tasks: list[asyncio.Task] = []

    @property
    def state(self) -> GatewayRuntimeState:
        return self._state

    async def start(self) -> None:
        """Start adapters, register the payload handler, and launch loops."""

        self._logger.info("gateway starting")
        await self._backend_adapter.start()
        await self._tag_adapter.start()
        self._backend_adapter.set_incoming_payload_handler(self._on_payload_ingress)

        self._background_tasks = [
            asyncio.create_task(self._scan_loop(), name="scan_loop"),
            asyncio.create_task(self._delivery_loop(), name="delivery_loop"),
            asyncio.create_task(self._telemetry_loop(), name="telemetry_loop"),
        ]
        self._state.status = GatewayStatus.ONLINE

    async def stop(self) -> None:
        """Cancel all loops and close adapters."""

        self._logger.info("gateway stopping")
        for task in self._background_tasks:
            task.cancel()
        for task in self._background_tasks:
            try:
                await task
            except asyncio.CancelledError:
                pass
        self._background_tasks.clear()

        await self._tag_adapter.stop()
        await self._backend_adapter.stop()
        self._state.status = GatewayStatus.STOPPED

    async def _on_payload_ingress(self, payload: IncomingPayload) -> None:
        """Queue the payload and make a single immediate delivery attempt."""

        self._logger.info(
            "payload received tag=%s title=%r price=%s",
            payload.tag_id,
            payload.title,
            payload.final_price,
        )
        self._tag_registry_service.register_tag(
            RegisterTagInput(tag_id=payload.tag_id)
        )
        self._payload_delivery_service.enqueue(
            EnqueuePayloadInput(
                tag_id=payload.tag_id,
                title=payload.title,
                final_price=payload.final_price,
            )
        )
        await self._payload_delivery_service.attempt_next_delivery_for_tag(
            payload.tag_id
        )

    async def _scan_loop(self) -> None:
        """Periodically scan for tags and link discovered BLE identifiers.

        MVP policy: if only one tag is registered and we see exactly one
        device advertising the tag service, auto-link them. More sophisticated
        mapping (e.g. BLE name encodes tag id) is left to future iterations.
        """

        while True:
            try:
                discovered_tags = await self._tag_adapter.scan_once(
                    scan_duration_seconds=self._config.ble_scan_interval_seconds
                )
                self._auto_link_single_tag(discovered_tags)
            except Exception:  # noqa: BLE001
                self._logger.error("scan_loop error", exc_info=True)
            await asyncio.sleep(self._config.ble_scan_interval_seconds)

    def _auto_link_single_tag(self, discovered_tags) -> None:
        registered_tags_without_ble = [
            registered_tag
            for registered_tag in self._tag_registry_service.list_all()
            if registered_tag.ble_identifier is None
        ]
        if len(registered_tags_without_ble) == 1 and len(discovered_tags) == 1:
            only_registered_tag = registered_tags_without_ble[0]
            only_discovered_tag = discovered_tags[0]
            self._tag_registry_service.link_ble_identifier(
                UpdateTagLinkInput(
                    tag_id=only_registered_tag.tag_id,
                    ble_identifier=only_discovered_tag.ble_identifier,
                )
            )

    async def _delivery_loop(self) -> None:
        """Retry pending payloads across all known tags."""

        while True:
            try:
                for registered_tag in self._tag_registry_service.list_all():
                    if registered_tag.ble_identifier is None:
                        continue
                    await self._payload_delivery_service.attempt_next_delivery_for_tag(
                        registered_tag.tag_id
                    )
            except Exception:  # noqa: BLE001
                self._logger.error("delivery_loop error", exc_info=True)
            await asyncio.sleep(self._config.payload_delivery_retry_seconds)

    async def _telemetry_loop(self) -> None:
        """Periodically refresh tag telemetry and push advertisements."""

        while True:
            try:
                for registered_tag in self._tag_registry_service.list_all():
                    await self._telemetry_service.refresh_for_tag(
                        registered_tag.tag_id
                    )
            except Exception:  # noqa: BLE001
                self._logger.error("telemetry_loop error", exc_info=True)
            await asyncio.sleep(self._config.heartbeat_interval_seconds)
