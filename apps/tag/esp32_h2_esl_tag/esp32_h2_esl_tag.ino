#include <Arduino.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>

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
static String acknowledgeValue = "WAITING";

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

    if (incomingPayload.length() > 127) {
      incomingPayload = incomingPayload.substring(0, 127);
    }

    payloadValue = incomingPayload;
    acknowledgeValue = "RECEIVED";
    acknowledgeCharacteristic->setValue(acknowledgeValue);

    /* Future:
       call display update function here, for example:
       displayPayload(payloadValue);
    */

    Serial.println("Payload written by client");
    Serial.print("Characteristic handle: ");
    Serial.println(characteristic->getHandle());

    Serial.print("Payload value: ");
    Serial.println(payloadValue);

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

  Serial.println("Starting BLE tag");

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
  acknowledgeCharacteristic->setValue(acknowledgeValue);

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