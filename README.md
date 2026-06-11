# Feeder Status LED Bar

Visuel status-enhed for **Dual Filament System** — en **ESP32** viser feeder-status, spolevægt og rumklima baseret på live-data fra `pi3feeder` (Moonraker/Klipper).

> **Opdateret juni 2026:** Host skiftet fra Pi Zero 2 W til ESP32. Se **[delivery_summary.md](delivery_summary.md)** for fuld status og teknologivalg.

Del af økosystemet omkring [Dual-Filament-System-P1S](https://github.com/ShadowMasterJedi/Dual-Filament-System-P1S).

## Formål

Et hurtigt **perifert blik** ved printerbænken: Er feederen klar? Er der filament? Er der runout? Ingen browser, ingen Mainsail — bare farver.

```
pi3feeder (Pi 3, Klipper)              feedled (ESP32)
        │                                       │
        │  Moonraker :7125                      │
        └──────────────────┬────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
   WS2812 LED-bar    SSD1306 OLED      Web :80
   (grøn/gul/rød)    vægt + klima
```

## Status-koder (LED)

| Farve | Mønster | Betydning |
|-------|---------|-----------|
| 🟢 Grøn | Fast | Klipper `ready`, downstream-sensor: filament OK |
| 🟡 Gul | Pulserende | Spool B preloadet / standby (`PRELOAD_B` kørt) |
| 🔴 Rød | Blink | Runout eller `FILAMENT_RUNOUT` / sensor tom |
| 🔵 Blå | Fast | Ekstern signal: P1S printer (MQTT/Home Assistant — valgfrit) |
| ⚫ Slukket | — | Moonraker offline / Pi Zero kan ikke nå `pi3feeder` |

Farver og mønstre konfigureres i `config.yaml`.

## Indkøb

Komplet indkøbsliste (begge Pi Zero-projekter): **[docs/bom.md](docs/bom.md)**

## Hardware

| Komponent | Antal | Note |
|-----------|-------|------|
| ESP32 DevKit (CH340) | 1 | Host — PlatformIO firmware |
| HX711 + load cell | 2 | Spool A + B vægt |
| SSD1306 OLED 0,96" I2C | 1 | Status + gram/meter |
| BME280 | 1 | Rum-temp + fugt (anbefalet) |
| WS2812B LED-strip | 8–16 LED | 5V, data på GPIO18 |
| 5V strømforsyning | 1 | Til LED-strip |
| 330 Ω modstand | 1 | LED data-linje |

**GPIO:** Se `delivery_summary.md` for komplet kort.

## Software

- **PlatformIO** + Arduino (`firmware/esp32/`)
- Moonraker REST-klient → `pi3feeder` (`192.168.50.14:7125`)
- WiFi, NTP, web-dashboard (v0.3 kører)
- HX711 + OLED + BME280 (v1.0 — efter moduler ankommer)
- **MQTT-prototype** med web-dashboard (v2.0 forberedelse) — se nedenfor

```bash
WIFI_PASSWORD='...' bash firmware/esp32/flash.sh
```

## MQTT + web-dashboard (prototype)

Grafisk filament-monitor (temp, fugt, gram tilbage) — kører på NUC til test, genbruges ved fase 2 MQTT:

```bash
pip3 install -r tools/mqtt_test/requirements.txt
bash tools/mqtt_test/run_web.sh
# → http://<NUC-IP>:8765/
```

Se [`tools/mqtt_test/README.md`](tools/mqtt_test/README.md) · design/UI i `tools/mqtt_test/web_dashboard.py`

## Konfiguration

`config.example.yaml`:

```yaml
moonraker:
  host: pi3feeder.local
  port: 7125

led:
  count: 12
  pin: 18
  brightness: 64
  freq_hz: 800000

sensors:
  downstream: filament_switch_sensor filament_sensor
```

## Opsætning

1. Klon repo, installér PlatformIO (`pip install platformio`)
2. Flash ESP32: `WIFI_PASSWORD='...' bash firmware/esp32/flash.sh`
3. Åbn web-dashboard på ESP32'ens IP (vises på seriel)
4. Tilslut HX711, OLED, BME280, LED-strip (se `delivery_summary.md`)
5. Kalibrér vægt via web `/calibrate` (v1.0)

## Relation til Dual Filament

| System | Rolle |
|--------|-------|
| `pi3feeder` (Pi 3) | Klipper-host, S6, feedere — **uændret** |
| `feedled` (ESP32) | Status, vægt, klima — læser, styrer ikke feedere |

## Status

🚧 **Fase:** ESP32 firmware v0.3 kører (WiFi + tid + vejr)  
⏳ **Næste:** v1.0 med HX711 + OLED + BME280 når moduler ankommer  

Se **[delivery_summary.md](delivery_summary.md)** for komplet overblik.

## Licens

MIT
