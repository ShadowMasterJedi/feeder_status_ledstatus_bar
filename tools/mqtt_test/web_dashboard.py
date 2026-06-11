#!/usr/bin/env python3
"""Web-dashboard — viser live MQTT filament-data."""
import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

import paho.mqtt.client as mqtt

BROKER = os.environ.get("MQTT_BROKER", "127.0.0.1")
MQTT_PORT = int(os.environ.get("MQTT_PORT", "1883"))
WEB_PORT = int(os.environ.get("WEB_PORT", "8765"))
PREFIX = os.environ.get("MQTT_PREFIX", "feedled")

state = {
    "boxes": {
        "box1": {"label": "Spool A", "temperature_c": None, "humidity_pct": None, "remaining_g": None},
        "box2": {"label": "Spool B", "temperature_c": None, "humidity_pct": None, "remaining_g": None},
    },
    "updated": None,
    "connected": False,
}
lock = threading.Lock()


def on_connect(client, _userdata, _flags, reason_code, _props):
    with lock:
        state["connected"] = reason_code == 0
    if reason_code == 0:
        client.subscribe(f"{PREFIX}/#")


def on_message(_client, _userdata, msg):
    topic = msg.topic
    if not topic.startswith(f"{PREFIX}/"):
        return
    parts = topic.split("/")
    if len(parts) < 3:
        return
    box_id, field = parts[1], parts[2]
    try:
        text = msg.payload.decode("utf-8")
    except UnicodeDecodeError:
        return

    with lock:
        if box_id not in state["boxes"]:
            state["boxes"][box_id] = {
                "label": box_id,
                "temperature_c": None,
                "humidity_pct": None,
                "remaining_g": None,
            }
        box = state["boxes"][box_id]

        if field == "state":
            try:
                data = json.loads(text)
                box.update(data)
            except json.JSONDecodeError:
                pass
        elif field == "temperature":
            box["temperature_c"] = float(text)
        elif field == "humidity":
            box["humidity_pct"] = float(text)
        elif field == "remaining":
            box["remaining_g"] = float(text)

        state["updated"] = time.time()


def mqtt_thread():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="filament-web")
    client.on_connect = on_connect
    client.on_message = on_message
    while True:
        try:
            client.connect(BROKER, MQTT_PORT, 60)
            client.loop_forever()
        except Exception:
            with lock:
                state["connected"] = False
            time.sleep(3)


