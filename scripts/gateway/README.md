# ESL Gateway - Raspberry Pi Pico 2 W

This folder contains the Python scripts that run on the Raspberry Pi gateway device to communicate with the ESL web application and Arduino label devices.

## Hardware Setup

- **Gateway**: Raspberry Pi Pico 2 W
- **Labels**: Arduino UNO R4 WiFi with LED Matrix
- **Communication**: BLE between Pi and Arduino, HTTP between Pi and Web Server

## Architecture

```
┌─────────────────┐     HTTP      ┌─────────────────┐
│   Web Server    │◄────────────►│  Raspberry Pi   │
│  192.168.8.5    │               │   (Gateway)     │
└─────────────────┘               └────────┬────────┘
                                           │ BLE
                                           ▼
                                  ┌─────────────────┐
                                  │  Arduino UNO    │
                                  │  R4 WiFi        │
                                  │  (Label)        │
                                  └─────────────────┘
```

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Copy the config template:

```bash
cp config.example.json config.json
```

3. Edit `config.json` with your gateway's serial number (from admin registration)

4. Run the daemon:

```bash
python gateway_daemon.py
```

## Configuration

Edit `config.json`:

```json
{
  "server_url": "http://192.168.8.5:3000",
  "serial_number": "YOUR-GATEWAY-UUID-HERE",
  "api_key": null,
  "sync_interval_seconds": 30,
  "claim_check_interval_seconds": 10,
  "firmware_version": "1.0.0",
  "ble_scan_timeout": 10.0
}
```

## Files

| File                 | Description                                  |
| -------------------- | -------------------------------------------- |
| `gateway_daemon.py`  | Main daemon process                          |
| `gateway_client.py`  | HTTP client for web API                      |
| `ble_scanner.py`     | BLE scanner for Arduino labels               |
| `ble_sender.py`      | BLE sender to push updates to labels         |
| `matrix_renderer.py` | Converts product data to LED matrix patterns |
| `check_claim.py`     | Standalone claim status checker              |
| `sync_labels.py`     | Standalone label sync script                 |

## Flow

1. **Startup**: Gateway checks if it's been claimed
2. **Waiting**: If not claimed, polls every 10s until user claims it via web UI
3. **Scanning**: Once claimed, scans for nearby Arduino labels via BLE
4. **Syncing**: Reports discovered labels to web server
5. **Updates**: Receives product assignments and pushes to Arduino displays
6. **Loop**: Repeats scanning/syncing every 30s

## Arduino Label Setup

Each Arduino must be programmed with a unique serial number. The Arduino advertises via BLE with its serial number embedded in the device name.

See `../arduino/` folder for Arduino code.
