#include <Arduino.h>
#include <PubSubClient.h>
#include <WiFi.h>

#include "wifi_secrets.h"

constexpr uint8_t LED_PIN = 2;

WiFiClient wifiClient;
PubSubClient mqtt(wifiClient);
uint32_t lastBlink = 0;
uint32_t msgCount = 0;

void blinkLed() {
    digitalWrite(LED_PIN, !digitalRead(LED_PIN));
}

void onMessage(char *topic, uint8_t *payload, unsigned int length) {
    String body;
    body.reserve(length + 1);
    for (unsigned int i = 0; i < length; i++) {
        body += static_cast<char>(payload[i]);
    }
    Serial.printf("[MQTT] %s → %s\n", topic, body.c_str());
    msgCount++;
    lastBlink = millis();
    digitalWrite(LED_PIN, HIGH);
}

void connectWifi() {
    Serial.printf("WiFi → %s\n", WIFI_SSID);
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    uint8_t dots = 0;
    while (WiFi.status() != WL_CONNECTED) {
        delay(400);
        Serial.print(".");
        if (++dots % 20 == 0) Serial.println();
        blinkLed();
    }
    Serial.printf("\nWiFi OK  IP=%s\n", WiFi.localIP().toString().c_str());
    digitalWrite(LED_PIN, LOW);
}

void connectMqtt() {
    mqtt.setServer(MQTT_BROKER, MQTT_PORT);
    mqtt.setCallback(onMessage);
    mqtt.setBufferSize(512);

    String clientId = "feedled-node-" + String((uint32_t)ESP.getEfuseMac(), HEX);

    while (!mqtt.connected()) {
        Serial.printf("MQTT → %s:%d  id=%s\n", MQTT_BROKER, MQTT_PORT, clientId.c_str());
        if (mqtt.connect(clientId.c_str())) {
            String topic = String(MQTT_PREFIX) + "/#";
            mqtt.subscribe(topic.c_str());
            Serial.printf("MQTT OK  subscribe %s\n", topic.c_str());
        } else {
            Serial.printf("MQTT fejl %d — retry 3s\n", mqtt.state());
            delay(3000);
        }
    }
}

void setup() {
    Serial.begin(115200);
    delay(500);
    pinMode(LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, LOW);

    Serial.println();
    Serial.println("=== feedled MQTT node test ===");
    connectWifi();
    connectMqtt();
}

void loop() {
    if (WiFi.status() != WL_CONNECTED) {
        connectWifi();
    }
    if (!mqtt.connected()) {
        connectMqtt();
    }
    mqtt.loop();

    if (millis() - lastBlink > 150) {
        if (millis() - lastBlink < 800) {
            blinkLed();
        } else {
            digitalWrite(LED_PIN, LOW);
        }
    }

    static uint32_t lastStats = 0;
    if (millis() - lastStats > 30000) {
        lastStats = millis();
        Serial.printf("Stats: %u beskeder modtaget\n", msgCount);
    }
}
