#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
#include "RTClib.h"

#define IR_PIN 14

const char* ssid = "00000000";
const char* password = "00000000";

const char* esp1IP = "10.176.103.249";
const uint16_t esp1Port = 80;
const char* endpoint = "/receive_car";

const char* vehicle_id = "CAR_01";
const char* segment = "Petra_Street";

RTC_DS3231 rtc;
int lastState = -1;

String makeIsoTimestamp(DateTime dt) {
  char buf[32];
  snprintf(buf, sizeof(buf), "%04u-%02u-%02uT%02u:%02u:%02u",
           dt.year(), dt.month(), dt.day(),
           dt.hour(), dt.minute(), dt.second());
  return String(buf);
}

void sendVehicleData() {
  if (WiFi.status() != WL_CONNECTED) return;

  DateTime now = rtc.now();
  String timestamp = makeIsoTimestamp(now);

  String payload = "{";
  payload += "\"vehicle_id\":\"" + String(vehicle_id) + "\",";
  payload += "\"segment\":\"" + String(segment) + "\",";
  payload += "\"timestamp\":\"" + timestamp + "\"";
  payload += "}";

  String url = String("http://") + esp1IP + ":" + String(esp1Port) + endpoint;

  HTTPClient http;
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  int httpCode = http.POST(payload);
  if (httpCode > 0) {
    Serial.printf("Sent to ESP1, POST %d\n", httpCode);
  } else {
    Serial.printf("POST failed: %s\n", http.errorToString(httpCode).c_str());
  }
  http.end();
}

void setup() {
  Serial.begin(115200);
  pinMode(IR_PIN, INPUT_PULLUP);

  if (!rtc.begin()) Serial.println("RTC not found!");

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  unsigned long start = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - start < 20000) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  if (WiFi.status() == WL_CONNECTED) Serial.println(WiFi.localIP());
}

void loop() {
  int irState = !digitalRead(IR_PIN);

  if (irState != lastState) {
    Serial.printf("IR change: %d -> %d\n", lastState, irState);
    if (irState == 1) sendVehicleData();
    lastState = irState;
  }

  if (WiFi.status() != WL_CONNECTED) WiFi.reconnect();
  delay(50);
}