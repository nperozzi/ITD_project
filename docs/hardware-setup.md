# ESL System Complete Setup Guide

This guide walks you through setting up the complete Electronic Shelf Label (ESL) system from scratch.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              WEB SERVER                                      │
│                          (192.168.8.5:3000)                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │   Dashboard     │  │   REST API      │  │   tRPC API      │             │
│  │   (Next.js)     │  │   /api/gateway  │  │   /api/trpc     │             │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘             │
│                              │                                              │
│                    ┌─────────┴─────────┐                                   │
│                    │   SQLite/Turso    │                                   │
│                    │   Database        │                                   │
│                    └───────────────────┘                                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTP (REST API)
                                    │
┌─────────────────────────────────────────────────────────────────────────────┐
│                         RASPBERRY PI PICO 2 W                               │
│                              (Gateway)                                       │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────┐           │
│  │                    gateway_daemon.py                         │           │
│  │  - Checks claim status with web server                       │           │
│  │  - Scans for Arduino labels via BLE                          │           │
│  │  - Reports discovered labels to server                       │           │
│  │  - Receives product updates                                  │           │
│  │  - Pushes display updates to Arduinos                        │           │
│  └─────────────────────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ BLE
                                    │
┌─────────────────────────────────────────────────────────────────────────────┐
│                      ARDUINO UNO R4 WIFI (Label)                            │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────┐           │
│  │                      esl_label.ino                           │           │
│  │  - Advertises via BLE as "ESL-{serial}"                      │           │
│  │  - Receives 96-byte LED matrix frames                        │           │
│  │  - Displays price on 12x8 LED matrix                         │           │
│  └─────────────────────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Step 1: Web Server Setup

### 1.1 Install Dependencies

```bash
cd web-app
bun install
```

### 1.2 Configure Environment

```bash
cp .env.example .env
# Edit .env with your database and auth settings
```

### 1.3 Setup Database

```bash
bun db:push
```

### 1.4 Start Development Server

```bash
bun dev
```

The server will be available at `http://localhost:3000` (or `http://192.168.8.5:3000` on your network).

## Step 2: Register Serial Numbers

### 2.1 Register Gateway Serial

```bash
bun admin gateway:create 1
```

Output:

```
Created 1 gateway serial(s):
  46c1fe7a-c6f7-4559-a530-cca060aef72b
```

**Save this serial number!** You'll need it for the Raspberry Pi.

### 2.2 Register Label Serial

```bash
bun admin label:create 1
```

Output:

```
Created 1 label serial(s):
  550e8400-e29b-41d4-a716-446655440000
```

**Save this serial number!** You'll need the first 8 characters for the Arduino.

### 2.3 List All Serials

```bash
bun admin gateway:list
bun admin label:list
```

## Step 3: Arduino Setup

### 3.1 Prepare the Code

1. Open `scripts/arduino/esl_label/esl_label.ino` in Arduino IDE
2. Edit the `LABEL_SERIAL` constant with the **first 8 characters** of your label serial:

```cpp
const char* LABEL_SERIAL = "550e8400";  // First 8 chars of your serial
```

### 3.2 Upload to Arduino

1. Select board: **Arduino UNO R4 WiFi**
2. Select port
3. Upload

### 3.3 Verify

Open Serial Monitor (115200 baud). You should see:

```
================================
ESL Label - Arduino UNO R4 WiFi
================================
Device Name: ESL-550e8400
Serial: 550e8400

BLE advertising started
Waiting for gateway connection...
```

The LED matrix should show a border pattern indicating "ready".

## Step 4: Raspberry Pi Setup

### 4.1 Install Python Dependencies

```bash
cd scripts/gateway
pip install -r requirements.txt
```

### 4.2 Configure Gateway

```bash
cp config.example.json config.json
```

Edit `config.json`:

```json
{
  "server_url": "http://192.168.8.5:3000",
  "serial_number": "46c1fe7a-c6f7-4559-a530-cca060aef72b",
  "api_key": null,
  "sync_interval_seconds": 30,
  "claim_check_interval_seconds": 10,
  "firmware_version": "1.0.0",
  "ble_scan_timeout": 10.0
}
```

### 4.3 Start the Gateway Daemon

```bash
python gateway_daemon.py
```

Output:

