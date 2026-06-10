# Feeder Status LED Bar

Visuel status-bar for **Dual Filament System** — en Raspberry Pi Zero 2 W styrer WS2812/NeoPixel-LED'er baseret på live-data fra `pi3feeder` (Moonraker/Klipper).

Del af økosystemet omkring [Dual-Filament-System-P1S](https://github.com/ShadowMasterJedi/Dual-Filament-System-P1S).

## Formål

Et hurtigt **perifert blik** ved printerbænken: Er feederen klar? Er der filament? Er der runout? Ingen browser, ingen Mainsail — bare farver.

```
pi3feeder (Pi 3, Klipper)          Pi Zero 2 W (dette projekt)
        │                                    │
        │  Moonraker WebSocket :7125         │
        └──────────────┬─────────────────────┘
                       │
                 WS2812 LED-bar
              (grøn / gul / rød / blå)
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

## Hardware

| Komponent | Antal | Note |
|-----------|-------|------|
| Raspberry Pi Zero 2 W | 1 | Pi OS Lite, 8 GB SD er nok |
| WS2812B LED-strip eller ring | 8–16 LED | 5V, data på GPIO18 |
| 5V strømforsyning | 1 | Delt med LED (ikke fra Pi 5V-pin alene ved mange LED) |
| 330 Ω modstand | 1 | Data-linje (anbefalet) |
| Jumper-ledninger | — | Pi GPIO → DIN på strip |

**GPIO (standard):** Data = GPIO18 (PWM0), GND fælles med PSU.

## Software (planlagt)

- Python 3 + `rpi_ws281x` (LED)
- Moonraker WebSocket-klient (samme RPC-mønster som Dual-Filament dashboard)
- Abonnerer på: `webhooks`, `filament_switch_sensor filament_sensor`, `gcode_macro _FEEDER_VARS`

```bash
# Eksempel — når implementeret
sudo apt install python3-pip
pip3 install rpi-ws281x websocket-client pyyaml
python3 feeder_led.py
```

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

1. Flash Pi OS Lite på Pi Zero 2 W (8 GB SD)
2. WiFi + hostname, fx `feederled.local` — brug `configure_pi_wifi.sh` fra Dual-Filament-repo
3. Klon dette repo på Zero'en
4. Tilslut LED-strip, test med `python3 feeder_led.py --test`
5. Kør som systemd-service (`feeder-led.service`)

## Relation til Dual Filament

| System | Rolle |
|--------|-------|
| `pi3feeder` (Pi 3) | Klipper-host, S6, feedere — **uændret** |
| `feederled` (Pi Zero) | Kun status-visning — læser, styrer ikke feedere |

## Status

🚧 **Fase:** Projektbeskrivelse / tidlig udvikling  
Ingen produktionskode endnu — README og arkitektur først.

## Licens

MIT
