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