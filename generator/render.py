#!/usr/bin/env python3
"""Genera carruseles 1080x1350 para Instagram/TikTok a partir de un JSON.

Uso:  python3 generator/render.py posts/2027-02-01-plantones/post.json
Crea slide-1.png, slide-2.png... en la misma carpeta que el JSON.

Formato del JSON:
{
  "sector": "barberia",            # elige colores (ver THEMES)
  "slides": [
    {"type": "cover", "kicker": "BARBEROS", "title": "Texto grande", "sub": "opcional"},
    {"type": "item",  "n": 1, "title": "Titular", "body": "Texto corto"},
    {"type": "stat",  "big": "240 €", "title": "al mes", "body": "explicación"},
    {"type": "chat",  "time": "23:47", "msg": "¿Tienes hueco mañana?", "title": "opcional"},
    {"type": "cta",   "title": "¿Y si reservaran solos?", "body": "citasweb.es", "word": "BARBER"}
  ]
}
"""
import json
import sys
import html
from pathlib import Path
from playwright.sync_api import sync_playwright

THEMES = {
    "general":     ("#0B1B3F", "#3DDC97"),
    "barberia":    ("#111111", "#E8B04B"),
    "peluqueria":  ("#2A1438", "#F28DB2"),
    "estetica":    ("#3A1F2B", "#F6B8C8"),
    "restaurante": ("#2B1A10", "#F2994A"),
    "taller":      ("#0F1A24", "#F2C94C"),
    "fisio":       ("#0D2B2B", "#56CCF2"),
    "dental":      ("#0A2540", "#7FDBFF"),
    "limpieza":    ("#0B2E3A", "#6FE3C1"),
    "vet":         ("#1D2B12", "#9BE15D"),
    "fitness":     ("#1A1A1A", "#FF5A5F"),
}

LOGO = ('<svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" '
        'height="17" rx="3"/><path d="M8 2v4M16 2v4M3 10h18"/><path d="m9 15 2 2 4-4"/></svg>')

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
body{width:1080px;height:1350px;background:var(--bg);color:#fff;font-family:'Poppins','Inter',sans-serif;
 position:relative;overflow:hidden}
.glow{position:absolute;width:900px;height:900px;border-radius:50%;background:var(--ac);opacity:.10;
 filter:blur(120px);right:-300px;top:-300px}
.wrap{position:absolute;inset:90px 90px 150px 90px;display:flex;flex-direction:column;justify-content:center}
.kicker{display:inline-block;align-self:flex-start;background:var(--ac);color:var(--bg);font-weight:700;
 font-size:30px;letter-spacing:3px;padding:10px 24px;border-radius:999px;margin-bottom:40px}