```
╔══════════════════════════════════════════════════╗
║          ESL GATEWAY DAEMON                      ║
║      Raspberry Pi Pico 2 W + Arduino R4          ║
╚══════════════════════════════════════════════════╝

Server URL: http://192.168.8.5:3000
Gateway Serial: 46c1fe7a-c6f7-4559-a530-cca060aef72b
Firmware Version: 1.0.0

==================================================
WAITING FOR CLAIM
==================================================

Serial Number: 46c1fe7a-c6f7-4559-a530-cca060aef72b

Please claim this gateway in the web dashboard.
Checking every 10 seconds...
```

## Step 5: Web Dashboard Operations

### 5.1 Create Account & Sign In

1. Go to `http://192.168.8.5:3000`
2. Create an account or sign in

### 5.2 Claim the Gateway

1. Go to the Gateways page
2. Click "Add Gateway"
3. Enter the gateway serial number: `46c1fe7a-c6f7-4559-a530-cca060aef72b`
4. Give it a name (e.g., "Store Gateway 1")
5. Click "Claim"

The Raspberry Pi should show:

```
✓ Gateway claimed!
  Name: Store Gateway 1
  Gateway ID: ...

==================================================
SYNC LOOP STARTED
==================================================
```

### 5.3 Register a Label

Once the gateway is syncing, it will discover the Arduino label:

```
[10:30:45] Starting sync cycle...
  Scanning for labels...
  Found 1 labels
    - 550e8400 (RSSI: -45)
  Syncing with server...
  ✓ Sync complete:
    Pending labels: 1
    Labels to update: 0
```

In the web dashboard:

1. Go to the Labels page
2. You should see the discovered label with serial `550e8400...`
3. Click "Register" to add it to your account

### 5.4 Create a Product

1. Go to the Products page
2. Click "Add Product"
3. Enter product details:
   - Name: "Coffee Beans"
   - Price: 9.99
   - SKU: "COF-001"
4. Save

### 5.5 Assign Product to Label

1. Go to the Labels page
2. Click on your registered label
3. Click "Assign Product"
4. Select "Coffee Beans"
5. Save

The system will now:

1. Queue the update for the label
2. Next sync cycle, gateway receives the update
3. Gateway pushes the price to Arduino via BLE
4. Arduino displays "9.99" on the LED matrix

## Step 6: Verify End-to-End

### On Raspberry Pi

```
[10:31:15] Starting sync cycle...
  Scanning for labels...
  Found 1 labels
    - 550e8400 (RSSI: -42)
  Syncing with server...
  ✓ Sync complete:
    Pending labels: 0
    Labels to update: 1

  Processing 1 display updates...
    → Pushing update to 550e8400
      Product: Coffee Beans
      Price: $9.99
      ✓ Display updated
  Acknowledged: 1 successful, 0 failed
```

### On Arduino Serial Monitor

```
Gateway connected
Display updated
```

### On Arduino LED Matrix

The display should show: `9.99`

## Troubleshooting

### Gateway can't connect to server

- Check that `server_url` in config.json is correct
- Verify the server is running and accessible
- Check firewall settings

### Gateway shows "Invalid serial number"

- Verify the serial was registered with `bun admin gateway:list`
- Check for typos in the serial number
- Serial numbers are case-insensitive

### Arduino not found by gateway

- Make sure Arduino is powered and BLE is advertising
- Check that the serial prefix in Arduino code matches
- Try moving the devices closer together
- Increase `ble_scan_timeout` in config.json

### Label not showing in dashboard

- Wait for the next sync cycle (default 30 seconds)
- Check gateway logs for discovery
- Verify the label serial was registered with `bun admin label:list`

### Price not updating on display

- Check that the product is assigned to the label
- Wait for the next sync cycle
- Check gateway logs for "Processing display updates"
- Verify BLE connection in Arduino serial monitor

## Files Reference

### Web Server

- `src/app/api/gateway/claim/route.ts` - Claim status API
- `src/app/api/gateway/sync/route.ts` - Sync API
- `src/services/gateway/` - Gateway service layer
- `scripts/admin.ts` - Admin CLI

### Raspberry Pi Gateway

- `scripts/gateway/gateway_daemon.py` - Main daemon
- `scripts/gateway/gateway_client.py` - HTTP client
- `scripts/gateway/ble_scanner.py` - BLE scanner
- `scripts/gateway/ble_sender.py` - BLE sender
- `scripts/gateway/matrix_renderer.py` - Price renderer
- `scripts/gateway/config.json` - Configuration

### Arduino Label

- `scripts/arduino/esl_label/esl_label.ino` - Label firmware
