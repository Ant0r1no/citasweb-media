#!/usr/bin/env python3
"""Convierte un carrusel (posts/<carpeta>/post.json) en un mini vídeo vertical con música.

Uso: python3 generator/slideshow.py posts/<carpeta>/post.json [estilo_musica] [semilla]

Usa las mismas diapositivas que generator/render.py, pero en 1080x1920 y animadas:
entrada deslizada de cada diapositiva, textos que aparecen escalonados, números que
"saltan", barra de progreso tipo historias, música propia (generator/music.py) y efectos
(generator/sfx.py). Crea video.mp4 y cover.jpg en la misma carpeta.
"""
import json
import shutil
import subprocess
import sys
import wave
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
import music  # noqa: E402
import sfx  # noqa: E402
from render import CSS, LOGO, THEMES, slide_html  # noqa: E402

FPS = 30

EXTRA_CSS = """
body{width:1080px;height:1920px;background:var(--bg)}
.glow{filter:none;opacity:1;background:radial-gradient(circle,color-mix(in srgb,var(--ac) 22%,transparent),transparent 65%);
 width:1300px;height:1300px}
.grid{position:absolute;inset:0;background-image:linear-gradient(#ffffff0a 1px,transparent 1px),
 linear-gradient(90deg,#ffffff0a 1px,transparent 1px);background-size:72px 72px}
.slide{position:absolute;inset:0;opacity:0}
.slide .wrap{inset:300px 90px 360px 90px}
.slide .wrap>*{opacity:0}
h1{font-size:112px}h2{font-size:86px}.body,.sub{font-size:50px}
.num{font-size:240px}.big{font-size:250px}
.bubble{font-size:62px}
.bars{position:absolute;top:120px;left:90px;right:90px;display:flex;gap:12px}
.bars i{flex:1;height:10px;border-radius:5px;background:#ffffff30;overflow:hidden;position:relative}
.bars i b{position:absolute;left:0;top:0;bottom:0;width:0;background:var(--ac)}
.foot{bottom:190px}
.site{color:var(--ac)}
"""

JS = """
const D = __DURS__, BPM = __BPM__;
const starts = []; {let a = 0; for (const d of D) {starts.push(a); a += d;}}
const ease = x => 1 - Math.pow(1 - Math.min(Math.max(x, 0), 1), 3);
const back = x => {x = Math.min(Math.max(x, 0), 1); const c = 1.9; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2);};
const slides = [...document.querySelectorAll('.slide')], bars = [...document.querySelectorAll('.bars b')];
const glow = document.querySelector('.glow');
function render(t) {
  let i = 0; while (i + 1 < D.length && t >= starts[i + 1]) i++;
  slides.forEach((s, j) => {
    const lt = t - starts[j];
    let op = 0, x = 0;
    if (j === i) { op = j === 0 ? 1 : ease(lt / 0.35); x = j === 0 ? 0 : (1 - ease(lt / 0.35)) * 140; }
    if (j === i - 1) { const k = ease((t - starts[i]) / 0.35); op = 1 - k; x = -k * 140; }
    s.style.opacity = op; s.style.transform = `translateX(${x}px)`;
    if (j !== i && j !== i - 1) return;
    const kids = [...s.querySelectorAll('.wrap > *')];
    kids.forEach((el, n) => {
      const k = (lt - 0.15 - n * 0.16) / 0.45;
      const pop = el.classList.contains('num') || el.classList.contains('big') || el.classList.contains('bubble') || el.classList.contains('word');
      el.style.opacity = ease(k * 1.4);
      el.style.transform = pop ? `scale(${0.55 + 0.45 * back(k)})` : `translateY(${(1 - ease(k)) * 60}px)`;
      el.style.transformOrigin = 'left center';
    });
    const beat = 60 / BPM, ph = (t % beat) / beat, pulse = 1 + 0.035 * Math.exp(-ph * 6);
    s.querySelectorAll('.kicker,.word').forEach(el => { if (lt > 0.9) el.style.transform = `scale(${pulse})`; });
  });
  bars.forEach((b, j) => { b.style.width = (j < i ? 100 : j > i ? 0 : Math.min(100, (t - starts[i]) / D[i] * 100)) + '%'; });
  glow.style.transform = `translate(${Math.sin(t * 0.5) * 120}px, ${Math.cos(t * 0.4) * 160}px)`;
}
"""


