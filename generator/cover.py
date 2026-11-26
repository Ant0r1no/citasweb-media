#!/usr/bin/env python3
"""Portadas 1200x630 para el blog (y para compartir enlaces).

Uso: python3 generator/cover.py salida.png sector "Kicker" "Título con *resaltado*"
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).parent))
from render import THEMES, LOGO, esc  # noqa: E402

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
body{width:1200px;height:630px;background:var(--bg);color:#fff;font-family:'Poppins','Inter',sans-serif;
 position:relative;overflow:hidden}
.glow{position:absolute;width:800px;height:800px;border-radius:50%;background:var(--ac);opacity:.14;
 filter:blur(110px);right:-260px;top:-300px}
.grid{position:absolute;inset:0;background-image:linear-gradient(#ffffff08 1px,transparent 1px),
 linear-gradient(90deg,#ffffff08 1px,transparent 1px);background-size:60px 60px}
.wrap{position:absolute;left:80px;right:80px;top:70px;bottom:110px;display:flex;flex-direction:column;justify-content:center}
.kicker{align-self:flex-start;background:var(--ac);color:var(--bg);font-weight:700;font-size:24px;
 letter-spacing:3px;padding:8px 20px;border-radius:999px;margin-bottom:30px}
h1{font-size:64px;line-height:1.08;font-weight:800;letter-spacing:-1.5px;max-width:1000px}
h1 em{font-style:normal;color:var(--ac)}
.foot{position:absolute;left:80px;right:80px;bottom:50px;display:flex;justify-content:space-between;
 align-items:center;font-size:26px;font-weight:600;color:#ffffffb3}
.brand{display:flex;align-items:center;gap:12px;color:#fff}.brand svg{color:var(--ac)}
"""


def main(out, sector, kicker, title):
    bg, ac = THEMES.get(sector, THEMES["general"])
    html = f"""<!doctype html><html><head><meta charset="utf-8"><style>:root{{--bg:{bg};--ac:{ac}}}{CSS}</style></head>
<body><div class="grid"></div><div class="glow"></div><div class="wrap"><div class="kicker">{esc(kicker)}</div>
<h1>{esc(title)}</h1></div><div class="foot"><div class="brand">{LOGO}<span>CitasWeb</span></div>
<span>citasweb.es/blog</span></div></body></html>"""
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        p = b.new_page(viewport={"width": 1200, "height": 630})
        p.set_content(html, wait_until="networkidle")
        p.screenshot(path=out)
        b.close()


if __name__ == "__main__":
    main(*sys.argv[1:5])
