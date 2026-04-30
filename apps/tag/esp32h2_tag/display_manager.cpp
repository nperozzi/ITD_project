#include "display_manager.h"
#include "config.h"

#include <GxEPD2_BW.h>
#include <SPI.h>

namespace {
SPIClass &spi = SPI;

GxEPD2_BW<GxEPD2_213_B74, GxEPD2_213_B74::HEIGHT>
display(GxEPD2_213_B74(CS_PIN, DC_PIN, RST_PIN, BUSY_PIN));
}

void initDisplay() {
  spi.begin(SCK_PIN, -1, MOSI_PIN, CS_PIN);
  display.epd2.selectSPI(spi, SPISettings(4000000, MSBFIRST, SPI_MODE0));
  display.init(115200, true, 2, false);
}

void displayDefaultScreen() {
  display.setRotation(1);
  display.setFullWindow();
  display.firstPage();

  do {
    display.fillScreen(GxEPD_WHITE);
    display.setTextColor(GxEPD_BLACK);
    display.setFont(NULL);
    display.setTextWrap(false);

    // Outer frame
    display.drawRect(4, 4, 242, 114, GxEPD_BLACK);
    display.drawRect(8, 8, 234, 106, GxEPD_BLACK);

    // Header
    display.setTextSize(1);
    display.setCursor(16, 20);
    display.print("ESL TAG");

    display.setCursor(196, 20);
    display.print(DEVICE_NAME);

    // Main status
    // display.setTextSize(2);
    // display.setCursor(92, 48);
    // display.print("READY");

    // Waiting message
    // display.setTextSize(1);
    // display.setCursor(58, 75);
    // display.print("Waiting for data");

    // Bottom status line
    display.setCursor(24, 100);
    display.print("BLE advertising - no update yet");

  } while (display.nextPage());

  Serial.println("Power-on default displayed on e-paper display.");
}

void displayPayload(const String &title, const String &finalPrice) {
  display.setFullWindow();
  display.firstPage();
  display.setRotation(1);
  //display.setTextSize(2);

  do {
    display.fillScreen(GxEPD_WHITE);
    display.setTextColor(GxEPD_BLACK);
    display.setFont(NULL);
    display.setTextWrap(false);

    // Outer frame
    display.drawRect(4, 4, 242, 114, GxEPD_BLACK);
    display.drawRect(8, 8, 234, 106, GxEPD_BLACK);

    // Header
    display.setTextSize(1);
    display.setCursor(16, 20);
    display.print("ESL TAG");

    display.setCursor(196, 20);
    display.print(DEVICE_NAME);

    // Payload content
    display.setTextSize(2);

    display.setCursor(10, 50);
    display.println(title);

    display.setCursor(10, 85);
    display.println(finalPrice + " SEK");

  } while (display.nextPage());

  Serial.println("Payload displayed on e-paper");
}