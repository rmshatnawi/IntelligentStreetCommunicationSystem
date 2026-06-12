#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
#include "RTClib.h"
#include <WebServer.h>

#define IR_PIN 14

// Wi‑Fi
const char* ssid = "00000000";
const char* password = "00000000";

// Server config
const char* serverIP = "10.31.237.192";
const uint16_t serverPort = 8000;
const char* endpoint = "/ingest";

// RSU info
const char* rsu_id = "ESP32_01";
const char* segment = "ESP_Segment";

RTC_DS3231 rtc;
int lastState = -1;
int vehicleCount = 0;

String incomingVehicleId = "";
String incomingSegment = "";

WebServer esp1Server(80);

void handleCarData() {
  if (esp1Server.hasArg("plain")) {
    String payload = esp1Server.arg("plain");
    incomingVehicleId = "";
    incomingSegment = "";

    int vidIdx = payload.indexOf("vehicle_id");
    int segIdx = payload.indexOf("segment");
    if (vidIdx != -1 && segIdx != -1) {
      int start = payload.indexOf(":", vidIdx) + 2;
      int end = payload.indexOf("\"", start);
      if (start != -1 && end != -1) {
        incomingVehicleId = payload.substring(start, end);
      }

      start = payload.indexOf(":", segIdx) + 2;
      end = payload.indexOf("\"", start);
      if (start != -1 && end != -1) {
        incomingSegment = payload.substring(start, end);
      }
    }
    esp1Server.send(200, "text/plain", "Data received");
    Serial.printf("Received vehicle: %s, segment: %s\n", incomingVehicleId.c_str(), incomingSegment.c_str());
  } else {
    esp1Server.send(400, "text/plain", "No payload");
  }
}

String makeIsoTimestamp(DateTime dt) {
  char buf[32];
  snprintf(buf, sizeof(buf), "%04u-%02u-%02uT%02u:%02u:%02u",
           dt.year(), dt.month(), dt.day(),
           dt.hour(), dt.minute(), dt.second());
  return String(buf);
}

void sendToServer(bool detected) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi not connected, abort send");
    return;
  }

  if (detected) {
    vehicleCount++;
  }

  String url = String("http://") + serverIP + ":" + String(serverPort) + endpoint;
  DateTime now = rtc.now();
  String timestamp = makeIsoTimestamp(now);

 String payload = "{";
payload += "\"rsu_id\":\"" + String(rsu_id) + "\",";
payload += "\"segment\":\"" + String(segment) + "\",";
payload += "\"vehicle_count\":" + String(vehicleCount) + ",";
payload += "\"vehicle_id\":\"" + incomingVehicleId + "\",";
payload += "\"timestamp\":\"" + timestamp + "\",";
payload += "\"speed\":42.0";
payload += "}";
  Serial.println("=== Sending to server ===");
  Serial.print("URL: "); Serial.println(url);
  Serial.print("Payload: "); Serial.println(payload);

  HTTPClient http;
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  int httpCode = http.POST(payload);
  if (httpCode > 0) {
    String resp = http.getString();
    Serial.printf("HTTP %d\n", httpCode);
    Serial.print("Response: "); Serial.println(resp);
  } else {
    Serial.printf("POST failed: %s\n", http.errorToString(httpCode).c_str());
  }
  http.end();
}

void setup() {
  Serial.begin(115200);
  pinMode(IR_PIN, INPUT_PULLUP);

  if (!rtc.begin()) {
    Serial.println("RTC not found!");
  } else if (rtc.lostPower()) {
    rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));
  }

  WiFi.begin(ssid, password);
  Serial.print("Connecting WiFi");
  unsigned long start = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - start < 20000) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("Local IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("Failed to connect WiFi");
  }

  esp1Server.on("/receive_car", HTTP_POST, handleCarData);
  esp1Server.begin();
}

void loop() {
  int irState = !digitalRead(IR_PIN); // Active LOW
  if (irState != lastState) {
    Serial.printf("Sensor change: %d -> %d\n", lastState, irState);
    if (irState == 1) sendToServer(true);
    lastState = irState;
  }

  esp1Server.handleClient();
  if (WiFi.status() != WL_CONNECTED) WiFi.reconnect();
  delay(50);
}