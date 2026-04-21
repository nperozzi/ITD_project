# Gateway

Python asyncio daemon that bridges the ESL backend (over MQTT) and ESP32 tag devices (over BLE).

Runs on a Raspberry Pi in production. Ships with a `MockTagAdapter` for container/dev runs that don't have BLE hardware.

## Architecture

See `src/` for the full layout:

- `adapters/backend/` - `AbstractBackendAdapter` plus `MVPBackendAdapter` (MQTT).
- `adapters/tag/` - `AbstractTagAdapter` plus `MVPTagAdapter` (bleak BLE) and `MockTagAdapter`.
- `features/tag_registry/` - which tags we know about, BLE mapping, connection state.
- `features/payload_delivery/` - queues and delivers payloads to tags with ack tracking.
- `features/telemetry/` - battery/rssi advertisements and heartbeats back to backend.
- `features/gateway_runtime/` - orchestrator that wires the loops together.

## Running

Dev (Docker, mock tag adapter):

```bash
bun run compose:up --build gateway
```

Host with real BLE (Pi):

```bash
cd apps/gateway
pip install -e .[dev]
GATEWAY_TAG_ADAPTER=ble python -m main
```

## Tests

```bash
cd apps/gateway
pip install -e .[dev]
pytest
```
