# Arduino UNO R4 WiFi - ESL Label Code

This folder contains the Arduino code for ESL (Electronic Shelf Label) devices.

## Hardware

- Arduino UNO R4 WiFi with built-in LED Matrix (12x8)
- Uses BLE to communicate with Raspberry Pi gateway

## Setup

### 1. Get a Label Serial Number

First, register a label serial number using the admin CLI on the web server:

```bash
cd web-app
bun admin label:create 1
```

This will output something like:

```
Created 1 label serial(s):
  550e8400-e29b-41d4-a716-446655440000
```

### 2. Configure the Arduino

Copy `esl_label.ino` to your Arduino project.

Edit the `LABEL_SERIAL` constant with the **first 8 characters** of your serial number:

```cpp
// Use first 8 chars of your registered serial number
const char* LABEL_SERIAL = "550e8400";
```

### 3. Upload to Arduino

1. Open Arduino IDE
2. Select board: Arduino UNO R4 WiFi
3. Upload the sketch

### 4. Verify

The Arduino will advertise as `ESL-{serial}` via BLE.

You can verify with the gateway's BLE scanner:

```bash
cd ../gateway
python ble_scanner.py
```

## How It Works

1. Arduino boots and starts BLE advertising as `ESL-{serial}`
2. Raspberry Pi gateway scans and discovers the Arduino
3. Gateway reports the label's serial to the web server
4. User assigns a product to the label via web UI
5. Gateway receives update and sends 96-byte LED frame to Arduino
6. Arduino displays the product price on LED matrix

## LED Matrix Format

The LED matrix is 12 columns × 8 rows = 96 pixels.

Data is sent as 96 bytes, row-major order:

- Byte 0-11: Row 0 (top)
- Byte 12-23: Row 1
- ...
- Byte 84-95: Row 7 (bottom)

Each byte is 0 (off) or 1 (on).
