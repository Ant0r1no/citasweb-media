"""Looks visuales para los vídeos con voz (generator/voicevideo.py): fondo, paleta, maqueta, transición,
entrada de palabras y decoración. pick_look() rota cada parte con pasos distintos y lo apunta en
videos/_looks.json para que dos vídeos seguidos no se parezcan."""
import base64
import colorsys
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG = ROOT / "videos/_looks.json"
FOTOS = ROOT / "marca/fotos"

FONDOS = ["manchas", "malla", "puntos", "rayas", "iconos", "foto"]
PALETAS = ["oscura", "clara", "viva"]
MAQUETAS = ["arriba", "centro", "abajo", "tarjeta"]
TRANS = ["sube", "lado", "zoom"]
ENTRADAS = ["rebote", "desliza", "enfoque"]
DECOS = ["emoji", "nada"]  # "numero" solo para series con capítulos

EMOJIS = {
    "general": "📅⏰📲✅💬", "barberia": "💈✂️🪒🧔💺", "peluqueria": "✂️💇‍♀️💆‍♀️🪮💜",
    "estetica": "💅✨💄🌸🪞", "restaurante": "🍽️🍷🍝🥂🧑‍🍳", "taller": "🔧🚗⚙️🛞🔩",
    "fisio": "💪🦴🩺🧘🤸", "dental": "🦷🪥😁✨🩺", "limpieza": "🧽🫧🧹✨🧼",
    "vet": "🐾🐶🐱🦴❤️", "fitness": "🏋️💪⏱️🥗🔥",
}


def fotos(sector):
    d = FOTOS / sector
    return sorted(d.glob("*.jpg")) if d.exists() else []


def pick_look(slug, sector):
    log = json.loads(LOG.read_text()) if LOG.exists() else {}
    if slug in log:
        return log[slug]
    n = len(log)
    fondos = FONDOS if fotos(sector) else FONDOS[:-1]
    prev = [v.get("fondo") for v in list(log.values())[-2:]]
    fondo = fondos[(n * 2 + 2) % len(fondos)]
    k = 0
    while fondo in prev and k < len(fondos):  # nunca el mismo fondo que los dos últimos vídeos
        k += 1
        fondo = fondos[(n * 2 + 2 + k) % len(fondos)]
    look = {"fondo": fondo,
            "paleta": "oscura" if fondo == "foto" else PALETAS[(n * 2 + 1) % 3],
            "maqueta": MAQUETAS[(n * 3) % 4], "trans": TRANS[n % 3], "entrada": ENTRADAS[(n * 2) % 3],
            "deco": DECOS[(n + 1) % 2], "semilla": 7 + n * 13}
    if fondo == "foto":
        fs = fotos(sector)
        look["foto"] = str(fs[n % len(fs)].relative_to(ROOT))
    log[slug] = look
    LOG.write_text(json.dumps(log, ensure_ascii=False, indent=1) + "\n")
    return look


def _rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def _hex(c):
    return "#" + "".join(f"{round(max(0, min(1, x)) * 255):02x}" for x in c)


def _mix(a, b, k):
    return _hex([x * (1 - k) + y * k for x, y in zip(_rgb(a), _rgb(b))])


def _hue(a, deg):
    h, l, s = colorsys.rgb_to_hls(*_rgb(a))
    return _hex(colorsys.hls_to_rgb((h + deg / 360) % 1, l, s))


def palette(theme, name):
    """Devuelve (bg, ac, variables CSS extra)."""
    bg, ac = theme
    if name == "clara":
        lbg = _mix(ac, "#ffffff", .87)
        return lbg, ac, {"--fg": bg, "--on": bg, "--ln": bg + "14", "--tr": bg + "22", "--mu": bg + "cc", "--ac2": _hue(ac, 50)}
    if name == "viva":
        return ac, bg, {"--fg": bg, "--on": ac, "--ln": bg + "14", "--tr": bg + "26", "--mu": bg + "d0", "--ac2": _hue(ac, -40)}
    return bg, ac, {"--fg": "#ffffff", "--ac2": _hue(ac, 45)}


CSS = """
.look #grid,.look .blob{display:none}
.f-manchas #grid,.f-manchas .blob,.f-puntos #b1,.f-rayas #b2,.f-iconos #b1,.f-iconos #b2{display:block}
#mesh{position:absolute;left:-50%;top:-25%;width:200%;height:150%;background:conic-gradient(from 0deg,var(--ac),var(--bg),var(--ac2),var(--bg),var(--ac));filter:blur(150px);opacity:.55}
#dots{position:absolute;inset:-120px;background-image:radial-gradient(var(--tr) 4px,transparent 4.5px);background-size:60px 60px}
#stripes{position:absolute;inset:-500px;background:repeating-linear-gradient(-45deg,color-mix(in srgb,var(--ac) 16%,transparent) 0 70px,transparent 70px 150px)}
.ico{position:absolute;left:0;top:0;line-height:1;opacity:.16;filter:saturate(.8)}
#photo{position:absolute;left:-6%;top:-4%;width:112%;height:108%;object-fit:cover}
#pov{position:absolute;inset:0;background:linear-gradient(180deg,color-mix(in srgb,var(--bg) 55%,transparent) 0%,color-mix(in srgb,var(--bg) 78%,transparent) 45%,color-mix(in srgb,var(--bg) 94%,transparent) 100%)}
#num.emo{color:initial;-webkit-text-stroke:0;opacity:.11;font-size:560px;right:-40px;top:1080px}
#num.none{display:none}
.m-centro .top,.m-centro .ph,.m-centro .cta{text-align:center}.m-centro .btnrow{justify-content:center}
.m-centro .ph:not(.withsc){top:800px}
.m-abajo .ph:not(.withsc){top:auto;bottom:430px;font-size:80px}
.m-abajo #num{top:300px}
.m-tarjeta .ph:not(.withsc){top:700px;padding:60px 56px;font-size:74px;border-radius:52px;background:color-mix(in srgb,var(--bg) 72%,transparent);border:3px solid color-mix(in srgb,var(--ac) 55%,transparent);box-shadow:0 30px 80px #0005}
"""

