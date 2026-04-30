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

  if(!doc["tagId"].is<int>() && !doc["tagId"].is<const char *>()){
    Serial.println("JSON tagId missing or wrong type");
    return false;
  }

  if(!doc["title"].is<const char *>()) {
    Serial.println("JSON title missing or wrong type");
    return false;
  }

  if(!doc["finalPrice"].is<float>() && !doc["finalPrice"].is<int>()){
    Serial.println("JSON finalPrice missing or wrong type");
    return false;
  }

  bool tagMatches = false;

  if (doc["tagId"].is <int>()){
    int incomingTagId = doc["tagId"].as<int>();

    if (incomingTagId == TAG_ID_NUMBER){
      tagMatches = true;
    }
  }

  if (doc["tagId"].is<const char *>()) {
    const char *incomingTagName = doc["tagId"].as<const char *>();

    if(strcmp(incomingTagName, DEVICE_NAME) == 0) {
      tagMatches = true;
    }
  }

  if (!tagMatches) {
    Serial.println("Payload rejected: tagId does not match this tag");
    return false;
  }

  const char *title = doc["title"].as<const char *>();
  float finalPrice = doc["finalPrice"].as<float>();
  
  titleToDisplay = String(title);
  finalPriceToDisplay = String(finalPrice, 2);

  return true;
}