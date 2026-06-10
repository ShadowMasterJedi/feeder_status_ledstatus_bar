#!/bin/bash
# Flash feedled ESP32 — WiFi + Moonraker dashboard
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
PORT="${PORT:-/dev/ttyUSB0}"
SECRETS="${DIR}/wifi_secrets.h"

export WIFI_SSID="${WIFI_SSID:-Waoo4920_998N}"
export WIFI_PASSWORD="${WIFI_PASSWORD:?Sæt WIFI_PASSWORD}"

export PATH="${HOME}/.local/bin:${PATH}"

if [ ! -e "${PORT}" ]; then
    echo "❌ Serielport ikke fundet: ${PORT}"
    exit 1
fi

if fuser "${PORT}" >/dev/null 2>&1; then
    echo "❌ ${PORT} optaget — luk serielmonitor (Ctrl+])"
    exit 1
fi

cat > "${SECRETS}" << EOF
#pragma once
#define WIFI_SSID     "${WIFI_SSID}"
#define WIFI_PASSWORD "${WIFI_PASSWORD}"
EOF

cd "${DIR}"
echo "=== Bygger (SSID: ${WIFI_SSID}) ==="
pio run

echo ""
echo "=== Flasher til ${PORT} ==="
pio run -t upload --upload-port "${PORT}"

echo ""
echo "✅ Flash færdig"
echo "   Serielmonitor:  pio device monitor --port ${PORT} --baud 115200"
echo "   Web-dashboard:  http://<ESP32-IP>/  (IP vises på seriel)"
