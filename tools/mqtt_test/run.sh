#!/bin/bash
# Start lokal MQTT-test: broker + simulator + monitor
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
BROKER="${MQTT_BROKER:-127.0.0.1}"
PORT="${MQTT_PORT:-1883}"
CONF="${DIR}/mosquitto.conf"
PIDFILE="/tmp/feedled-mosquitto-test.pid"
BROKER_PIDFILE="/tmp/feedled-mqtt-broker.pid"

cleanup() {
    for f in "${PIDFILE}" "${BROKER_PIDFILE}"; do
        if [ -f "${f}" ]; then
            kill "$(cat "${f}")" 2>/dev/null || true
            rm -f "${f}"
        fi
    done
    [ -n "${SIM_PID:-}" ] && kill "${SIM_PID}" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

python3 -c "import paho.mqtt.client" 2>/dev/null || {
    echo "Installer:  pip3 install -r ${DIR}/requirements.txt"
    exit 1
}

for f in "${PIDFILE}" "${BROKER_PIDFILE}"; do
    [ -f "${f}" ] && kill "$(cat "${f}")" 2>/dev/null || true
    rm -f "${f}"
done

echo "=== MQTT filament-test ==="
echo "Broker:  mqtt://${BROKER}:${PORT}"
echo "NUC IP:  $(hostname -I | awk '{print $1}')  (ESP32: MQTT_BROKER=<denne IP>)"
echo ""

if command -v mosquitto >/dev/null; then
    echo "Starter mosquitto..."
    mosquitto -c "${CONF}" -v &
    echo $! > "${PIDFILE}"
else
    echo "Starter Python-broker (ingen mosquitto — eller: sudo apt install mosquitto)"
    python3 "${DIR}/broker.py" &
    echo $! > "${BROKER_PIDFILE}"
fi
sleep 2

export MQTT_BROKER="${BROKER}" MQTT_PORT="${PORT}"
python3 "${DIR}/filament_simulator.py" &
SIM_PID=$!
sleep 2

python3 "${DIR}/monitor.py"
