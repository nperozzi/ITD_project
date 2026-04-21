"""Telemetry service.

Collects battery/rssi readings from the tag adapter and forwards them to the
backend adapter as advertisements. Also updates the tag registry's latest
snapshot so other features can read it without repeating BLE work.
"""

from __future__ import annotations

from adapters.backend.backend_adapter import AbstractBackendAdapter
from adapters.tag.tag_adapter import AbstractTagAdapter
from adapters.types import TagAdvertisement, TagId
from features.tag_registry.input import UpdateTelemetryInput
from features.tag_registry.service import TagRegistryService
from features.telemetry.input import ReportTelemetryInput
from logger import Logger


class TelemetryService:
    """Publishes tag telemetry to the backend adapter."""

    def __init__(
        self,
        tag_adapter: AbstractTagAdapter,
        backend_adapter: AbstractBackendAdapter,
        tag_registry_service: TagRegistryService,
        logger: Logger | None = None,
    ) -> None:
        self._tag_adapter = tag_adapter
        self._backend_adapter = backend_adapter
        self._tag_registry_service = tag_registry_service
        self._logger = logger or Logger("TelemetryService")

    async def report(self, params: ReportTelemetryInput) -> None:
        """Update the registry snapshot and publish an advertisement."""

        self._tag_registry_service.record_telemetry(
            UpdateTelemetryInput(
                tag_id=params.tag_id,
                battery_percent=params.battery_percent,
                rssi=params.rssi,
            )
        )
        await self._backend_adapter.publish_advertisement(
            TagAdvertisement(
                tag_id=params.tag_id,
                battery_percent=params.battery_percent,
                rssi=params.rssi,
            )
        )
        self._logger.debug(
            "report(tag_id=%s, battery=%s, rssi=%s)",
            params.tag_id,
            params.battery_percent,
            params.rssi,
        )

    async def refresh_for_tag(self, tag_id: TagId) -> None:
        """Ask the tag adapter for fresh telemetry and publish it."""

        registered_tag = self._tag_registry_service.get(tag_id)
        if registered_tag is None or registered_tag.ble_identifier is None:
            return
        battery_percent = await self._tag_adapter.read_battery_percent(
            registered_tag.ble_identifier
        )
        if battery_percent is None:
            return
        rssi = registered_tag.last_rssi if registered_tag.last_rssi is not None else -60
        await self.report(
            ReportTelemetryInput(
                tag_id=tag_id,
                battery_percent=battery_percent,
                rssi=rssi,
            )
        )
