/*
 * ESL Label - Arduino UNO R4 WiFi
 * 
 * Electronic Shelf Label firmware for Arduino UNO R4 WiFi.
 * Receives LED matrix frames from Raspberry Pi gateway via BLE.
 * 
 * Setup:
 * 1. Register a label serial number via web admin CLI:
 *    bun admin label:create 1
 * 2. Edit LABEL_SERIAL below with the first 8 characters of the serial
 * 3. Upload this sketch to the Arduino
 * 
 * The Arduino will advertise as "ESL-{LABEL_SERIAL}" via BLE and wait
 * for the gateway to send display updates.
 */

#include <ArduinoBLE.h>
#include "Arduino_LED_Matrix.h"

// ============================================================================
// CONFIGURATION - Edit this with your label's serial number (first 8 chars)
// ============================================================================
const char* LABEL_SERIAL = "e07423c5";  // Replace with first 8 chars of your serial
// ============================================================================

// BLE UUIDs - Must match gateway code
#define SERVICE_UUID "12345678-1234-1234-1234-1234567890ab"
#define CHAR_UUID    "abcdefab-1234-5678-1234-abcdefabcdef"

// LED Matrix dimensions
#define MATRIX_WIDTH  12
#define MATRIX_HEIGHT 8
#define FRAME_SIZE    (MATRIX_WIDTH * MATRIX_HEIGHT)  // 96 bytes

// Buzzer pin
#define BUZZER_PIN 8

// BLE service and characteristic
BLEService matrixService(SERVICE_UUID);
BLECharacteristic matrixChar(
  CHAR_UUID,
  BLEWriteWithoutResponse,
  FRAME_SIZE
);

// LED Matrix
ArduinoLEDMatrix matrix;

// Pixel buffer
uint8_t pixels[FRAME_SIZE];

// Previous frame buffer for change detection
uint8_t previousPixels[FRAME_SIZE];

// Device name buffer
char deviceName[20];

void setup() {
  Serial.begin(115200);
  
  // Wait for serial (optional, remove for production)
  // while (!Serial);
  
  // Initialize buzzer pin
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);
  
  // Initialize LED matrix
  matrix.begin();
  
  // Clear previous frame buffer
  memset(previousPixels, 0, FRAME_SIZE);
  
  // Show startup pattern
  showStartupPattern();
  
  // Build device name: "ESL-{serial}"
  snprintf(deviceName, sizeof(deviceName), "ESL-%s", LABEL_SERIAL);
  
  Serial.println("================================");
  Serial.println("ESL Label - Arduino UNO R4 WiFi");
  Serial.println("================================");
  Serial.print("Device Name: ");
  Serial.println(deviceName);
  Serial.print("Serial: ");
  Serial.println(LABEL_SERIAL);
  Serial.println();
  
  // Initialize BLE
  if (!BLE.begin()) {
    Serial.println("ERROR: BLE initialization failed!");
    showErrorPattern();
    while (1);
  }
  
  // Set device name and advertise service
  BLE.setLocalName(deviceName);
  BLE.setAdvertisedService(matrixService);
  
  // Add characteristic to service
  matrixService.addCharacteristic(matrixChar);
  BLE.addService(matrixService);
  
  // Start advertising
  BLE.advertise();
  
  Serial.println("BLE advertising started");
  Serial.println("Waiting for gateway connection...");
  Serial.println();
  
  // Show ready pattern
  showReadyPattern();
}

void loop() {
  // Poll for BLE events
  BLEDevice central = BLE.central();
  
  if (central) {
    Serial.print("Gateway connected: ");
    Serial.println(central.address());
    
    while (central.connected()) {
      // Check if new data was written
      if (matrixChar.written()) {
        int len = matrixChar.valueLength();
        
        if (len == FRAME_SIZE) {
          // Read the frame data
          matrixChar.readValue(pixels, FRAME_SIZE);
          
          // Check if frame actually changed
          if (memcmp(pixels, previousPixels, FRAME_SIZE) != 0) {
            // Frame is different, update display and beep
            matrix.loadPixels(pixels, FRAME_SIZE);
            
            // Save current frame as previous
            memcpy(previousPixels, pixels, FRAME_SIZE);
            
            // Beep to indicate update
            beep();
            
            Serial.println("Display updated");
          } else {
            // Frame is the same, skip update
            Serial.println("Frame unchanged, skipping update");
          }
        } else {
          Serial.print("Invalid frame size: ");
          Serial.println(len);
        }
      }
      
      delay(10);  // Small delay to prevent tight loop
    }
    
    Serial.println("Gateway disconnected");
    Serial.println("Waiting for reconnection...");
    
    // Keep showing last frame (display persistence)
  }
  
  delay(100);
}

// ============================================================================
// Buzzer Control
// ============================================================================

void beep() {
  for(int i = 0; i < 100; i++) {
    digitalWrite(BUZZER_PIN, HIGH);
    delay(2);
    digitalWrite(BUZZER_PIN, LOW);
    delay(2);
  }
}

// ============================================================================
// Display Patterns
// ============================================================================

void showStartupPattern() {
  // Fill pattern (all LEDs on briefly)
  memset(pixels, 1, FRAME_SIZE);
  matrix.loadPixels(pixels, FRAME_SIZE);
  delay(200);
  
  // Clear
  memset(pixels, 0, FRAME_SIZE);
  matrix.loadPixels(pixels, FRAME_SIZE);
}

void showReadyPattern() {
  // Show a simple "ready" indicator (border)
  memset(pixels, 0, FRAME_SIZE);
  
  // Top and bottom rows
  for (int x = 0; x < MATRIX_WIDTH; x++) {
    pixels[x] = 1;                              // Top row
    pixels[(MATRIX_HEIGHT - 1) * MATRIX_WIDTH + x] = 1;  // Bottom row
  }
  
  // Left and right columns
  for (int y = 0; y < MATRIX_HEIGHT; y++) {
    pixels[y * MATRIX_WIDTH] = 1;               // Left column
    pixels[y * MATRIX_WIDTH + MATRIX_WIDTH - 1] = 1;  // Right column
  }
  
  matrix.loadPixels(pixels, FRAME_SIZE);
}

void showConnectedPattern() {
  // Checkmark pattern
  memset(pixels, 0, FRAME_SIZE);
  
  // Draw a simple checkmark
  int checkmark[][2] = {
    {3, 5}, {4, 6}, {5, 7}, {6, 6}, {7, 5}, {8, 4}, {9, 3}
  };
  
  for (int i = 0; i < 7; i++) {
    int x = checkmark[i][0];
    int y = checkmark[i][1];
    if (x >= 0 && x < MATRIX_WIDTH && y >= 0 && y < MATRIX_HEIGHT) {
      pixels[y * MATRIX_WIDTH + x] = 1;
    }
  }
  
  matrix.loadPixels(pixels, FRAME_SIZE);
}

void showErrorPattern() {
  // X pattern for errors
  memset(pixels, 0, FRAME_SIZE);
  
  for (int i = 0; i < min(MATRIX_WIDTH, MATRIX_HEIGHT); i++) {
    // Diagonal from top-left to bottom-right
    if (i < MATRIX_HEIGHT) {
      pixels[i * MATRIX_WIDTH + i] = 1;
    }
    // Diagonal from top-right to bottom-left  
    if (i < MATRIX_HEIGHT) {
      pixels[i * MATRIX_WIDTH + (MATRIX_WIDTH - 1 - i)] = 1;
    }
  }
  
  matrix.loadPixels(pixels, FRAME_SIZE);
}