JS = r"""
function lookRender(t, pulse){
  const L = window.LOOK; if (!L) return;
  const m = document.getElementById('mesh'); if (m) m.style.transform = `rotate(${t*14}deg) scale(${1+.05*pulse})`;
  const d = document.getElementById('dots'); if (d) d.style.transform = `translate(${(t*22)%60}px,${(t*34)%60}px)`;
  const s = document.getElementById('stripes'); if (s) s.style.transform = `translateX(${(t*45)%212}px)`;
  const ph = document.getElementById('photo'); if (ph) ph.style.transform = `scale(${1+.07*t/TOTAL}) translate(${-28*t/TOTAL}px,${-14*t/TOTAL}px)`;
  (L.icons||[]).forEach((c,i) => { const el = document.getElementById('ico'+i);
    const y = ((c.y - t*c.sp) % 2300 + 2300) % 2300 - 200;
    el.style.transform = `translate(${c.x + 30*Math.sin(t*.6+i)}px,${y}px) rotate(${c.r + 12*Math.sin(t*.5+i)}deg) scale(${1+.04*pulse})`; });
}
function lookOut(el, o){
  const T = (window.LOOK||{}).trans || 'sube', e = 1 - Math.pow(1 - Math.min(Math.max(o,0),1), 3);
  if (T === 'lado') return `translateX(${-260*e}px)`;
  if (T === 'zoom') return `scale(${1-.25*e})`;
  return `translateY(${-120*e}px)`;
}
function lookWord(w, s, b){
  const E = (window.LOOK||{}).entrada || 'rebote';
  if (E === 'desliza'){ const k = 1 - Math.pow(1-Math.min(Math.max(s,0),1),3); w.style.transform = `translateX(${(1-k)*-70}px)`; w.style.filter = ''; return; }
  if (E === 'enfoque'){ const k = Math.min(Math.max(s,0),1); w.style.transform = `scale(${1.25-.25*k})`; w.style.filter = `blur(${(1-k)*14}px)`; return; }
  w.style.transform = `translateY(${(1-b)*50}px) scale(${.55+.45*b})`;
}
"""


def build(look, theme, sector, n):
    """Devuelve (bg, ac, vars_css, clases_body, html_fondo, contenido_num, js_look)."""
    bg, ac, vars_ = palette(theme, look.get("paleta", "oscura"))
    f = look.get("fondo", "manchas")
    rnd = random.Random(look.get("semilla", 1))
    html, icons = "", []
    if f == "malla":
        html = '<div id="mesh"></div>'
    elif f == "puntos":
        html = '<div id="dots"></div>'
    elif f == "rayas":
        html = '<div id="stripes"></div>'
    elif f == "iconos":
        em = list(EMOJIS.get(sector, EMOJIS["general"]).replace("‍", "‍"))
        em = _split_emojis(EMOJIS.get(sector, EMOJIS["general"]))
        for i in range(13):
            icons.append({"x": rnd.randint(-60, 960), "y": rnd.randint(0, 2300), "sp": rnd.uniform(28, 70), "r": rnd.randint(-25, 25)})
            html += f'<div class="ico" id="ico{i}" style="font-size:{rnd.randint(90, 210)}px">{em[i % len(em)]}</div>'
    elif f == "foto" and look.get("foto"):
        b64 = base64.b64encode((ROOT / look["foto"]).read_bytes()).decode()
        html = f'<img id="photo" src="data:image/jpeg;base64,{b64}"><div id="pov"></div>'
    deco = look.get("deco", "numero")
    if deco == "emoji":
        num = (_split_emojis(EMOJIS.get(sector, EMOJIS["general"])) or ["📅"])[rnd.randrange(5)], "emo"
    elif deco == "nada":
        num = "", "none"
    else:
        num = f"{n:02d}", ""
    classes = f"look f-{f} m-{look.get('maqueta', 'arriba')}"
    js = "window.LOOK=" + json.dumps({"trans": look.get("trans"), "entrada": look.get("entrada"), "icons": icons}) + ";"
    return bg, ac, vars_, classes, html, num, js


def _split_emojis(s):
    """Separa una cadena de emojis respetando ZWJ y selectores de variante."""
    out, cur = [], ""
    for ch in s:
        if cur and ch not in "‍️" and not cur.endswith("‍"):
            out.append(cur)
            cur = ""
        cur += ch
    if cur:
        out.append(cur)
    return out
