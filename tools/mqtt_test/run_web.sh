#!/bin/bash
# Broker + simulator + web-dashboard (ingen terminal-monitor)
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
BROKER="${MQTT_BROKER:-127.0.0.1}"
PORT="${MQTT_PORT:-1883}"
WEB_PORT="${WEB_PORT:-8765}"
CONF="${DIR}/mosquitto.conf"
PIDFILE="/tmp/feedled-mosquitto-test.pid"
BROKER_PIDFILE="/tmp/feedled-mqtt-broker.pid"

cleanup() {
    for f in "${PIDFILE}" "${BROKER_PIDFILE}"; do
        [ -f "${f}" ] && kill "$(cat "${f}")" 2>/dev/null || true
        rm -f "${f}"
    done
    [ -n "${SIM_PID:-}" ] && kill "${SIM_PID}" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

python3 -c "import paho.mqtt.client" 2>/dev/null || {
    pip3 install -r "${DIR}/requirements.txt"
}

for f in "${PIDFILE}" "${BROKER_PIDFILE}"; do
    [ -f "${f}" ] && kill "$(cat "${f}")" 2>/dev/null || true
    rm -f "${f}"
done

NUC_IP="$(hostname -I | awk '{print $1}')"
echo "=== feedled MQTT web-test ==="

if command -v mosquitto >/dev/null; then
    mosquitto -c "${CONF}" -v &
    echo $! > "${PIDFILE}"
else
    python3 "${DIR}/broker.py" &
    echo $! > "${BROKER_PIDFILE}"
fi
sleep 2

export MQTT_BROKER="${BROKER}" MQTT_PORT="${PORT}"
python3 "${DIR}/filament_simulator.py" &
SIM_PID=$!
sleep 1

echo ""
echo "  Web:    http://127.0.0.1:${WEB_PORT}/"
echo "  LAN:    http://${NUC_IP}:${WEB_PORT}/"
echo "  MQTT:   mqtt://${BROKER}:${PORT}"
echo "  Ctrl+C stopper alt"
echo ""

export WEB_PORT
python3 "${DIR}/web_dashboard.py"
