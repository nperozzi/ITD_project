# Gateway

Python asyncio daemon that bridges the ESL backend (over MQTT) and ESP32 tag devices (over BLE).

Runs on a Raspberry Pi in production. Ships with a `MockTagAdapter` for container/dev runs that don't have BLE hardware.

## Architecture

```
backend  <--MQTT-->  gateway  <--BLE-->  tag (ESP32)
                      |
                      +-- MVPBackendAdapter (paho-mqtt)
                      +-- MVPTagAdapter (bleak) | MockTagAdapter
                      +-- features/ (tag_registry, payload_delivery, telemetry, gateway_runtime)
                      +-- SQLite (via SQLAlchemy + Alembic)
```

Slot convention:

- `features/<feature>/{types,input,schema,repository,service}.py`
- `adapters/<domain>/<domain>_adapter.py` (abstract) + `implementation/*.py` (concrete).

### Key modules

- `adapters/backend/` - `AbstractBackendAdapter` plus `MVPBackendAdapter` (MQTT).
- `adapters/tag/` - `AbstractTagAdapter` plus `MVPTagAdapter` (bleak BLE) and `MockTagAdapter`.
- `features/tag_registry/` - which tags we know about, BLE mapping, connection state.
- `features/payload_delivery/` - queues and delivers payloads to tags with ack tracking.
- `features/telemetry/` - battery/rssi advertisements and heartbeats back to backend.
- `features/gateway_runtime/` - orchestrator that wires the loops together.
- `container.py` - single composition root; `main.py` reads config, runs migrations, starts the runtime.

## Configuration

All settings are read via Pydantic `BaseSettings` with prefix `GATEWAY_`:

| Variable                  | Default                       | Description                         |
| ------------------------- | ----------------------------- | ----------------------------------- |
| `GATEWAY_MQTT_BROKER_HOST`| `mosquitto`                   | MQTT broker host                    |
| `GATEWAY_MQTT_BROKER_PORT`| `1883`                        | MQTT broker port                    |
| `GATEWAY_MQTT_CLIENT_ID`  | `gateway-1`                   | Client identifier                   |
| `GATEWAY_DATABASE_URL`    | `sqlite:///./gateway.db`      | SQLAlchemy URL                      |
| `GATEWAY_TAG_ADAPTER`     | `mock`                        | `mock` or `ble`                     |
| `GATEWAY_SCAN_INTERVAL_SECONDS`     | `5`                 | BLE scan cadence                    |
| `GATEWAY_DELIVERY_INTERVAL_SECONDS` | `2`                 | Pending-payload drain cadence       |
| `GATEWAY_TELEMETRY_INTERVAL_SECONDS`| `30`                | Advertisement/heartbeat cadence     |
| `GATEWAY_LOG_LEVEL`       | `INFO`                        | Python logging level                |

## Running

### Dev (Docker, mock tag adapter)

```bash
bun run compose:up --build gateway
```

The compose service mounts a named volume at `/data` for the SQLite file and defaults `GATEWAY_TAG_ADAPTER=mock`.

### Host with real BLE (Raspberry Pi)

```bash
cd apps/gateway
pip install -e .[dev]
GATEWAY_TAG_ADAPTER=ble GATEWAY_MQTT_BROKER_HOST=<backend-host> python -m main
```

On Linux, `bleak` uses BlueZ - ensure `bluetooth` is running and the user has access (`sudo usermod -aG bluetooth $USER` and log back in).

### MQTT topic contract

- Backend -> gateway: `b-g/tag{tagId}/payload` with `{tagId, title, finalPrice}`.
- Gateway -> backend: `g-b/tag{tagId}/ack` with `{tagId, ack: true}`.
- Gateway -> backend: `b-g/tag{tagId}/advertisement` with `{battery, rssi}` (retained).

### BLE contract (matches `apps/tag/esp32h2_tag/esp32h2_tag.ino`)

- Device name prefix: `TG_`
- Service UUID: `B8E4F533-E530-4D1D-B54C-0D5D5A9A5A4B`
- Payload characteristic (write): `99CFD161-DCD8-4BEB-86B2-48673AEAE284`
- Acknowledge characteristic (read/notify): `53B04C05-A5E1-475B-BC9E-61C00112ACDE`

## Tests

```bash
cd apps/gateway
pip install -e .[dev]
pytest
```

Tests cover `tag_registry`, `payload_delivery`, `gateway_runtime`, the MQTT backend adapter, and the `MockTagAdapter` contract. The real BLE adapter requires hardware and is verified manually.

### Manual BLE verification

1. Flash the firmware in `apps/tag/esp32h2_tag/` to an ESP32-H2.
2. On the Pi: `GATEWAY_TAG_ADAPTER=ble python -m main`.
3. Look for `bleak adapter ready` plus a scan result with `TG_01`.
4. Trigger a price change in the backend (`PATCH /api/products/1`) and watch for `write_gatt_char` success and an ack forwarded to `g-b/tag1/ack`.
