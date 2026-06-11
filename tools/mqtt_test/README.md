# MQTT filament-test (NUC ↔ ESP32)

Lille server/node-setup til at verificere MQTT før rigtige sensorer (BME280, HX711) er på ESP32.

## Arkitektur

```
NUC (linuxrobot)                    ESP32 (valgfri node)
┌─────────────────┐                ┌──────────────────┐
│ Mosquitto :1883 │◄── WiFi ──────│ esp32_mqtt_test  │
│ filament_sim    │   subscribe   │ Serial log       │
│ monitor         │               └──────────────────┘
└─────────────────┘
```

## Emner (topics)

| Topic | Indhold | Eksempel |
|-------|---------|----------|
| `feedled/box1/temperature` | °C | `22.4` |
| `feedled/box1/humidity` | % RH | `47.8` |
| `feedled/box1/remaining` | gram tilbage | `978.2` |
| `feedled/box1/state` | JSON | `{"temperature_c":22.4,...}` |
| `feedled/box2/...` | Spool B | samme |

`box1` = Spool A, `box2` = Spool B.

## Hurtig start (NUC)

```bash
pip3 install -r tools/mqtt_test/requirements.txt
bash tools/mqtt_test/run.sh
```

`run.sh` starter en **Python-broker** automatisk (ingen sudo). Valgfrit: `sudo apt install mosquitto` for Mosquitto i stedet.

Kun simulator (anden terminal):

```bash
MQTT_BROKER=127.0.0.1 python3 tools/mqtt_test/filament_simulator.py
```

**Web-dashboard** (anbefalet):

```bash
bash tools/mqtt_test/run_web.sh
```

Åbn i browser: `http://192.168.50.119:8765/` (eller `http://127.0.0.1:8765/`)

Kun monitor (terminal):

```bash
python3 tools/mqtt_test/monitor.py
```

Manuel test med `mosquitto_sub`:

```bash
mosquitto_sub -h 127.0.0.1 -t 'feedled/#' -v
```

## ESP32 som node (valgfrit)

Flash MQTT-testfirmware — abonnerer på `feedled/#` og logger på Serial:

```bash
WIFI_PASSWORD='...' MQTT_BROKER='192.168.50.119' \
  bash firmware/esp32_mqtt_test/flash.sh
```

Åbn Serial Monitor (115200) — du skal se opdateringer hvert ~3 sek.

## Miljøvariabler

| Variabel | Standard | Betydning |
|----------|----------|-----------|
| `MQTT_BROKER` | `127.0.0.1` | Broker IP (NUC: `192.168.50.119`) |
| `MQTT_PORT` | `1883` | Broker port |
| `MQTT_PREFIX` | `feedled` | Topic-præfiks |
| `MQTT_INTERVAL` | `3` | Simulator interval (sek) |
