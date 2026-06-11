#!/bin/bash
# Flash ESP32 MQTT node-test
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "${DIR}/../.." && pwd)"
SECRETS="${DIR}/wifi_secrets.h"
EXAMPLE="${DIR}/wifi_secrets.h.example"
MAIN_SECRETS="${ROOT}/firmware/esp32/wifi_secrets.h"

UPLOAD_PORT="${UPLOAD_PORT:-/dev/ttyUSB1}"
MQTT_BROKER="${MQTT_BROKER:-192.168.50.119}"

if [ -z "${WIFI_PASSWORD:-}" ]; then
    echo "Brug: WIFI_PASSWORD='...' [MQTT_BROKER=IP] [UPLOAD_PORT=/dev/ttyUSB1] bash $0"
    exit 1
fi

SSID="${WIFI_SSID:-Waoo4920_998N}"

if [ -f "${MAIN_SECRETS}" ]; then
    SSID="$(grep WIFI_SSID "${MAIN_SECRETS}" | cut -d'"' -f2)"
fi

cat > "${SECRETS}" <<EOF
#pragma once
#define WIFI_SSID     "${SSID}"
#define WIFI_PASSWORD "${WIFI_PASSWORD}"
#define MQTT_BROKER   "${MQTT_BROKER}"
#define MQTT_PORT     1883
#define MQTT_PREFIX   "feedled"
EOF

echo "=== Flash MQTT node-test ==="
echo "    Port:   ${UPLOAD_PORT}"
echo "    Broker: ${MQTT_BROKER}"
echo "    WiFi:   ${SSID}"
echo ""

cd "${DIR}"
pio run -t upload --upload-port "${UPLOAD_PORT}"
pio device monitor --port "${UPLOAD_PORT}" --baud 115200
