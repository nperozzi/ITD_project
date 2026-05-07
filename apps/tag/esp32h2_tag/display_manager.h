#pragma once

#include <Arduino.h>

void initDisplay();
void displayDefaultScreen();
void displayPayload(const String &title, const String &finalPrice);