# Indkøbsliste (BOM) — Pi Zero perifer-projekter

Samlet indkøbsliste til **Feeder Status LED Bar** og **Spool Weight Tracker**.  
Estimerede priser i **DKK** (Amazon.de / danske shops, juni 2026).

> **Bemærk:** Hvert projekt er designet til **sin egen Pi Zero 2 W**. Køber du begge, skal du bruge **2 boards** (eller én Pi med begge funktioner — kræver mere GPIO/planlægning).

---

## Hurtig oversigt

| Scope | Est. pris |
|-------|-----------|
| Kun LED Bar | **~150–250 DKK** |
| Kun Spool Tracker | **~120–200 DKK** |
| **Begge projekter** | **~320–480 DKK** |

*(Pi Zero 2 W med header og SD er den største post.)*

---

## Fælles — købes én gang per Pi

| # | Komponent | Antal (1 projekt) | Antal (begge) | Est. pris/stk | Est. total | Hvor |
|---|-----------|-------------------|---------------|---------------|------------|------|
| F1 | **Raspberry Pi Zero 2 W** (med header) | 1 | 2 | 150–220 DKK | 300–440 DKK | Pimoroni, Kubii, Amazon |
| F2 | **microSD 8 GB** (Pi OS Lite) | 1 | 2 | 40–60 DKK | 80–120 DKK | Har du allerede 1 flashet |
| F3 | **micro-USB strømkabel** (data+strøm) | 1 | 2 | 25–40 DKK | 50–80 DKK | Ofte inkl. i Pi-kit |
| F4 | **micro-USB strømadapter** 5V 2,5A | 1 | 2 | 40–60 DKK | 80–120 DKK | Del én PSU hvis samme bænk |

**Fælles subtotal (begge projekter, uden SD du har):** ~**250–400 DKK**

---

## Projekt 1 — Feeder Status LED Bar

| # | Komponent | Antal | Est. pris/stk | Est. total | Note / søgeord |
|---|-----------|-------|---------------|------------|----------------|
| L1 | **WS2812B LED-strip** 30 LED/m, IP30 | 0,5 m (≈15 LED) | 40–70 DKK | 40–70 DKK | "WS2812B 1m 30LED" — klip til 12–16 LED |
| L2 | **5V PSU** til LED (min. 2A) | 1 | 50–80 DKK | 50–80 DKK | USB-barrel eller separat 5V — **ikke** kun Pi-pin ved >8 LED |
| L3 | **330 Ω modstand** | 1 | 5 DKK | 5 DKK | Data-linje GPIO18 → DIN |
| L4 | **Jumper-ledninger** dupont hun-hun | 1 sæt | 15–25 DKK | 15–25 DKK | Pi → strip |
| L5 | **Aluminium-profil** for LED (valgfrit) | 0,5 m | 40–80 DKK | 0–80 DKK | Pæn status-bar på hylden |

**Projekt 1 subtotal (ekskl. Pi):** ~**110–260 DKK**

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
| S2 | **Load cell 1 kg** (eller 5 kg) | 1 | 25–50 DKK | 25–50 DKK | 1 kg nok til spole; 5 kg hvis stor spole |
| S3 | **0,96" OLED SSD1306** I2C | 1 | 20–35 DKK | 20–35 DKK | Valgfri — viser gram tilbage |
| S4 | **3D-printet spool-base** | 1 | — | ~10 DKK | Filament — spole kun på cellen |
| S5 | **M3 skruer + afstandskiver** | 1 sæt | 15–25 DKK | 15–25 DKK | Montering cell + Pi-hus |
| S6 | **Kalibreringsvægt** 200 g | 1 | 0–30 DKK | 0–30 DKK | Møntvægt eller kendt masse |

**Projekt 2 subtotal (ekskl. Pi):** ~**85–180 DKK**

### GPIO (reference)

| Modul | Pi Zero GPIO |
|-------|----------------|
| HX711 DT | GPIO5 |
| HX711 SCK | GPIO6 |
| OLED SDA | GPIO2 |
| OLED SCL | GPIO3 |

---

## Samlet indkøbsliste — begge projekter

Kryds af når købt:

```
FÆLLES (×2 Pi)
[ ] Raspberry Pi Zero 2 W med header     ×2
[ ] microSD 8 GB (hvis mangler)        ×1  (du har 1 flashet)
[ ] micro-USB PSU 5V 2,5A              ×1–2

LED BAR
[ ] WS2812B strip ~0,5 m
[ ] 5V PSU til LED (2A+)
[ ] 330 Ω modstand
[ ] Jumper-ledninger

SPOOL TRACKER
[ ] HX711 modul
[ ] Load cell 1 kg
[ ] OLED SSD1306 0,96" (valgfri)
[ ] Print spool-base
```

---

## Allerede på lager (fra Dual Filament)

| Komponent | Brug |
|-----------|------|
| Pi Zero 2 W + 8 GB SD (flashet) | Andet projekt — **genbrug ikke** til feeder uden ny SD |
| `pi3feeder` på netværk | LED Bar læser Moonraker herfra — **ingen ekstra køb** |
| WiFi-scripts fra Dual-Filament-repo | Flash/konfig — gratis |

---

## Anbefalet rækkefølge

1. **LED Bar først** — færrest dele, hurtigst synligt resultat  
2. **Spool Tracker** — kræver print + kalibrering  
3. Køb **2× Pi Zero 2 W** hvis begge skal køre samtidigt  

---

## Undgå

| Produkt | Hvorfor |
|---------|---------|
| Raspberry Pi **Pico** | Ingen Linux — passer ikke til disse projekter |
| Pi Zero **W** (gammel, 1 kerne) | For svag; ny Pi OS understøtter den dårligt |
| SK6812 RGBW (medmindre du vil have hvid) | WS2812B er nok |
| Load cell uden HX711 | HX711-modulet inkluderer forstærker |

---

## Links (reference)

| Projekt | Repo |
|---------|------|
| LED Bar | [feeder_status_ledstatus_bar](https://github.com/ShadowMasterJedi/feeder_status_ledstatus_bar) |
| Spool Tracker | [Spool_weight_tracker](https://github.com/ShadowMasterJedi/Spool_weight_tracker) |
| Dual Filament | [Dual-Filament-System-P1S](https://github.com/ShadowMasterJedi/Dual-Filament-System-P1S) |

---

*Sidst opdateret: juni 2026*
