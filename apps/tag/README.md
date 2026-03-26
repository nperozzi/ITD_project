# Tag Advertisement Test 

This document is a step-by-step guide for setting up the required software and running a Bluetooth advertisement test with the **ESP32-H2-DevKitM-1**. 

## Purpose 

The purpose of this test is to help the group become familiar with the **ESP32-H2-DevKitM-1** as the project develops. Since this is one of the most practical parts of the project, it is important that everyone gains hands-on experience with the board.

## What the Code Does

This program configures the **ESP32-H2-DevKitM-1** as a Bluetooth Low Energy (BLE) peripheral using the NimBLE stack.

The code:

- sets the device name to **`ESL_TAG_001`**
- starts BLE advertising so nearby devices can discover it
- creates a custom GATT service and characteristic
- allows a connected device to read the value **`Hello from ESP32-H2`**
- restarts advertising automatically after a disconnect or failed connection

This test is useful for verifying that the board can advertise over BLE, accept a connection, and respond to a simple read request.

## Hardware Requirements

- ESP32-H2-DevKitM-1
- USB-A to USB-C (Type C) cable
- Computer running Windows, Linux, or macOS
- nRF Connect app (available on the App Store or Google Play)

## Software Setup

To install the required development environment, follow the official Espressif installation guide for your operating system:

- [ESP-IDF installation guide](https://docs.espressif.com/projects/esp-idf/en/latest/esp32h2/get-started/index.html#installation)

Make sure to select the correct instructions for:

- Windows
- Linux
- macOS

After the installation is complete:

1. Open a terminal.
2. Start the ESP-IDF enviroment.
3. Connect the **ESP32-H2-DevKitM-1** to your computer.
4. Verify that the board is detected.
5. Build and flash the project.




























# Tag Simulator

The tag module simulates electronic shelf label devices for development and validation. It allows teams to exercise device-facing behavior without relying on physical hardware.

## Role in the System

- Represents how labels react to updates sent through the platform.
- Emits device-like status signals to support monitoring and testing flows.
- Enables end-to-end scenario checks during feature development.

## Why It Matters

This module helps the team iterate quickly by providing a predictable stand-in for real tags. It reduces dependency on hardware availability during day-to-day work.

## Audience

New contributors should view this module as the development-time model of shelf labels within the larger ESL ecosystem.