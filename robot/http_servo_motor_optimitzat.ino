#include <ArduinoJson.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ESP32Servo.h>

// ====================== CONFIG ======================
const char* ssid = "testingesp";
const char* password = "12341234";
String gatewayStr = "192.168.1.50";

// Shift register pins
const int dataPin  = 15;
const int latchPin = 16;
const int clockPin = 17;

// Servo pins
const int servo1Pin = 32;
const int servo2Pin = 33;

// ====================== OBJECTS ======================
Servo servo1, servo2;

// ====================== INIT FUNCTIONS ======================
void updateShiftRegister(byte val1, byte val2) {
  digitalWrite(latchPin, LOW);
  shiftOut(dataPin, clockPin, LSBFIRST, val2);
  shiftOut(dataPin, clockPin, LSBFIRST, val1);
  digitalWrite(latchPin, HIGH);
}

// ====================== NETWORK FUNCTIONS ======================

void receiveData() {
  HTTPClient http;
  http.begin("http://" + String(gatewayStr) + ":5000/get");
  http.setTimeout(200);
  int httpResponseCode = http.GET();

  if (httpResponseCode > 0) {
    String payload = http.getString();
    StaticJsonDocument<300> doc;
    DeserializationError error = deserializeJson(doc, payload);

    if (!error) {
      String bitString = doc["bits"];
      if (bitString.length() == 24) {
        String first8 = bitString.substring(0, 8);
        uint8_t shiftValue = strtol(first8.c_str(), NULL, 2);
        updateShiftRegister(shiftValue, 0b11110000);

        String mid8 = bitString.substring(8, 16);
        int angle1 = strtol(mid8.c_str(), NULL, 2);
        servo1.write(angle1);

        String last8 = bitString.substring(16);
        int angle2 = strtol(last8.c_str(), NULL, 2);
        servo2.write(angle2);
      }
    }
  }

  Serial.print("GET Response: ");
  Serial.println(httpResponseCode);
  http.end();
}

// ====================== TASKS ======================

void TaskReceive(void *pvParameters) {
  const TickType_t xFrequency = pdMS_TO_TICKS(100);
  TickType_t xLastWakeTime = xTaskGetTickCount();

  for (;;) {
    if (WiFi.status() == WL_CONNECTED) {
      receiveData();   // la teva funció GET
    }
    vTaskDelayUntil(&xLastWakeTime, xFrequency);
  }
}

// ====================== MAIN ======================
void setup() {
  Serial.begin(115200);
  pinMode(dataPin, OUTPUT);
  pinMode(latchPin, OUTPUT);
  pinMode(clockPin, OUTPUT);

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500); Serial.print(".");
  }
  Serial.println("\nConnected!");
  gatewayStr = WiFi.gatewayIP().toString();

  servo1.attach(servo1Pin);
  servo2.attach(servo2Pin);

  updateShiftRegister(0b00000000, 0b00000000);

  // FreeRTOS tasks
  xTaskCreatePinnedToCore(TaskReceive, "TaskReceive", 8192, NULL, 1, NULL, 0); // Core 0
}

void loop() {
  // Buit: tot funciona amb FreeRTOS tasks
}
