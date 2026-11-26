#!/usr/bin/env python3
"""Imágenes 1600x1000 para los servicios del catálogo de citasweb.es.

Uso: python3 generator/service.py salida.png sector "KICKER" "Título con *resaltado*" "Etiqueta de precio"
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).parent))
from render import THEMES, LOGO, esc  # noqa: E402

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
body{width:1600px;height:1000px;background:var(--bg);color:#fff;font-family:'Poppins','Inter',sans-serif;position:relative;overflow:hidden}
.grid{position:absolute;inset:0;background-image:linear-gradient(#ffffff08 1px,transparent 1px),linear-gradient(90deg,#ffffff08 1px,transparent 1px);background-size:80px 80px}
.glow{position:absolute;width:1100px;height:1100px;border-radius:50%;background:var(--ac);opacity:.16;filter:blur(140px);right:-350px;top:-420px}
.wrap{position:absolute;left:120px;right:120px;top:110px;bottom:200px;display:flex;flex-direction:column;justify-content:center}
.kicker{align-self:flex-start;background:var(--ac);color:var(--bg);font-weight:700;font-size:32px;letter-spacing:4px;padding:12px 28px;border-radius:999px;margin-bottom:44px}
h1{font-size:104px;line-height:1.04;font-weight:800;letter-spacing:-2.5px;max-width:1300px}
h1 em{font-style:normal;color:var(--ac)}
.foot{position:absolute;left:120px;right:120px;bottom:90px;display:flex;justify-content:space-between;align-items:center}
.brand{display:flex;align-items:center;gap:16px;font-size:38px;font-weight:700}.brand svg{color:var(--ac);width:58px;height:58px}
.price{border:5px solid var(--ac);color:var(--ac);font-weight:800;font-size:46px;padding:16px 38px;border-radius:26px}
"""


def main(out, sector, kicker, title, price):
    bg, ac = THEMES.get(sector, THEMES["general"])
    price_html = f'<div class="price">{esc(price)}</div>' if price else ""
    html = f"""<!doctype html><html><head><meta charset="utf-8"><style>:root{{--bg:{bg};--ac:{ac}}}{CSS}</style></head>
<body><div class="grid"></div><div class="glow"></div><div class="wrap"><div class="kicker">{esc(kicker)}</div>
<h1>{esc(title)}</h1></div><div class="foot"><div class="brand">{LOGO}<span>CitasWeb</span></div>{price_html}</div></body></html>"""
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        p = b.new_page(viewport={"width": 1600, "height": 1000})
        p.set_content(html, wait_until="networkidle")
        p.screenshot(path=out, type="jpeg", quality=90)
        b.close()


if __name__ == "__main__":
    main(*sys.argv[1:6])
