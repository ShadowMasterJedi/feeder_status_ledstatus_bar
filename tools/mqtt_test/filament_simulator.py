#!/usr/bin/env python3
"""Simulerer 2 filament-bokse: temp, fugt (RH) og resterende vægt (g)."""
import json
import math
import os
import random
import signal
import sys
import time

import paho.mqtt.client as mqtt

BROKER = os.environ.get("MQTT_BROKER", "127.0.0.1")
PORT = int(os.environ.get("MQTT_PORT", "1883"))
PREFIX = os.environ.get("MQTT_PREFIX", "feedled")
INTERVAL = float(os.environ.get("MQTT_INTERVAL", "3"))

BOXES = {
    "box1": {"label": "Spool A", "remaining": 980.0, "drain": 0.35},
    "box2": {"label": "Spool B", "remaining": 412.0, "drain": 0.12},
}


def publish_box(client: mqtt.Client, box_id: str, t: float) -> None:
    meta = BOXES[box_id]
    phase = hash(box_id) % 100

    temp = 22.0 + 2.5 * math.sin(t / 120 + phase) + random.uniform(-0.2, 0.2)
    humidity = 45.0 + 8.0 * math.sin(t / 90 + phase * 0.7) + random.uniform(-1.0, 1.0)
    humidity = max(30.0, min(65.0, humidity))

    meta["remaining"] = max(0.0, meta["remaining"] - meta["drain"] + random.uniform(-0.05, 0.05))

    base = f"{PREFIX}/{box_id}"
    payload = {
        "label": meta["label"],
        "temperature_c": round(temp, 1),
        "humidity_pct": round(humidity, 1),
        "remaining_g": round(meta["remaining"], 1),
    }

    client.publish(f"{base}/temperature", f"{payload['temperature_c']:.1f}", qos=0, retain=True)
    client.publish(f"{base}/humidity", f"{payload['humidity_pct']:.1f}", qos=0, retain=True)
    client.publish(f"{base}/remaining", f"{payload['remaining_g']:.1f}", qos=0, retain=True)
    client.publish(f"{base}/state", json.dumps(payload), qos=0, retain=True)


def main() -> int:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="filament-simulator")
    client.connect(BROKER, PORT, 60)
    client.loop_start()

    print(f"Simulator → mqtt://{BROKER}:{PORT}  prefix={PREFIX}/  interval={INTERVAL}s")
    print("Topics: feedled/box1|box2/{temperature,humidity,remaining,state}")
    print("Ctrl+C for at stoppe\n")

    t0 = time.time()

    def stop(_sig, _frame):
        client.loop_stop()
        client.disconnect()
        sys.exit(0)

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)

    while True:
        t = time.time() - t0
        for box_id in BOXES:
            publish_box(client, box_id, t)
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
