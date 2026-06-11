# feedled – Delivery Summary & Memory Context

**Projektnavn**: feedled (Feeder Status + Spool Tracker)  
**Repo**: https://github.com/ShadowMasterJedi/feeder_status_ledstatus_bar  
**Dato**: 10. juni 2026  
**Status**: ESP32 firmware i gang · HX711 + sensorer på vej (~5 dage)  
**Sværhedsgrad**: Medium  
**Del af**: [Dual-Filament-System-P1S](https://github.com/ShadowMasterJedi/Dual-Filament-System-P1S)

---

## Projektmål

Perifer **status- og overvågningsenhed** ved printerbænken for Dual Filament System:

- Hurtigt blik: Er Klipper klar? Filament OK? Runout?
- **Tidlig advarsel** før runout via spolevægt (gram + meter tilbage)
- Rumklima (temp + fugt) for filament-opbevaring
- Ingen browser nødvendig — OLED + LED-bar + valgfrit web-dashboard

---

## Teknologivalg (besluttet juni 2026)

| Oprindelig plan | Valgt løsning | Begrundelse |
|-----------------|---------------|-------------|
| Raspberry Pi Zero 2 W | **ESP32-D0WD-V3** (CH340 DevKit) | Allerede på lager, lavere strøm, GPIO nok til alt |
| Python + `rpi_ws281x` | **C++ / Arduino / PlatformIO** | Native timing til HX711, WS2812, I2C |
| Kun LED-bar | **LED + OLED + vægt + klima** | Én enhed dækker feedled + spool-tracker |
| Pi Zero til spool-tracker | **Samlet på ESP32** | Pi Zero #2 frigøres til andet |

### Software-stack

| Lag | Teknologi |
|-----|-----------|
| Firmware | PlatformIO + `espressif32` + Arduino framework |
| Flash | `esptool` via `firmware/esp32/flash.sh` |
| WiFi | ESP32 STA → `Waoo4920_998N` |
| Tid | NTP (`0.dk.pool.ntp.org`) · tidszone `Europe/Copenhagen` |
| Vejr (bonus) | Open-Meteo API (HTTPS) · 5-dages prognose |
| Klipper-data | Moonraker REST → `192.168.50.14:7125` (pi3feeder) |
| Web-UI | ESP32 `WebServer` på port 80 |
| Vægt (planlagt) | HX711 ×2 + load cell ×2 |
| Display (planlagt) | SSD1306 0,96" OLED (I2C `0x3C`) |
| Klima (planlagt) | BME280 (I2C, deler bus med OLED) |
| LED-bar (planlagt) | WS2812B ×8–16 (GPIO18) |

---

## System-arkitektur

```
pi3feeder (Pi 3, Klipper)                    feedled (ESP32)
        │                                           │
        │  Moonraker :7125                          │
        └──────────────────┬────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
   WS2812 LED-bar    SSD1306 OLED      Web-dashboard
   (grøn/gul/rød)    vægt + status    :80 /status
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
         HX711 #1     HX711 #2      BME280
         Spool A      Spool B       temp/fugt
```

**Vigtigt**: ESP32 **læser og viser** — den styrer ikke feedere direkte (undtagen valgfri knap → Moonraker-macro).

---

## Hardware-status

| Komponent | Antal | Status |
|-----------|-------|--------|
| ESP32 DevKit (CH340, 4 MB flash) | 1 | ✅ I brug — IP `192.168.50.123` |
| Load cell (1–5 kg) | 5 | ✅ Købt — brug 2 (A+B), 3 reserve |
| HX711 modul | 2 | 🚚 Bestilt — forventet inden 5 dage |
| SSD1306 OLED 0,96" I2C | 1 | ⏳ Skal købes / på lager? |
| BME280 (temp + fugt) | 1 | ⏳ Anbefalet — skal købes |
| WS2812B LED-strip | 0,5 m | ⏳ Se `docs/bom.md` |
| 5V PSU til LED | 1 | ⏳ Se `docs/bom.md` |
| 330 Ω modstand (LED data) | 1 | ⏳ Se `docs/bom.md` |
| Raspberry Pi Zero 2 W | 2 | ✅ På lager — **ikke** brugt til feedled |

### ESP32 identitet (NUC flash-session)

| Parameter | Værdi |
|-----------|-------|
| Chip | ESP32-D0WD-V3 (rev 3.1) |
| Flash | 4 MB |
| MAC | `94:51:dc:4c:72:74` |
| USB-serial | CH340 → `/dev/ttyUSB0` |
| Pi-host | `pi3feeder` @ `192.168.50.14` |

---

## GPIO-kort (ESP32)

| GPIO | Funktion | Status |
|------|----------|--------|
| 2 | Onboard blå LED (status) | ✅ I brug |
| 16 | HX711 #1 DT (Spool A) | ⏳ Planlagt |
| 17 | HX711 #1 SCK | ⏳ Planlagt |
| 32 | HX711 #2 DT (Spool B) | ⏳ Planlagt |
| 33 | HX711 #2 SCK | ⏳ Planlagt |
| 18 | WS2812B data | ⏳ Planlagt |
| 21 | I2C SDA (OLED + BME280) | ⏳ Planlagt |
| 22 | I2C SCL | ⏳ Planlagt |
| 0 | Fysisk knap (BOOT) | ⏳ Planlagt |

---

## LED-bar status-koder (uændret fra original design)

| Farve | Mønster | Betydning |
|-------|---------|-----------|
| 🟢 Grøn | Fast | Klipper `ready`, filament OK |
| 🟡 Gul | Pulserende | Spool B standby / preload |
| 🔴 Rød | Blink | Runout / lav vægt (`<50 g`) |
| 🔵 Blå | Fast | P1S printer (fase 2 / MQTT) |
| ⚫ Slukket | — | Moonraker offline |

---

## OLED-skærme (planlagt rotation)

| Skærm | Indhold |
|-------|---------|
| 1 — Feeder | Klipper-state, filament-sensor, Spool B status |
| 2 — Vægt | Spool A + B: gram, meter, bargraf |
| 3 — Klima | Rum-temp, fugt %, fugt-alarm |

---

## Firmware-status

| Fase | Indhold | Status |
|------|---------|--------|
| v0.1 | LED blink / oracle (test) | ✅ Flashet |
| v0.2 | WiFi + Moonraker dashboard | ✅ Flashet |
| v0.3 | NTP atomur + 5-dages vejr (Open-Meteo) | ✅ Flashet — kører nu |
| **v1.0** | HX711 ×2 + OLED + BME280 + LED-bar + Moonraker | ⏳ Efter HX711 ankommer |
| v1.1 | Web `/calibrate` + NVS kalibrering | ⏳ Planlagt |
| v2.0 | MQTT / OTA / mDNS `feedled.local` | 🧪 Prototype klar (NUC) |
| v2.0-web | Filament-dashboard (Spool A/B, ring-diagram) | ✅ `tools/mqtt_test/web_dashboard.py` |

### Repo-filer (MQTT-prototype)

| Fil | Indhold |
|-----|---------|
| `tools/mqtt_test/run_web.sh` | Broker + simulator + web på port **8765** |
| `tools/mqtt_test/web_dashboard.py` | Grafisk UI (temp, RH, remaining g) |
| `tools/mqtt_test/filament_simulator.py` | `feedled/box1` + `box2` MQTT-emner |
| `firmware/esp32_mqtt_test/` | ESP32 node der lytter på MQTT |

Start på NUC: `bash tools/mqtt_test/run_web.sh` → `http://192.168.50.119:8765/`

### Repo-filer (firmware)

| Fil | Indhold |
|-----|---------|
| `firmware/esp32/src/main.cpp` | Aktuel firmware (tid + vejr + web) |
| `firmware/esp32/platformio.ini` | PlatformIO env `esp32dev` |
| `firmware/esp32/flash.sh` | Build + flash (`WIFI_PASSWORD` påkrævet) |
| `firmware/esp32/wifi_secrets.h.example` | WiFi + valgfri vejrplacering |

### Flash-kommando

```bash
WIFI_PASSWORD='...' bash firmware/esp32/flash.sh
```

---

## v1 features (besluttet — implementeres ved HX711-ankomst)

- [x] WiFi-forbindelse
- [x] NTP dansk atomur
- [x] Web-dashboard
- [ ] Moonraker live-status (Klipper + filament-sensor)
- [ ] HX711 ×2 — Spool A + B vægt
- [ ] Gram + estimeret meter tilbage
- [ ] Tidlig advarsel ved lav vægt
- [ ] BME280 rumtemp + fugt
- [ ] SSD1306 OLED (3 roterende skærme)
- [ ] WS2812 LED-bar (statusfarver)
- [ ] Kalibrering gemt i NVS
- [ ] Web `/calibrate` (tare + skala)
- [ ] JSON `/status` API
- [ ] Fysisk knap: skift skærm / `PRELOAD_B`

---

## Relation til økosystem

| System | Rolle | Ændres? |
|--------|-------|---------|
| `pi3feeder` (Pi 3) | Klipper-host, S6, feedere | **Nej** |
| `feedled` (ESP32) | Status, vægt, klima — kun læsning | Ny host |
| P1S | Printer | Nej |
| NUC (`linuxrobot`) | Flash-station, UR3 | Nej |
| Spool_weight_tracker (Pi Zero) | — | **Erstattet** af ESP32-vægt |

---

## Åbne punkter

- [ ] HX711-moduler ankommer og testes
- [ ] Køb/tilslut OLED + BME280
- [ ] Print 2× spool-holder (én celle per spole)
- [ ] Kalibrér begge celler (tare + 200 g referencevægt)
- [ ] Implementér v1.0 firmware
- [ ] Monter WS2812 ved printerbænk
- [ ] Opdatér `docs/bom.md` med ESP32-host (erstatter Pi Zero #1)
- [ ] Fase 2: MQTT til Home Assistant (UI-prototype findes i `tools/mqtt_test/`)

---

## Session-noter

- **10. juni 2026**: Projekt pivoteret fra Pi Zero → ESP32. CH340 USB-serial fix (BRLTTY fjernet på NUC). Firmware v0.1–v0.3 flashet fra `linuxrobot`. Dashboard live på `http://192.168.50.123`. 5× load cell købt, 2× HX711 bestilt (ankomst ~5 dage). Beslutning: samlet feedled + spool-tracker på én ESP32.
- **11. juni 2026**: MQTT filament-test på NUC med simulator + grafisk web-dashboard (Spool A/B). Committet til GitHub — genbrug ved v2.0.

---

*Sidst opdateret: 11. juni 2026*
