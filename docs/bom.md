# Indkøbsliste (BOM) — Pi Zero perifer-projekter

Samlet indkøbsliste til **Feeder Status LED Bar** og **Spool Weight Tracker**.  
Estimerede priser i **DKK** (Amazon.de / danske shops, juni 2026).

> **Status:** Du har **2× Raspberry Pi Zero** — ét board per projekt. Ingen Pi-køb nødvendig.

---

## Hurtig oversigt

| Scope | Est. pris |
|-------|-----------|
| Kun LED Bar (ekskl. Pi/SD) | **~110–260 DKK** |
| Kun Spool Tracker (ekskl. Pi/SD) | **~85–180 DKK** |
| **Begge projekter — rest der mangler** | **~195–440 DKK** |

*(Pi Zero ×2 og 1× flashet 8 GB SD er allerede på lager.)*

---

## Allerede på lager ✅

| Komponent | Antal | Projekt |
|-----------|-------|---------|
| **Raspberry Pi Zero** (2 W anbefalet) | 2 | LED Bar + Spool Tracker |
| **microSD 8 GB** flashet Pi OS Lite | 1 | Andet projekt (færdig flash) |
| `pi3feeder` på netværk | 1 | LED Bar læser Moonraker — gratis |
| WiFi-scripts (Dual-Filament-repo) | — | Flash/konfig begge SD-kort |

### Mangler stadig fra fælles udstyr

| # | Komponent | Antal | Est. pris | Note |
|---|-----------|-------|-----------|------|
| F1 | **microSD 8 GB** | **1** | 40–60 DKK | Andet SD til anden Pi |
| F2 | **micro-USB strømadapter** 5V 2,5A | 1–2 | 40–120 DKK | Én PSU OK hvis begge Pi på samme bænk via hub |
| F3 | **micro-USB kabel** (data+strøm) | 0–1 | 0–40 DKK | Ofte inkl. i kit |

**Fælles der mangler:** ~**40–160 DKK** (primært 1 ekstra SD-kort)

### Anbefalede hostnames

| Pi | Hostname | Projekt |
|----|----------|---------|
| Pi #1 | `feederled.local` | LED Bar |
| Pi #2 | `spooltrack.local` | Spool Weight Tracker |

---

## Projekt 1 — Feeder Status LED Bar

| # | Komponent | Antal | Est. pris/stk | Est. total | Note / søgeord |
|---|-----------|-------|---------------|------------|----------------|
| L1 | **WS2812B LED-strip** 30 LED/m, IP30 | 0,5 m (≈15 LED) | 40–70 DKK | 40–70 DKK | "WS2812B 1m 30LED" — klip til 12–16 LED |
| L2 | **5V PSU** til LED (min. 2A) | 1 | 50–80 DKK | 50–80 DKK | **Ikke** kun Pi 5V-pin ved >8 LED |
| L3 | **330 Ω modstand** | 1 | 5 DKK | 5 DKK | Data-linje GPIO18 → DIN |
| L4 | **Jumper-ledninger** dupont hun-hun | 1 sæt | 15–25 DKK | 15–25 DKK | Pi → strip |
| L5 | **Aluminium-profil** for LED (valgfrit) | 0,5 m | 40–80 DKK | 0–80 DKK | Pæn status-bar på hylden |

**Projekt 1 — skal købes:** ~**110–260 DKK**

### LED Bar — farvekoder (reference)

| LED | Funktion |
|-----|----------|
| Grøn fast | Klipper ready + filament OK |
| Gul puls | Spool B standby |
| Rød blink | Runout |
| Blå fast | P1S printer (valgfrit) |

---

## Projekt 2 — Spool Weight Tracker

| # | Komponent | Antal | Est. pris/stk | Est. total | Note / søgeord |
|---|-----------|-------|---------------|------------|----------------|
| S1 | **HX711 vægtmodul** | 1 | 15–30 DKK | 15–30 DKK | "HX711 load cell amplifier" |
| S2 | **Load cell 1 kg** (eller 5 kg) | 1 | 25–50 DKK | 25–50 DKK | 1 kg nok til spole |
| S3 | **0,96" OLED SSD1306** I2C | 1 | 20–35 DKK | 20–35 DKK | Valgfri — viser gram tilbage |
| S4 | **3D-printet spool-base** | 1 | — | ~10 DKK | Filament — spole kun på cellen |
| S5 | **M3 skruer + afstandskiver** | 1 sæt | 15–25 DKK | 15–25 DKK | Montering cell + Pi-hus |
| S6 | **Kalibreringsvægt** 200 g | 1 | 0–30 DKK | 0–30 DKK | Møntvægt eller kendt masse |

**Projekt 2 — skal købes:** ~**85–180 DKK**

### GPIO (reference)

| Modul | Pi Zero GPIO |
|-------|----------------|
| HX711 DT | GPIO5 |
| HX711 SCK | GPIO6 |
| OLED SDA | GPIO2 |
| OLED SCL | GPIO3 |

---

## Samlet indkøbsliste — kryds af

```
ALLEREDE HAR ✅
[x] Raspberry Pi Zero                    ×2
[x] microSD 8 GB + Pi OS Lite flash      ×1

SKAL KØBES
[ ] microSD 8 GB                         ×1  (anden Pi)
[ ] micro-USB PSU 5V 2,5A                ×1–2

LED BAR (Pi #1 → feederled)
[ ] WS2812B strip ~0,5 m
[ ] 5V PSU til LED (2A+)
[ ] 330 Ω modstand
[ ] Jumper-ledninger

SPOOL TRACKER (Pi #2 → spooltrack)
[ ] HX711 modul
[ ] Load cell 1 kg
[ ] OLED SSD1306 0,96" (valgfri)
[ ] Print spool-base
```

---

## Anbefalet rækkefølge

1. Køb **1 ekstra microSD 8 GB** — flash med `configure_pi_wifi.sh`  
2. **LED Bar først** på Pi #1 — færrest dele, hurtigst resultat  
3. **Spool Tracker** på Pi #2 — print base + kalibrering  

---

## Undgå

| Produkt | Hvorfor |
|---------|---------|
| Raspberry Pi Zero (flere) | Du har allerede 2 ✅ |
| Raspberry Pi **Pico** | Ingen Linux |
| Pi Zero **W** v1 (1 kerne) | For svag til disse projekter |
| SK6812 RGBW | WS2812B er nok |
| Load cell uden HX711 | HX711 inkluderer forstærker |

---

## Links

| Projekt | Repo |
|---------|------|
| LED Bar | [feeder_status_ledstatus_bar](https://github.com/ShadowMasterJedi/feeder_status_ledstatus_bar) |
| Spool Tracker | [Spool_weight_tracker](https://github.com/ShadowMasterJedi/Spool_weight_tracker) |
| Dual Filament | [Dual-Filament-System-P1S](https://github.com/ShadowMasterJedi/Dual-Filament-System-P1S) |

---

*Sidst opdateret: juni 2026 — 2× Pi Zero på lager*