def duration(s):
    text = " ".join(str(s.get(k, "")) for k in ("kicker", "title", "sub", "body", "msg", "big"))
    if s["type"] == "cta":
        return 3.6
    return round(min(4.6, max(2.6, 1.6 + 0.04 * len(text))), 2)


def build_html(slides, theme, durs, bpm):
    bg, ac = theme
    inner = "".join(f'<div class="slide"><div class="wrap">{slide_html(s)}</div></div>' for s in slides)
    bars = "".join("<i><b></b></i>" for _ in slides)
    js = JS.replace("__DURS__", json.dumps(durs)).replace("__BPM__", str(bpm))
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>:root{{--bg:{bg};--ac:{ac}}}{CSS}{EXTRA_CSS}</style>
</head><body><div class="grid"></div><div class="glow"></div>{inner}<div class="bars">{bars}</div>
<div class="foot"><div class="brand">{LOGO}<span>CitasWeb</span></div><span class="site">citasweb.es</span></div>
<script>{js}</script></body></html>"""


def make(json_path, style=None, seed=None):
    p = Path(json_path)
    data = json.loads(p.read_text(encoding="utf-8"))
    slides = data["slides"]
    theme = THEMES.get(data.get("sector", "general"), THEMES["general"])
    seed = int(seed or (sum(map(ord, p.parent.name)) % 97 + 1))
    style = style or ["pop", "house", "lofi"][seed % 3]
    bpm = music.STYLES[style]["bpm"]
    durs = [duration(s) for s in slides]
    total = round(sum(durs) + 0.4, 2)
    starts = [sum(durs[:i]) for i in range(len(durs))]
    events = []
    for i, s in enumerate(slides):
        if i:
            events.append((max(0, starts[i] - 0.1), "whoosh"))
        if s["type"] in ("item", "stat"):
            events.append((starts[i] + 0.2, "pop"))
        if s["type"] == "chat":
            events.append((starts[i] + 0.5, "ping"))
        if s["type"] == "cta":
            events.append((starts[i] + 0.7, "ding"))
    raw = p.parent / "frames"
    if raw.exists():
        shutil.rmtree(raw)
    raw.mkdir()
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1920})
        pg.set_content(build_html(slides, theme, durs, bpm), wait_until="networkidle")
        pg.evaluate(f"render({min(durs[0] - 0.1, 1.8)})")
        pg.screenshot(path=str(p.parent / "cover.jpg"), type="jpeg", quality=90)
        for f in range(int(total * FPS)):
            pg.evaluate(f"render({f / FPS:.4f})")
            pg.screenshot(path=str(raw / f"{f:05d}.jpg"), type="jpeg", quality=90)
        b.close()
    mwav, fxwav = p.parent / "music.wav", p.parent / "sfx.wav"
    for path, sr, arr in ((mwav, music.SR, music.make(total + 0.5, style, seed=seed)),
                          (fxwav, sfx.SR, sfx.make_track(total, events))):
        with wave.open(str(path), "wb") as w:
            w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes(arr.tobytes())
    out = p.parent / "video.mp4"
    fc = (f"[1:a]volume=0.85,afade=t=in:d=0.3,afade=t=out:st={total - 1.3:.2f}:d=1.3[m];"
          f"[m][2:a]amix=inputs=2:normalize=0:duration=first,atrim=0:{total:.2f},alimiter=limit=0.89[a]")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS), "-i", str(raw / "%05d.jpg"),
                    "-i", str(mwav), "-i", str(fxwav), "-filter_complex", fc, "-map", "0:v", "-map", "[a]",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", str(out)], check=True)
    shutil.rmtree(raw)
    mwav.unlink(); fxwav.unlink()
    print(out, f"{total}s", style)
    return out


if __name__ == "__main__":
    make(*sys.argv[1:4])
