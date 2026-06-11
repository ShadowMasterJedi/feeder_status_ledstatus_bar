#!/usr/bin/env python3
"""Minimal MQTT broker (fallback når mosquitto ikke er installeret)."""
import asyncio
import os
import signal
import sys

from amqtt.broker import Broker

PORT = int(os.environ.get("MQTT_PORT", "1883"))
BIND = os.environ.get("MQTT_BIND", "0.0.0.0")


async def main() -> None:
    config = {
        "listeners": {
            "default": {
                "type": "tcp",
                "bind": f"{BIND}:{PORT}",
            },
        },
        "sys_interval": 10,
        "auth": {"allow-anonymous": True, "plugins": ["auth_anonymous"]},
    }
    broker = Broker(config)
    await broker.start()
    print(f"Python MQTT broker på mqtt://{BIND}:{PORT}")
    stop = asyncio.Event()

    def _stop(*_args):
        stop.set()

    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)
    await stop.wait()
    await broker.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
