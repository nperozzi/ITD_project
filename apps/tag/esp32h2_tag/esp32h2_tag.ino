#include <Arduino.h>
#include <BLEDevice.h>
#include <BLEServer.h>

#include "config.h"
#include "display_manager.h"
#include "payload_parser.h"

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

    String title;
    String finalPrice;

    bool parseOk = extractDisplayFieldsFromJson(
        incomingPayload,
        title,
        finalPrice);

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

    payloadValue = title + " | " + finalPrice;

    displayPayload(title, finalPrice);

    acknowledgeValue = "true";
    acknowledgeCharacteristic->setValue(acknowledgeValue.c_str());

    Serial.println("Payload written by client");
    Serial.print("Characteristic handle: ");
    Serial.println(characteristic->getHandle());

    Serial.print("Displayed product name: ");
    Serial.println(title);

    Serial.print("Displayed price: ");
    Serial.println(finalPrice);

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

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("Starting BLE tag with e-paper");

  initDisplay();
  displayPayload("WAITING...", "");

  BLEDevice::init(DEVICE_NAME);

  bleServer = BLEDevice::createServer();
  bleServer->setCallbacks(new TagServerCallbacks());

  tagService = bleServer->createService(TAG_SERVICE_UUID);

  payloadCharacteristic = tagService->createCharacteristic(
      PAYLOAD_CHARACTERISTIC_UUID,
      BLECharacteristic::PROPERTY_WRITE);
  payloadCharacteristic->setCallbacks(new PayloadCharacteristicCallbacks());

  acknowledgeCharacteristic = tagService->createCharacteristic(
      ACKNOWLEDGE_CHARACTERISTIC_UUID,
      BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY);
  acknowledgeCharacteristic->setCallbacks(new AcknowledgeCharacteristicCallbacks());
  acknowledgeCharacteristic->setValue(acknowledgeValue.c_str());

  tagService->start();

  BLEAdvertising *bleAdvertising = BLEDevice::getAdvertising();
  bleAdvertising->addServiceUUID(TAG_SERVICE_UUID);
  bleAdvertising->setScanResponse(true);
  bleAdvertising->start();

  Serial.println("Advertising started");
}

void loop() {
  delay(100);
}