h1{font-size:96px;line-height:1.05;font-weight:800;letter-spacing:-2px}
h1 em,h2 em{font-style:normal;color:var(--ac)}
h2{font-size:72px;line-height:1.1;font-weight:800;letter-spacing:-1px}
.sub{font-size:40px;line-height:1.35;margin-top:40px;color:#ffffffcc;font-weight:500}
.num{font-size:200px;font-weight:800;color:var(--ac);line-height:1;margin-bottom:20px}
.big{font-size:230px;font-weight:800;color:var(--ac);line-height:1;letter-spacing:-6px}
.body{font-size:42px;line-height:1.4;margin-top:36px;color:#ffffffd9;font-weight:500}
.bubble{background:#fff;color:#111;border-radius:40px 40px 40px 8px;padding:44px 52px;font-size:56px;
 font-weight:600;line-height:1.25;max-width:820px;box-shadow:0 20px 60px #0006}
.time{font-size:34px;color:#ffffff99;margin:24px 0 0 8px;font-weight:500}
.word{margin-top:50px;display:inline-block;align-self:flex-start;border:4px solid var(--ac);color:var(--ac);
 font-weight:800;font-size:46px;padding:18px 36px;border-radius:24px}
.foot{position:absolute;left:90px;right:90px;bottom:60px;display:flex;justify-content:space-between;
 align-items:center;font-size:32px;font-weight:600;color:#ffffffb3}
.brand{display:flex;align-items:center;gap:14px;color:#fff}
.brand svg{color:var(--ac)}
.dots{display:flex;gap:12px}.dots i{width:14px;height:14px;border-radius:50%;background:#ffffff40}
.dots i.on{background:var(--ac);width:40px;border-radius:7px}
.swipe{color:var(--ac)}
"""


def esc(s):
    """Escapa HTML pero permite *texto* para resaltarlo con el color de acento."""
    s = html.escape(s or "")
    parts = s.split("*")
    return "".join(f"<em>{p}</em>" if i % 2 else p for i, p in enumerate(parts))


def slide_html(s):
    t = s["type"]
    if t == "cover":
        k = f'<div class="kicker">{esc(s.get("kicker"))}</div>' if s.get("kicker") else ""
        sub = f'<div class="sub">{esc(s.get("sub"))}</div>' if s.get("sub") else ""
        return f'{k}<h1>{esc(s["title"])}</h1>{sub}'
    if t == "item":
        body = f'<div class="body">{esc(s.get("body"))}</div>' if s.get("body") else ""
        return f'<div class="num">{s.get("n", "")}</div><h2>{esc(s["title"])}</h2>{body}'
    if t == "stat":
        body = f'<div class="body">{esc(s.get("body"))}</div>' if s.get("body") else ""
        return f'<div class="big">{esc(s["big"])}</div><h2>{esc(s.get("title"))}</h2>{body}'
    if t == "chat":
        title = f'<h2 style="margin-bottom:60px">{esc(s.get("title"))}</h2>' if s.get("title") else ""
        return (f'{title}<div class="bubble">{esc(s["msg"])}</div>'
                f'<div class="time">{esc(s.get("time", ""))}</div>')
    if t == "cta":
        body = f'<div class="sub">{esc(s.get("body"))}</div>' if s.get("body") else ""
        word = f'<div class="word">Comenta “{esc(s["word"])}”</div>' if s.get("word") else ""
        return f'<h1>{esc(s["title"])}</h1>{body}{word}'
    raise ValueError(f"tipo de slide desconocido: {t}")


def page(s, i, total, theme, vertical=False):
    bg, ac = theme
    extra = VERT_CSS if vertical else ""
    dots = "".join(f'<i class="{"on" if j == i else ""}"></i>' for j in range(total))
    right = '<span class="swipe">Desliza →</span>' if i < total - 1 else '<span>citasweb.es</span>'
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>:root{{--bg:{bg};--ac:{ac}}}{CSS}{extra}</style>
</head><body><div class="glow"></div><div class="wrap">{slide_html(s)}</div>
<div class="foot"><div class="brand">{LOGO}<span>CitasWeb</span></div><div class="dots">{dots}</div>{right}</div>
</body></html>"""


VERT_CSS = """
body{height:1920px}
.wrap{inset:260px 90px 340px 90px}
.foot{bottom:200px}
h1{font-size:110px}h2{font-size:84px}.body,.sub{font-size:48px}
"""


def render(json_path):
    p = Path(json_path)
    data = json.loads(p.read_text(encoding="utf-8"))
    theme = THEMES.get(data.get("sector", "general"), THEMES["general"])
    slides = data["slides"]
    vertical = data.get("format") == "vertical"
    out = []
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1920 if vertical else 1350})
        for i, s in enumerate(slides):
            pg.set_content(page(s, i, len(slides), theme, vertical), wait_until="networkidle")
            f = p.parent / f"slide-{i + 1}.png"
            pg.screenshot(path=str(f))
            out.append(f)
        b.close()
    return out


if __name__ == "__main__":
    for j in sys.argv[1:]:
        for f in render(j):
            print(f)
