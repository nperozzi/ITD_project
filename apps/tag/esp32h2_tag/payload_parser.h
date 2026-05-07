#pragma once

#include <Arduino.h>

bool extractDisplayFieldsFromJson(
    const String &jsonPayload,
    String &titleToDisplay,
    String &finalPriceToDisplay);