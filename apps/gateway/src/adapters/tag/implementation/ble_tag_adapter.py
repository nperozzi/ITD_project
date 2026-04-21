"""MVPTagAdapter: real BLE implementation of AbstractTagAdapter using bleak.

Matches the ESP32 firmware in `apps/tag/esp32h2_tag/esp32h2_tag.ino`:

    DEVICE_NAME                      = "TG_01"
    TAG_SERVICE_UUID                 = B8E4F533-E530-4D1D-B54C-0D5D5A9A5A4B
    PAYLOAD_CHARACTERISTIC_UUID      = 99CFD161-DCD8-4BEB-86B2-48673AEAE284   (WRITE)
    ACKNOWLEDGE_CHARACTERISTIC_UUID  = 53B04C05-A5E1-475B-BC9E-61C00112ACDE   (READ/NOTIFY)

No automated tests: `bleak` needs a real BLE radio and at least one powered ESP32
flashed with the firmware. Manual verification steps live in `apps/gateway/README.md`.
"""

from __future__ import annotations

import asyncio

from bleak import BleakClient, BleakScanner

from adapters.tag.tag_adapter import AbstractTagAdapter, TagDisconnectHandler
from adapters.types import BleIdentifier, DiscoveredTag
from logger import Logger


TAG_SERVICE_UUID = "b8e4f533-e530-4d1d-b54c-0d5d5a9a5a4b"
PAYLOAD_CHARACTERISTIC_UUID = "99cfd161-dcd8-4beb-86b2-48673aeae284"
ACKNOWLEDGE_CHARACTERISTIC_UUID = "53b04c05-a5e1-475b-bc9e-61c00112acde"
TAG_ADVERTISED_NAME_PREFIX = "TG_"


class MVPTagAdapter(AbstractTagAdapter):
    """Real BLE adapter. One BleakClient per tag; filtered by service UUID."""

    def __init__(self, logger: Logger | None = None) -> None:
        self._logger = logger or Logger("MVPTagAdapter")
        self._clients_by_identifier: dict[BleIdentifier, BleakClient] = {}
        self._disconnect_handler: TagDisconnectHandler | None = None
        self._asyncio_loop: asyncio.AbstractEventLoop | None = None

    async def start(self) -> None:
        self._asyncio_loop = asyncio.get_running_loop()
        self._logger.info("bleak adapter ready")

    async def stop(self) -> None:
        for identifier in list(self._clients_by_identifier.keys()):
            await self.disconnect(identifier)

    async def scan_once(self, scan_duration_seconds: float) -> list[DiscoveredTag]:
        discovered_devices = await BleakScanner.discover(
            timeout=scan_duration_seconds,
            service_uuids=[TAG_SERVICE_UUID],
            return_adv=True,
        )
        result: list[DiscoveredTag] = []
        for ble_device, advertisement_data in discovered_devices.values():
            advertised_name = ble_device.name or advertisement_data.local_name or ""
            if not advertised_name.startswith(TAG_ADVERTISED_NAME_PREFIX):
                continue
            result.append(
                DiscoveredTag(
                    ble_identifier=ble_device.address,
                    advertised_name=advertised_name,
                    rssi=int(advertisement_data.rssi or 0),
                )
            )
        return result

    async def connect(self, ble_identifier: BleIdentifier) -> bool:
        existing_client = self._clients_by_identifier.get(ble_identifier)
        if existing_client is not None and existing_client.is_connected:
            return True

        client = BleakClient(
            ble_identifier,
            disconnected_callback=self._make_disconnect_callback(ble_identifier),
        )
        try:
            await client.connect()
        except Exception:  # noqa: BLE001
            self._logger.error("bleak connect failed for %s", ble_identifier, exc_info=True)
            return False

        self._clients_by_identifier[ble_identifier] = client
        return client.is_connected

    async def disconnect(self, ble_identifier: BleIdentifier) -> None:
        client = self._clients_by_identifier.pop(ble_identifier, None)
        if client is None:
            return
        try:
            await client.disconnect()
        except Exception:  # noqa: BLE001
            self._logger.warning("disconnect error for %s", ble_identifier)

    async def is_connected(self, ble_identifier: BleIdentifier) -> bool:
        client = self._clients_by_identifier.get(ble_identifier)
        return client is not None and client.is_connected

    async def write_payload(
        self, ble_identifier: BleIdentifier, payload_bytes: bytes
    ) -> bool:
        client = self._clients_by_identifier.get(ble_identifier)
        if client is None or not client.is_connected:
            return False
        try:
            await client.write_gatt_char(
                PAYLOAD_CHARACTERISTIC_UUID,
                payload_bytes,
                response=True,
            )
            return True
        except Exception:  # noqa: BLE001
            self._logger.error(
                "bleak write_gatt_char failed for %s", ble_identifier, exc_info=True
            )
            return False

    async def read_acknowledge(self, ble_identifier: BleIdentifier) -> bool:
        client = self._clients_by_identifier.get(ble_identifier)
        if client is None or not client.is_connected:
            return False
        try:
            raw_value = await client.read_gatt_char(ACKNOWLEDGE_CHARACTERISTIC_UUID)
        except Exception:  # noqa: BLE001
            self._logger.error(
                "bleak read_gatt_char failed for %s", ble_identifier, exc_info=True
            )
            return False
        decoded = raw_value.decode("utf-8", errors="ignore").strip().lower()
        return decoded == "true"

    async def read_battery_percent(self, ble_identifier: BleIdentifier) -> int | None:
        # Firmware does not currently expose a battery characteristic. Hook for
        # when it does; returns None so callers can fall back to cached telemetry.
        return None

    def set_disconnect_handler(self, handler: TagDisconnectHandler) -> None:
        self._disconnect_handler = handler

    def _make_disconnect_callback(self, ble_identifier: BleIdentifier):
        def on_disconnect(_client: BleakClient) -> None:
            self._clients_by_identifier.pop(ble_identifier, None)
            if self._disconnect_handler is None or self._asyncio_loop is None:
                return
            asyncio.run_coroutine_threadsafe(
                self._disconnect_handler(ble_identifier),
                self._asyncio_loop,
            )
        return on_disconnect
