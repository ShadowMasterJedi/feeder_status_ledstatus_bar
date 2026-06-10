#include <Arduino.h>
#include <ArduinoJson.h>
#include <HTTPClient.h>
#include <WebServer.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <time.h>

#include "wifi_secrets.h"

#ifndef WEATHER_LAT
#define WEATHER_LAT 55.6761
#endif
#ifndef WEATHER_LON
#define WEATHER_LON 12.5683
#endif
#ifndef WEATHER_PLACE
#define WEATHER_PLACE "København"
#endif

constexpr uint8_t LED_PIN = 2;
constexpr uint32_t WEATHER_POLL_MS = 30UL * 60UL * 1000UL;
constexpr uint8_t FORECAST_DAYS = 5;

WebServer server(80);

struct DayForecast {
    char date[11];
    char weekday[12];
    char desc[28];
    float tempMax;
    float tempMin;
    int weatherCode;
    bool valid;
};

DayForecast forecast[FORECAST_DAYS];
bool ntpSynced = false;
bool weatherOk = false;
uint32_t lastWeatherPoll = 0;
String weatherError;

const char *WEEKDAYS[] = {"søndag", "mandag", "tirsdag", "onsdag",
                          "torsdag", "fredag", "lørdag"};

const char *weatherDesc(int code) {
    if (code == 0) return "Klart";
    if (code <= 3) return "Delvist skyet";
    if (code <= 48) return "Tåge";
    if (code <= 55) return "Let regn";
    if (code <= 65) return "Regn";
    if (code <= 75) return "Sne";
    if (code <= 82) return "Byger";
    if (code <= 86) return "Snebyger";
    if (code >= 95) return "Torden";
    return "Ukendt";
}

void ledConnecting() {
    static uint32_t last = 0;
    if (millis() - last > 300) {
        last = millis();
        digitalWrite(LED_PIN, !digitalRead(LED_PIN));
    }
}

void ledOk() { digitalWrite(LED_PIN, HIGH); }

void ledWarn() {
    static uint32_t last = 0;
    if (millis() - last > 1000) {
        last = millis();
        digitalWrite(LED_PIN, !digitalRead(LED_PIN));
    }
}

void weekdayFromDate(const char *iso, char *out, size_t outLen) {
    int y, m, d;
    if (sscanf(iso, "%d-%d-%d", &y, &m, &d) != 3) {
        snprintf(out, outLen, "—");
        return;
    }
    struct tm t = {};
    t.tm_year = y - 1900;
    t.tm_mon = m - 1;
    t.tm_mday = d;
    mktime(&t);
    snprintf(out, outLen, "%s", WEEKDAYS[t.tm_wday]);
}

bool syncNtp() {
    configTime(0, 0, "0.dk.pool.ntp.org", "1.dk.pool.ntp.org", "pool.ntp.org");
    setenv("TZ", "CET-1CEST,M3.5.0,M10.5.0/3", 1);
    tzset();

    struct tm timeinfo;
    for (uint8_t i = 0; i < 20; i++) {
        if (getLocalTime(&timeinfo)) {
            ntpSynced = true;
            Serial.println("NTP synkroniseret (DK atomur)");
            return true;
        }
        delay(500);
    }
    ntpSynced = false;
    Serial.println("NTP fejlede");
    return false;
}

bool fetchWeather() {
    WiFiClientSecure client;
    client.setInsecure();
    HTTPClient http;
    String url = "https://api.open-meteo.com/v1/forecast?latitude=";
    url += String(WEATHER_LAT, 4);
    url += "&longitude=";
    url += String(WEATHER_LON, 4);
    url += "&daily=weather_code,temperature_2m_max,temperature_2m_min";
    url += "&timezone=Europe%2FCopenhagen&forecast_days=5";

    http.setTimeout(10000);
    http.begin(client, url);
    int code = http.GET();
    if (code != 200) {
        weatherError = "HTTP " + String(code);
        http.end();
        weatherOk = false;
        return false;
    }

    String body = http.getString();
    http.end();

    JsonDocument doc;
    if (deserializeJson(doc, body)) {
        weatherError = "JSON fejl";
        weatherOk = false;
        return false;
    }

    JsonObject daily = doc["daily"];
    if (daily.isNull()) {
        weatherError = "Manglende data";
        weatherOk = false;
        return false;
    }

    for (uint8_t i = 0; i < FORECAST_DAYS; i++) {
        const char *date = daily["time"][i] | "";
        forecast[i].tempMax = daily["temperature_2m_max"][i] | 0.0f;
        forecast[i].tempMin = daily["temperature_2m_min"][i] | 0.0f;
        forecast[i].weatherCode = daily["weather_code"][i] | -1;
        strncpy(forecast[i].date, date, sizeof(forecast[i].date) - 1);
        weekdayFromDate(date, forecast[i].weekday, sizeof(forecast[i].weekday));
        strncpy(forecast[i].desc, weatherDesc(forecast[i].weatherCode),
                sizeof(forecast[i].desc) - 1);
        forecast[i].valid = date[0] != '\0';
    }

    weatherOk = true;
    weatherError = "";
    Serial.println("Vejr opdateret (5 dage)");
    return true;
}

