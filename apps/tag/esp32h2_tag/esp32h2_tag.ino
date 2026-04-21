#include <Arduino.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <GxEPD2_BW.h>
#include <SPI.h>
#include <ArduinoJson.h>
#include <cstring>

/* -------------------- BLE -------------------- */
#define DEVICE_NAME "TG_01"

/* UUID strings */
static const char *TAG_SERVICE_UUID =
    "B8E4F533-E530-4D1D-B54C-0D5D5A9A5A4B";

static const char *PAYLOAD_CHARACTERISTIC_UUID =
    "99CFD161-DCD8-4BEB-86B2-48673AEAE284";

static const char *ACKNOWLEDGE_CHARACTERISTIC_UUID =
    "53B04C05-A5E1-475B-BC9E-61C00112ACDE";

/* Stored values */
static String payloadValue = "";
static String acknowledgeValue = "false";

/* BLE objects */
static BLEServer *bleServer = nullptr;
static BLEService *tagService = nullptr;
static BLECharacteristic *payloadCharacteristic = nullptr;
static BLECharacteristic *acknowledgeCharacteristic = nullptr;

/* Connection state */
static bool clientConnected = false;

/* -------------------- E-PAPER -------------------- */
#define MOSI 10
#define SCK  11
#define CS   3
#define DC   2
#define RST  1
#define BUSY 4

SPIClass spi = SPI;

GxEPD2_BW<GxEPD2_213_B74, GxEPD2_213_B74::HEIGHT>
display(GxEPD2_213_B74(CS, DC, RST, BUSY));

/* -------------------- DISPLAY FUNCTION -------------------- */
void displayPayload(const String &productName, const String &price) {
  display.setFullWindow();
  display.firstPage();
  display.setRotation(1);
  display.setTextSize(2);

  do {
    display.fillScreen(GxEPD_WHITE);
    display.setTextColor(GxEPD_BLACK);
    display.setTextWrap(true);

    display.setCursor(10, 40);
    display.println(productName);

    display.setCursor(10, 80);
    display.println(price);

  } while (display.nextPage());

  Serial.println("Payload displayed on e-paper");
}

/* -------------------- JSON PARSE FUNCTION -------------------- */
/*
  Expected JSON payload from gateway:  Fields can be updated accordingly 
  {
    "tag_id": "TG_01",
    "product_name": "Milk 1L",
    "price": "29.00 SEK",
    "status": "Ok"
  }
*/
bool extractDisplayFieldsFromJson(
    const String &jsonPayload,
    String &productNameToDisplay,
    String &priceToDisplay) {

  JsonDocument doc;

  DeserializationError error = deserializeJson(doc, jsonPayload);
  if (error) {
    Serial.print("deserializeJson() failed: ");
    Serial.println(error.c_str());
    return false;
  }

  const char *tagId = doc["tag_id"];  // Validation field
  const char *productName = doc["product_name"];
  const char *price = doc["price"];
  const char *status = doc["status"];

  if (tagId == nullptr || productName == nullptr || price == nullptr || status == nullptr) {
    Serial.println("JSON missing one or more required fields");
    return false;
  }

  if (strcmp(tagId, DEVICE_NAME) != 0) {
    Serial.println("Payload rejected: tag_id does not match this tag");
    return false;
  }

  if (strcmp(status, "Ok") != 0) {
    Serial.println("Payload rejected: status is not Ok");
    return false;
  }

  productNameToDisplay = String(productName);
  priceToDisplay = String(price);

  return true;
}

/* -------------------- BLE CALLBACKS -------------------- */
class TagServerCallbacks : public BLEServerCallbacks {
  void onConnect(BLEServer *server) override {
    clientConnected = true;
    Serial.println("Client connected");
  }

  void onDisconnect(BLEServer *server) override {
    clientConnected = false;
    Serial.println("Client disconnected");

    delay(200);
    server->getAdvertising()->start();
    Serial.println("Advertising restarted");
  }
};