HTML = """<!DOCTYPE html>
<html lang="da">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>feedled — Filament Monitor</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=JetBrains+Mono:wght@500;600&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #080b10;
      --surface: rgba(18, 24, 36, 0.72);
      --border: rgba(255,255,255,0.08);
      --text: #eef2f8;
      --muted: #8b9cb3;
      --a: #ff7b54;
      --a-glow: rgba(255, 123, 84, 0.35);
      --b: #4cc9f0;
      --b-glow: rgba(76, 201, 240, 0.35);
      --ok: #52b788;
      --warn: #f4a261;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: "DM Sans", system-ui, sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      overflow-x: hidden;
    }
    .bg {
      position: fixed; inset: 0; z-index: 0; pointer-events: none;
      background:
        radial-gradient(ellipse 80% 50% at 20% -10%, rgba(255,123,84,0.18), transparent),
        radial-gradient(ellipse 70% 45% at 90% 10%, rgba(76,201,240,0.14), transparent),
        radial-gradient(ellipse 60% 40% at 50% 100%, rgba(82,183,136,0.08), transparent),
        var(--bg);
    }
    .grid-bg {
      position: fixed; inset: 0; z-index: 0; opacity: 0.35; pointer-events: none;
      background-image:
        linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
      background-size: 48px 48px;
      mask-image: radial-gradient(ellipse 80% 70% at 50% 40%, black, transparent);
    }
    .wrap { position: relative; z-index: 1; max-width: 1100px; margin: 0 auto; padding: 2rem 1.25rem 3rem; }
    header {
      display: flex; flex-wrap: wrap; align-items: flex-end; justify-content: space-between;
      gap: 1rem; margin-bottom: 2rem;
    }
    .brand h1 {
      font-size: clamp(1.6rem, 4vw, 2.2rem); font-weight: 700; letter-spacing: -0.03em;
      background: linear-gradient(135deg, #fff 0%, #a8c7fa 100%);
      -webkit-background-clip: text; -webkit-text-fill-color: transparent;
      background-clip: text;
    }
    .brand p { color: var(--muted); font-size: 0.95rem; margin-top: 0.35rem; }
    .brand code {
      font-family: "JetBrains Mono", monospace; font-size: 0.82rem;
      background: rgba(255,255,255,0.06); padding: 0.15rem 0.45rem; border-radius: 6px;
    }
    .pill {
      display: inline-flex; align-items: center; gap: 0.5rem;
      padding: 0.45rem 0.9rem; border-radius: 999px; font-size: 0.82rem; font-weight: 500;
      border: 1px solid var(--border); backdrop-filter: blur(12px);
      background: var(--surface);
    }
    .pill .dot {
      width: 8px; height: 8px; border-radius: 50%; background: #e76f51;
      box-shadow: 0 0 0 0 rgba(231,111,81,0.5);
    }
    .pill.ok .dot {
      background: var(--ok);
      animation: pulse 2s infinite;
    }
    .pill.ok { border-color: rgba(82,183,136,0.35); color: #b7e4c7; }
    .pill.bad { border-color: rgba(231,111,81,0.35); color: #f8ad9d; }
    @keyframes pulse {
      0%, 100% { box-shadow: 0 0 0 0 rgba(82,183,136,0.5); }
      50% { box-shadow: 0 0 0 8px rgba(82,183,136,0); }
    }
    .cards {
      display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 1.25rem;
    }
    .card {
      position: relative; border-radius: 20px; padding: 1.5rem;
      background: var(--surface); border: 1px solid var(--border);
      backdrop-filter: blur(20px);
      box-shadow: 0 20px 50px rgba(0,0,0,0.35);
      overflow: hidden;
      transition: transform 0.25s ease, box-shadow 0.25s ease;
    }
    .card:hover { transform: translateY(-3px); box-shadow: 0 28px 60px rgba(0,0,0,0.45); }
    .card::before {
      content: ""; position: absolute; top: 0; left: 0; right: 0; height: 3px;
      background: var(--accent);
    }
    .card.a { --accent: linear-gradient(90deg, #ff7b54, #ffb347); }
    .card.b { --accent: linear-gradient(90deg, #4cc9f0, #7b9fff); }
    .card-head {
      display: flex; align-items: center; justify-content: space-between;
      margin-bottom: 1.25rem;
    }
    .card-head h2 { font-size: 1.15rem; font-weight: 600; }
    .badge {
      font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.08em;
      padding: 0.25rem 0.55rem; border-radius: 6px; font-weight: 600;
      background: rgba(255,255,255,0.06); color: var(--muted);
    }
    .card.a .badge { color: #ffb347; background: rgba(255,123,84,0.12); }
    .card.b .badge { color: #7bdcf7; background: rgba(76,201,240,0.12); }
    .hero {
      display: flex; align-items: center; gap: 1.25rem; margin-bottom: 1.5rem;
      padding-bottom: 1.25rem; border-bottom: 1px solid var(--border);
    }
    .ring-wrap { position: relative; width: 110px; height: 110px; flex-shrink: 0; }
    .ring-wrap svg { transform: rotate(-90deg); width: 100%; height: 100%; }
    .ring-bg { fill: none; stroke: rgba(255,255,255,0.06); stroke-width: 8; }
    .ring-fg {
      fill: none; stroke-width: 8; stroke-linecap: round;
      transition: stroke-dashoffset 0.8s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .card.a .ring-fg { stroke: url(#gradA); filter: drop-shadow(0 0 6px var(--a-glow)); }
    .card.b .ring-fg { stroke: url(#gradB); filter: drop-shadow(0 0 6px var(--b-glow)); }
    .ring-center {
      position: absolute; inset: 0; display: flex; flex-direction: column;
      align-items: center; justify-content: center; text-align: center;
    }
    .ring-center .grams {
      font-family: "JetBrains Mono", monospace; font-size: 1.35rem; font-weight: 600; line-height: 1;
    }
    .ring-center .sub { font-size: 0.72rem; color: var(--muted); margin-top: 0.2rem; }
    .hero-text .label { font-size: 0.75rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.06em; }
    .hero-text .pct {
      font-family: "JetBrains Mono", monospace; font-size: 2rem; font-weight: 600;
      margin-top: 0.15rem;
    }
    .hero-text .hint { font-size: 0.85rem; color: var(--muted); margin-top: 0.25rem; }
    .metrics { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; }
    .metric {
      background: rgba(255,255,255,0.03); border: 1px solid var(--border);
      border-radius: 14px; padding: 0.9rem 1rem;
      display: flex; align-items: flex-start; gap: 0.65rem;
    }
    .metric .icon {
      width: 36px; height: 36px; border-radius: 10px; flex-shrink: 0;
      display: flex; align-items: center; justify-content: center;
    }
    .card.a .metric .icon { background: rgba(255,123,84,0.12); color: #ffb347; }
    .card.b .metric .icon { background: rgba(76,201,240,0.12); color: #7bdcf7; }
    .metric .lbl { font-size: 0.72rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.05em; }
    .metric .num {
      font-family: "JetBrains Mono", monospace; font-size: 1.35rem; font-weight: 600;
      margin-top: 0.15rem;
    }
    .metric .unit { font-size: 0.8rem; color: var(--muted); font-weight: 400; }
    footer {
      margin-top: 2rem; text-align: center; font-size: 0.8rem; color: var(--muted);
    }
    .waiting {
      grid-column: 1 / -1; text-align: center; padding: 4rem 2rem;
      color: var(--muted); font-size: 1.05rem;
    }
    .waiting .spin {
      width: 40px; height: 40px; border: 3px solid rgba(255,255,255,0.08);
      border-top-color: #4cc9f0; border-radius: 50%;
      animation: spin 0.9s linear infinite; margin: 0 auto 1rem;
    }
    @keyframes spin { to { transform: rotate(360deg); } }
    @media (max-width: 480px) {
      .hero { flex-direction: column; text-align: center; }
      .metrics { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="bg"></div>
  <div class="grid-bg"></div>
  <div class="wrap">
    <header>
      <div class="brand">
        <h1>feedled</h1>
        <p>Filament monitor · live MQTT fra <code id="prefix">feedled</code></p>
      </div>
      <div id="conn" class="pill bad"><span class="dot"></span><span id="conn-txt">Forbinder…</span></div>
    </header>
    <div class="cards" id="grid">
      <div class="waiting"><div class="spin"></div>Venter på MQTT-data…</div>
    </div>
    <footer>Senest opdateret <span id="ts">—</span> · opdateres hvert 2 sek</footer>
  </div>
  <svg width="0" height="0" aria-hidden="true">
    <defs>
      <linearGradient id="gradA" x1="0%" y1="0%" x2="100%" y2="0%">
        <stop offset="0%" stop-color="#ff7b54"/><stop offset="100%" stop-color="#ffb347"/>
      </linearGradient>
      <linearGradient id="gradB" x1="0%" y1="0%" x2="100%" y2="0%">
        <stop offset="0%" stop-color="#4cc9f0"/><stop offset="100%" stop-color="#7b9fff"/>
      </linearGradient>
    </defs>
  </svg>
  <script>
    const MAX_G = 1000;
    const R = 46, C = 2 * Math.PI * R;

    const icons = {
      temp: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z"/></svg>',
      hum: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"/></svg>',
    };

    function fmt(v, dec=1) {
      return v == null ? '—' : Number(v).toFixed(dec);
    }

    function levelHint(pct) {
      if (pct == null) return 'Afventer data';
      if (pct > 60) return 'God mængde tilbage';
      if (pct > 25) return 'Overvej at bestille';
      return 'Lav — skift snart';
    }

    function ring(pct) {
      const p = Math.max(0, Math.min(100, pct || 0));
      const off = C * (1 - p / 100);
      return `<div class="ring-wrap">
        <svg viewBox="0 0 100 100"><circle class="ring-bg" cx="50" cy="50" r="${R}"/>
        <circle class="ring-fg" cx="50" cy="50" r="${R}" stroke-dasharray="${C}" stroke-dashoffset="${off}"/></svg>
        <div class="ring-center"><span class="grams" data-val></span><span class="sub">gram</span></div>
      </div>`;
    }

    function cardHtml(id, b) {
      const theme = id === 'box1' ? 'a' : 'b';
      const rem = b.remaining_g;
      const pct = rem == null ? null : Math.min(100, rem / MAX_G * 100);
      const badge = id === 'box1' ? 'Aktiv' : 'Standby';
      return `<article class="card ${theme}">
        <div class="card-head"><h2>${b.label || id}</h2><span class="badge">${badge}</span></div>
        <div class="hero">
          ${ring(pct)}
          <div class="hero-text">
            <div class="label">Resterende</div>
            <div class="pct" data-pct>${pct == null ? '—' : Math.round(pct) + '%'}</div>
            <div class="hint">${levelHint(pct)}</div>
          </div>
        </div>
        <div class="metrics">
          <div class="metric">
            <div class="icon">${icons.temp}</div>
            <div><div class="lbl">Temperatur</div><div class="num" data-temp>${fmt(b.temperature_c)}<span class="unit"> °C</span></div></div>
          </div>
          <div class="metric">
            <div class="icon">${icons.hum}</div>
            <div><div class="lbl">Luftfugtighed</div><div class="num" data-hum>${fmt(b.humidity_pct)}<span class="unit"> %</span></div></div>
          </div>
        </div>
      </article>`;
    }

    function render(data) {
      document.getElementById('prefix').textContent = data.prefix || 'feedled';
      const conn = document.getElementById('conn');
      const ok = data.connected;
      conn.className = 'pill ' + (ok ? 'ok' : 'bad');
      document.getElementById('conn-txt').textContent = ok ? 'MQTT live' : 'MQTT offline';
      document.getElementById('ts').textContent = data.updated
        ? new Date(data.updated * 1000).toLocaleTimeString('da-DK')
        : '—';

      const boxes = data.boxes || {};
      const order = ['box1', 'box2'];
      const ids = [...order.filter(k => k in boxes), ...Object.keys(boxes).filter(k => !order.includes(k))];
      const grid = document.getElementById('grid');

      if (!ids.length) {
        grid.innerHTML = '<div class="waiting"><div class="spin"></div>Venter på MQTT-data…</div>';
        return;
      }

      if (grid.children.length !== ids.length || [...grid.children].some((el, i) => !el.classList.contains('card'))) {
        grid.innerHTML = ids.map(id => cardHtml(id, boxes[id])).join('');
      }

      ids.forEach((id, i) => {
        const b = boxes[id];
        const el = grid.children[i];
        const rem = b.remaining_g;
        const pct = rem == null ? null : Math.min(100, rem / MAX_G * 100);
        const gEl = el.querySelector('[data-val]');
        const pEl = el.querySelector('[data-pct]');
        const tEl = el.querySelector('[data-temp]');
        const hEl = el.querySelector('[data-hum]');
        if (gEl) gEl.textContent = rem == null ? '—' : Math.round(rem);
        if (pEl) pEl.textContent = pct == null ? '—' : Math.round(pct) + '%';
        if (tEl) tEl.innerHTML = fmt(b.temperature_c) + '<span class="unit"> °C</span>';
        if (hEl) hEl.innerHTML = fmt(b.humidity_pct) + '<span class="unit"> %</span>';
        const ringFg = el.querySelector('.ring-fg');
        if (ringFg && pct != null) ringFg.style.strokeDashoffset = C * (1 - pct / 100);
        const hint = el.querySelector('.hint');
        if (hint) hint.textContent = levelHint(pct);
      });
    }

    async function poll() {
      try {
        const r = await fetch('/api/status');
        render(await r.json());
      } catch (e) { console.error(e); }
    }
    poll();
    setInterval(poll, 2000);
  </script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, _fmt, *_args):
        pass

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/status":
            with lock:
                payload = {
                    "prefix": PREFIX,
                    "connected": state["connected"],
                    "updated": state["updated"],
                    "boxes": state["boxes"],
                }
            body = json.dumps(payload).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(body)
            return
        if path in ("/", "/index.html"):
            body = HTML.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_response(404)
        self.end_headers()


def main():
    threading.Thread(target=mqtt_thread, daemon=True).start()
    host = os.environ.get("WEB_BIND", "0.0.0.0")
    server = HTTPServer((host, WEB_PORT), Handler)
    print(f"Dashboard:  http://127.0.0.1:{WEB_PORT}/")
    try:
        import socket
        lan = socket.gethostbyname(socket.gethostname())
        if lan and not lan.startswith("127."):
            print(f"            http://{lan}:{WEB_PORT}/")
    except OSError:
        pass
    print(f"MQTT:       mqtt://{BROKER}:{MQTT_PORT}  prefix={PREFIX}/")
    server.serve_forever()


if __name__ == "__main__":
    main()