String formatNow() {
    struct tm timeinfo;
    if (!getLocalTime(&timeinfo)) {
        return "Synkroniserer...";
    }
    char buf[9];
    strftime(buf, sizeof(buf), "%H:%M:%S", &timeinfo);
    return String(buf);
}

String formatDate() {
    struct tm timeinfo;
    if (!getLocalTime(&timeinfo)) {
        return "";
    }
    char buf[48];
    snprintf(buf, sizeof(buf), "%s %d. %s %d", WEEKDAYS[timeinfo.tm_wday],
             timeinfo.tm_mday,
             (const char *[]){"jan", "feb", "mar", "apr", "maj", "jun",
                              "jul", "aug", "sep", "okt", "nov", "dec"}[timeinfo.tm_mon],
             timeinfo.tm_year + 1900);
    return String(buf);
}

void handleRoot() {
    String clock = formatNow();
    String date = formatDate();

    String html = R"rawliteral(
<!DOCTYPE html>
<html lang="da"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="refresh" content="30">
<title>feedled — tid & vejr</title>
<style>
  *{box-sizing:border-box}
  body{font-family:system-ui,sans-serif;background:linear-gradient(160deg,#0a1628,#1a2a4a);color:#e8f0ff;margin:0;min-height:100vh;padding:1.2rem}
  .wrap{max-width:520px;margin:0 auto}
  h1{font-size:1.1rem;font-weight:500;color:#7eb8ff;margin:0 0 .2rem}
  .clock{font-size:3.2rem;font-weight:700;letter-spacing:.04em;margin:.2rem 0}
  .date{color:#9ab;font-size:1rem;margin-bottom:1.2rem}
  .badge{display:inline-block;background:#1e3a5f;padding:.25rem .6rem;border-radius:1rem;font-size:.75rem;color:#8cf;margin-bottom:1.5rem}
  .grid{display:grid;gap:.6rem}
  .day{background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1);border-radius:.8rem;padding:.8rem 1rem;display:flex;justify-content:space-between;align-items:center}
  .day .left .w{font-weight:600;text-transform:capitalize}
  .day .left .d{font-size:.8rem;color:#9ab}
  .day .right{text-align:right}
  .day .temp{font-size:1.3rem;font-weight:700}
  .day .desc{font-size:.8rem;color:#9cf}
  .foot{margin-top:1.5rem;font-size:.75rem;color:#678}
  .err{color:#f88}
</style>
</head><body><div class="wrap">
<h1>🇩🇰 feedled ESP32</h1>
)rawliteral";

    html += "<div class='clock'>" + clock + "</div>";
    html += "<div class='date'>" + date + "</div>";
    html += "<div class='badge'>";
    html += ntpSynced ? "Atomur · NTP synkroniseret" : "Venter på NTP...";
    html += " · " + String(WEATHER_PLACE) + "</div>";

    html += "<div class='grid'>";
    if (weatherOk) {
        for (uint8_t i = 0; i < FORECAST_DAYS; i++) {
            if (!forecast[i].valid) continue;
            html += "<div class='day'><div class='left'>";
            html += "<div class='w'>" + String(forecast[i].weekday) + "</div>";
            html += "<div class='d'>" + String(forecast[i].date) + "</div>";
            html += "</div><div class='right'>";
            html += "<div class='temp'>" + String((int)round(forecast[i].tempMax)) + "° / ";
            html += String((int)round(forecast[i].tempMin)) + "°</div>";
            html += "<div class='desc'>" + String(forecast[i].desc) + "</div>";
            html += "</div></div>";
        }
    } else {
        html += "<div class='day err'>Vejr ikke tilgængeligt";
        if (!weatherError.isEmpty()) html += " (" + weatherError + ")";
        html += "</div>";
    }
    html += "</div>";

    html += "<div class='foot'>";
    html += WiFi.localIP().toString() + " · opdateres hvert 30 sek";
    html += "</div></div></body></html>";

    server.send(200, "text/html", html);
}

void connectWiFi() {
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

    Serial.printf("Forbinder til %s", WIFI_SSID);
    for (uint8_t i = 0; i < 40 && WiFi.status() != WL_CONNECTED; i++) {
        ledConnecting();
        delay(500);
        Serial.print(".");
    }
    Serial.println();

    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("WiFi OK — IP: " + WiFi.localIP().toString());
    } else {
        Serial.println("WiFi fejlede");
    }
}

void setup() {
    Serial.begin(115200);
    pinMode(LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, LOW);

    for (uint8_t i = 0; i < FORECAST_DAYS; i++) {
        forecast[i].valid = false;
    }

    delay(500);
    Serial.println("\n=== feedled ESP32 — tid & vejr ===");

    connectWiFi();
    syncNtp();
    fetchWeather();
    lastWeatherPoll = millis();

    server.on("/", handleRoot);
    server.begin();
    Serial.println("Dashboard: http://" + WiFi.localIP().toString());
}

void loop() {
    server.handleClient();

    if (WiFi.status() != WL_CONNECTED) {
        connectWiFi();
        syncNtp();
    }

    if (millis() - lastWeatherPoll > WEATHER_POLL_MS) {
        lastWeatherPoll = millis();
        fetchWeather();
    }

    if (ntpSynced && weatherOk) {
        ledOk();
    } else {
        ledWarn();
    }
}