class PayloadCharacteristicCallbacks : public BLECharacteristicCallbacks {
  void onWrite(BLECharacteristic *characteristic) override {
    String incomingPayload = characteristic->getValue();

if (incomingPayload.length() == 0) {
  Serial.println("Empty payload received");

  acknowledgeValue = "false";
  acknowledgeCharacteristic->setValue(acknowledgeValue.c_str());

  if (clientConnected) {
    acknowledgeCharacteristic->notify();
    Serial.println("Acknowledge notification sent");
  }
  return;
}

    Serial.println("Raw JSON received over BLE:");
    Serial.println(incomingPayload);

    String productName;
    String price;

    bool parseOk = extractDisplayFieldsFromJson(
        incomingPayload,
        productName,
        price);

    if (!parseOk) {
      acknowledgeValue = "false";
      acknowledgeCharacteristic->setValue(acknowledgeValue.c_str());

      Serial.println("JSON parse/validation failed, nothing displayed");

      if (clientConnected) {
        acknowledgeCharacteristic->notify();
        Serial.println("Acknowledge notification sent");
      }
      return;
    }

    payloadValue = productName + " | " + price;

    displayPayload(productName, price);

    acknowledgeValue = "true";
    acknowledgeCharacteristic->setValue(acknowledgeValue.c_str());

    Serial.println("Payload written by client");
    Serial.print("Characteristic handle: ");
    Serial.println(characteristic->getHandle());

    Serial.print("Displayed product name: ");
    Serial.println(productName);

    Serial.print("Displayed price: ");
    Serial.println(price);

    Serial.print("Acknowledge value updated to: ");
    Serial.println(acknowledgeValue);

    if (clientConnected) {
      acknowledgeCharacteristic->notify();
      Serial.println("Acknowledge notification sent");
    }
  }
};

class AcknowledgeCharacteristicCallbacks : public BLECharacteristicCallbacks {
  void onRead(BLECharacteristic *characteristic) override {
    Serial.println("Acknowledgement read by client");
    Serial.print("Characteristic handle: ");
    Serial.println(characteristic->getHandle());

    Serial.print("Acknowledge value sent: ");
    Serial.println(acknowledgeValue);
  }
};

/* -------------------- SETUP -------------------- */
void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("Starting BLE tag with e-paper");

  /* E-paper init */
  spi.begin(SCK, -1, MOSI, CS);
  display.epd2.selectSPI(spi, SPISettings(4000000, MSBFIRST, SPI_MODE0));
  display.init(115200, true, 2, false);

  displayPayload("WAITING...", "");

  /* BLE init */
  BLEDevice::init(DEVICE_NAME);

  bleServer = BLEDevice::createServer();
  bleServer->setCallbacks(new TagServerCallbacks());

  tagService = bleServer->createService(TAG_SERVICE_UUID);

  payloadCharacteristic = tagService->createCharacteristic(
      PAYLOAD_CHARACTERISTIC_UUID,
      BLECharacteristic::PROPERTY_WRITE
  );
  payloadCharacteristic->setCallbacks(new PayloadCharacteristicCallbacks());

  acknowledgeCharacteristic = tagService->createCharacteristic(
      ACKNOWLEDGE_CHARACTERISTIC_UUID,
      BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY
  );
  acknowledgeCharacteristic->setCallbacks(new AcknowledgeCharacteristicCallbacks());
  acknowledgeCharacteristic->setValue(acknowledgeValue.c_str());

  tagService->start();

  BLEAdvertising *bleAdvertising = BLEDevice::getAdvertising();
  bleAdvertising->addServiceUUID(TAG_SERVICE_UUID);
  bleAdvertising->setScanResponse(true);
  bleAdvertising->start();

  Serial.println("Advertising started");
}

/* -------------------- LOOP -------------------- */
void loop() {
  delay(100);
}