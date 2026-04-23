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

void displayPayload(const String &title, const String &finalPrice) {
  display.setFullWindow();
  display.firstPage();
  display.setRotation(1);
  display.setTextSize(2);

  do {
    display.fillScreen(GxEPD_WHITE);
    display.setTextColor(GxEPD_BLACK);
    display.setTextWrap(true);

    display.setCursor(10, 40);
    display.println(title);

    display.setCursor(10, 80);
    display.println(finalPrice);

  } while (display.nextPage());

  Serial.println("Payload displayed on e-paper");
}