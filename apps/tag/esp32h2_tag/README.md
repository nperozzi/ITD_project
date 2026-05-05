# ESL Tag with E-paper Display

This document is a step-by-step guide on how to set up the **ESP32-H2-DevKitM-1** with the **WeAct Studio 2.13" Monochrome E-Paper Module**
for development with the Arduino IDE.

## Purpose

The purpose is to help group members get their **WeAct Studio 2.13" Monochrome E-Paper Module** working with the **ESP32-H2-DevKitM-1** board.

## Hardware List

- **ESP32-H2-DevKitM-1**.
- **WeAct Studio 2.13" Monochrome E-Paper Module (122×250, SSD1680, FPC-7528B family)**.
- USB-C to USB-C (with USB-C female to male USB-A adapter if needed) cable.

## Software Installation & Setup

## Arduino IDE

### 1. Arduino IDE Installation

See these install instructions:  
[Downloading and installing the Arduino IDE 2](https://docs.arduino.cc/software/ide-v2/tutorials/getting-started/ide-v2-downloading-and-installing/)  

### 2. Install Support for **ESP32-H2-DevKitM-1** in Arduino IDE

#### 2.1 Add suppport for the **ESP32-H2-DevKitM-1**

Go to `File -> Preferences -> Additional Board Manager URLs = Add` and add the below:

```bash
https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
```

then click `OK` to close the window which you pasted the above URL in. Then click `OK` again to finish this process properly.

#### 2.2 Install ESP32 Support Package

Go to `Tools -> Boards: ... -> Boards Manager... -> search 'esp32 (by Espressif Systems)' -> Install that package`.

#### 2.3 Selecting correct board

Go to `Tools -> Board: ... -> esp32 -> Select 'ESP32H2 Dev Module'`.

**IMPORTANT:** Do NOT select any other board as that will not work with the exact board we have.

### 3. Install **GxEPD2** library for **WeAct Studio 2.13" Monochrome E-Paper Module**

Go to `Tools -> Manage Libraries... -> Search for 'GxEPD2' by 'Jean-Marc Zingg' -> Click 'INSTALL'`.

### 4. Install **ArduinoJSON** library for JSON handling
Go to `Tools -> Manage Libraries... -> Search for 'ArduinoJson' by 'Benoit Blanchon' -> Click 'INSTALL'`

## Wiring Setup

1. Connect the USB-C to USB-C cable to first to the `UART` USB-C port on the **ESP32-H2-DevKitM-1**.

2. Then wire the **WeAct Studio 2.13" Monochrome E-Paper Module** cable to the **ESP32-H2-DevKitM-1** using the below pairing:

```bash
VCC -> 3.3V
GND -> GND (G)
SDA(MOSI) -> pin 10
SCL(SCK) -> pin 11
CS -> pin 3
D/C (DC) -> pin 2
RST -> pin 1
BUSY -> pin 4
```

1. Make sure the correct USB port under `Tools -> Port: ...` is selected.

2. Connect the end of the USB-C to USB-C cable that is free to your computer and make sure sure that in the lower right corner of the Arduino IDE window  
you can see e.g. `ESP32H2 Dev Module on /dev/ttyUSB0` (for Linux)  
`ESP32H2 Dev Module on COM3` (for Windows).

3. Connect the white plug of the **WeAct Studio 2.13" Monochrome E-Paper Module** cable to the **WeAct Studio 2.13" Monochrome E-Paper Module**.

## Compiling, Building and Flashing/Uploading to **ESP32-H2-DevKitM-1**

1. In Arduino IDE go to `File -> Open...` and navigate to `apps/tag/esp32_h2_esl_tag/esp32_h2_esl_tag.ino` to open the correct `*.ino` file.

2. Assuming you are done with your code changes click `✓` (the little checkmark in the top left corner), let it finish.

3. Assuming the `✓` step didn't fail now click on `➜` (the little checkmark in the top left corner next to `✓`), let it finish.  
This will compile, build and then flash the source code to the **ESP32-H2-DevKitM-1**.

**IMPORTANT:** Always use the Arduino IDE to edit, verify/debug and flash the `*.ino` file(s) to the **ESP32-H2-DevKitM-1**. For Git usage do as you normally do on your computer.

## nRF Connect App Usage for BLE Testing

Since the gateway is not yet implemented, the **nRF Connect** app is used as a temporary BLE client for testing communication with the tag.

Using the app, team members can:

- scan for the tag
- connect to it over BLE
- inspect its services and characteristics
- send test data
- receive acknowledge data back 
- verify responses during development

## Before Scanning

Before scanning for the tag in **nRF Connect**, ensure that the project code has been compiled and flashed to the **ESP32-H2-DevKitM-1**.

If the firmware is not uploaded to the board, the tag may not advertise correctly and may therefore not appear in the BLE scan results.

It is also recommended to keep the **Serial Monitor** open in the **Arduino IDE** during testing. This makes it easier to observe debug output and verify whether the tag is receiving data as expected.

## Setup for test with nRF Connect app

### iOS

1. Open the **App Store**.
2. Search for **nRF Connect for Mobile**.
3. Install the app.
4. Launch the app and open the scanner.
5. Scan for the tag and select it from the list of available devices.
6. Tap **Connect**.
7. Once connected, the app will display the available BLE services and characteristics.

### Android

1. Open the **Google Play Store**.
2. Search for **nRF Connect for Mobile**.
3. Install the app.
4. Launch the app and start scanning for nearby BLE devices.
5. Select the tag from the list of available devices.
6. Tap **Connect**.
7. Once connected, the app will display the available BLE services and characteristics.

## Sending Text to the Tag

After connecting to the tag:

1. Open the custom BLE service.
2. Locate the characteristic used to **send payload data to the tag** *(identified as "Write" under Characteristics)*.
3. Select the write option for that characteristic and set the value format to **UTF-8**, as the default format is typically **Byte Array (Hex)**.
4. Enter the text to be sent to the tag (example JSON below) exactly as written:

- Expected input examples

{"tagId":"TG_01","title":"Apple 1kg","finalPrice":49.00}
{"tagId":1,"title":"Apple 1kg","finalPrice":49.00}
5. Send the value.
6. Sent value should display on the  **WeAct Studio 2.13" Monochrome E-Paper Module**

This step is used to test whether the tag can receive and process payload data correctly.

### OBS

The expected fields of validation are the keys sent by the the **Gateway/Backend** which are - 'tagId', 'title' and 'finalPrice' any other fields added will be filtered out by the tag. But the tag will throw an eeror if any of the filed of validation is missing.

## Debugging

While sending text through **nRF Connect**, keep the **Serial Monitor** open in the **Arduino IDE**.

This helps to:

- verify that the **ESP32-H2-DevKitM-1** is running correctly
- confirm that the payload has been received
- identify issues during BLE testing

If the tag does not appear in the scanner, first verify that:

- the board is powered
- the correct firmware has been flashed
- BLE advertising is active
- the Serial Monitor shows normal debug output

## Setup for test with an actual Gateway

The gateway client scans a connects to the Tag BLE-server service and  and characteristics. The Tag has one service with contains two characteristics, with its respective UUID that that gateway client can connects to send and recieve data, read data.

### Expected behaviour of the Tag

- Discoverable and connectable. The tag is expected to stop advertising when a client is connected to the Tag BLE-server
- Able to inspect and interact with the service and characteristics of the Tag when connected to it.
- Send raw json payload to the payload characteristic.
- Send acknowlegde value back to client
- The Tag is expected ignore any other field that is not the validation field, but throw an error if any of the validation field is missing.
- The Tag is expected to display nnly the designated fields on the e-paper module

### Input expected from the Gateway by the Tag

The Tag advertises with its DEVICE NAME **TG_01** and can receive data from a BLE-Client with its DEVICE NAME or the Tag_ID_NUMBER **1** as the value to the key **tagId** in the field of validation.

#### Expected examples

- {"tagId":"TG_01","title":"Apple 1kg","finalPrice":49.00}

- {"tagId":1,"title":"Apple 1kg","finalPrice":49.00}

- {"tagId":1,"title":"Apple 1kg","finalPrice":49.00,"status":"ok"} -> status is expected to be ignored by the Tag.

#### Expected output on e-paper module

 Apple 1kg
 49.00 SEK