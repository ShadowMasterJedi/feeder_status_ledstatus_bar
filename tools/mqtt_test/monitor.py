#!/usr/bin/env python3
"""MQTT monitor — viser alle feedled-emner live."""
import os
import sys

import paho.mqtt.client as mqtt

BROKER = os.environ.get("MQTT_BROKER", "127.0.0.1")
PORT = int(os.environ.get("MQTT_PORT", "1883"))
PREFIX = os.environ.get("MQTT_PREFIX", "feedled")


def on_connect(client, _userdata, _flags, reason_code, _props):
    if reason_code != 0:
        print(f"Connect fejlede: {reason_code}")
        return
    client.subscribe(f"{PREFIX}/#")
    print(f"Lytter på mqtt://{BROKER}:{PORT}  →  {PREFIX}/#")
    print("-" * 60)


def on_message(_client, _userdata, msg):
    topic = msg.topic
    try:
        text = msg.payload.decode("utf-8")
    except UnicodeDecodeError:
        text = repr(msg.payload)
    print(f"{topic:40} {text}")


def main() -> int:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="filament-monitor")
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, 60)
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("\nStop.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
