#include "payload_parser.h"
#include "config.h"

#include <ArduinoJson.h>
#include <cstring>

bool extractDisplayFieldsFromJson(
    const String &jsonPayload,
    String &titleToDisplay,
    String &finalPriceToDisplay) {

  JsonDocument doc;

  DeserializationError error = deserializeJson(doc, jsonPayload);
  if (error) {
    Serial.print("deserializeJson() failed: ");
    Serial.println(error.c_str());
    return false;
  }

  const char *tagId = doc["tagId"];
  const char *title = doc["title"];
  const char *finalPrice = doc["finalPrice"];
  // const char *status = doc["status"];

  if (tagId == nullptr || title == nullptr || finalPrice == nullptr) {
    Serial.println("JSON missing one or more required fields");
    return false;
  }

  if (strcmp(tagId, DEVICE_NAME) != 0) {
    Serial.println("Payload rejected: tagId does not match this tag");
    return false;
  }

  titleToDisplay = String(title);
  finalPriceToDisplay = String(finalPrice);

  return true;
}