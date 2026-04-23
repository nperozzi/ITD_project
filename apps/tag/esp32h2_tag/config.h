#pragma once

#include <Arduino.h>

/* BLE */
static const char DEVICE_NAME[] = "TG_01";

static const char TAG_SERVICE_UUID[] =
    "B8E4F533-E530-4D1D-B54C-0D5D5A9A5A4B";

static const char PAYLOAD_CHARACTERISTIC_UUID[] =
    "99CFD161-DCD8-4BEB-86B2-48673AEAE284";

static const char ACKNOWLEDGE_CHARACTERISTIC_UUID[] =
    "53B04C05-A5E1-475B-BC9E-61C00112ACDE";

/* E-paper pins */
static const int MOSI_PIN = 10;
static const int SCK_PIN  = 11;
static const int CS_PIN   = 3;
static const int DC_PIN   = 2;
static const int RST_PIN  = 1;
static const int BUSY_PIN = 4;