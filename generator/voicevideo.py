#!/usr/bin/env python3
"""Monta vídeos verticales ANIMADOS (1080x1920, 30 fps) a partir de una grabación de voz y un JSON de frases con tiempos.

Uso: python3 generator/voicevideo.py videos/tipos.json [ruta_audio]
Para cada vídeo crea videos/<slug>/<outname> (por defecto video.mp4) y cover.jpg.
Formato del JSON: ver videos/tipos.json. "cta" como texto muestra la pantalla final "Comenta CITA".

Animación: fondo con manchas de color en movimiento y rejilla que se desplaza, pulso al ritmo de la música,
palabras que aparecen una a una al ritmo de la voz (con rebote), resaltado que se "pinta" detrás de las
palabras clave, transición de salida entre frases, zoom lento y pantalla final con botón que late.
Música: base original de generator/music.py mezclada bajo la voz (baja un poco cuando se habla).
"""
import html
import json
import shutil
import subprocess
import sys
import wave
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).parent))
from render import THEMES, LOGO, esc  # noqa: E402
import music  # noqa: E402
import scenes  # noqa: E402
import sfx  # noqa: E402

FPS = 30

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
body{width:1080px;height:1920px;background:var(--bg);color:#fff;font-family:'Poppins','Inter',sans-serif;position:relative;overflow:hidden}
.blob{position:absolute;border-radius:50%;will-change:transform}
#b1{width:1400px;height:1400px;background:radial-gradient(closest-side,var(--ac),transparent);opacity:.3}
#b2{width:1100px;height:1100px;background:radial-gradient(closest-side,var(--ac),transparent);opacity:.22}
#b3{width:1000px;height:1000px;background:radial-gradient(closest-side,#fff,transparent);opacity:.06}
#grid{position:absolute;inset:-200px;background-image:linear-gradient(#ffffff0d 2px,transparent 2px),linear-gradient(90deg,#ffffff0d 2px,transparent 2px);background-size:120px 120px}
#stage{position:absolute;inset:0;transform-origin:50% 45%}
.top{position:absolute;left:80px;right:80px;top:170px}
.kicker{display:inline-block;background:var(--ac);color:var(--bg);font-weight:800;font-size:34px;letter-spacing:4px;padding:12px 28px;border-radius:999px}
.hook{margin-top:34px;font-size:64px;font-weight:800;line-height:1.08;letter-spacing:-1px}
.hook em,.cta em{font-style:normal;color:var(--ac)}
.ph{position:absolute;left:80px;right:80px;top:740px;font-size:86px;font-weight:800;line-height:1.16;letter-spacing:-1.5px;opacity:0}
.w{display:inline-block;opacity:0;transform-origin:50% 80%;position:relative}
.g{position:relative;display:inline-block;z-index:0}
.g .w{color:var(--bg)}
.g::before{content:"";position:absolute;left:-.14em;right:-.14em;top:-.02em;bottom:-.06em;background:var(--ac);border-radius:.14em;z-index:-1;transform:scaleX(var(--s,0));transform-origin:0 50%}
.bar{position:absolute;left:80px;right:80px;bottom:300px;height:12px;background:#ffffff22;border-radius:9px;overflow:hidden}
.bar i{display:block;height:100%;background:var(--ac);width:0}
.foot{position:absolute;left:80px;right:80px;bottom:190px;display:flex;justify-content:space-between;align-items:center;font-size:38px;font-weight:700}
.brand{display:flex;align-items:center;gap:16px}.brand svg{width:58px;height:58px;color:var(--ac)}
.cta{position:absolute;left:80px;right:80px;top:680px;font-size:96px;font-weight:800;line-height:1.08;opacity:0}
.word{display:inline-block;margin-top:50px;background:var(--ac);color:var(--bg);font-size:80px;font-weight:800;padding:24px 52px;border-radius:34px;box-shadow:0 0 0 0 var(--ac)}
.sub{font-size:46px;color:#ffffffcc;font-weight:600;margin-top:40px}
.arrow{display:inline-block;font-size:90px;margin-left:24px}
.btnrow{display:flex;align-items:center;flex-wrap:nowrap;margin-top:50px}.btnrow .word{margin-top:0;white-space:nowrap;flex:none}
#num{position:absolute;right:-60px;top:1050px;font-size:720px;font-weight:900;color:transparent;-webkit-text-stroke:4px var(--ac);opacity:.13;line-height:1}
#flash{position:absolute;inset:0;background:var(--ac);opacity:0;pointer-events:none}
.ph.withsc{top:450px;font-size:72px}
#fade{position:absolute;left:0;right:0;bottom:0;height:380px;background:linear-gradient(180deg,transparent,var(--bg) 55%);z-index:5;opacity:0}
.bar,.foot{z-index:6}
#phone{z-index:4}
""" + scenes.CSS

JS = r"""
const P = window.PHR, BPM = window.BPM, FOUR = window.FOUR, TOTAL = window.TOTAL;
const ease = x => 1 - Math.pow(1 - Math.min(Math.max(x,0),1), 3);
const back = x => { x = Math.min(Math.max(x,0),1); const c = 1.9; return 1 + (c+1)*Math.pow(x-1,3) + c*Math.pow(x-1,2); };
const $ = id => document.getElementById(id);
function render(t){
  // fondo
  $('b1').style.transform = `translate(${380+260*Math.sin(t*.35)}px,${-300+220*Math.cos(t*.27)}px)`;
  $('b2').style.transform = `translate(${-250+200*Math.cos(t*.31)}px,${1100+260*Math.sin(t*.23)}px)`;
  $('b3').style.transform = `translate(${300+300*Math.sin(t*.19+1)}px,${700+300*Math.cos(t*.21)}px)`;
  $('grid').style.transform = `translate(${(t*30)%120}px,${(t*45)%120}px)`;
  // pulso al ritmo
  const beat = 60/BPM, ph = (t % (FOUR ? beat : 2*beat)) / (FOUR ? beat : 2*beat);
  const pulse = Math.exp(-ph*6);
  $('b1').style.opacity = (.26 + .16*pulse).toFixed(3);
  $('num').style.transform = `translateY(${-40*Math.sin(t*.4)}px) rotate(${-6+4*Math.sin(t*.25)}deg) scale(${1+.03*pulse})`;
  // frase activa
  let cur = 0; for (let i=0;i<P.length;i++) if (t >= P[i].t0) cur = i;
  const p = P[cur], lt = t - p.t0;
  // zoom lento + golpe al ritmo
  $('stage').style.transform = `scale(${(1 + .035*Math.min(lt/(p.t1-p.t0),1) + .008*pulse).toFixed(4)})`;
  // flash al cambiar de frase
  $('flash').style.opacity = cur>0 ? (.18*Math.max(0,1-lt/.18)).toFixed(3) : 0;
  // gancho: visible desde el fotograma 0, grande en el centro, y sube a su sitio
  const k = ease((t-.75)/.45);
  document.querySelector('.hook').style.transform = `translateY(${(1-k)*400}px)`;
  document.querySelector('.hook').style.fontSize = (100-36*k).toFixed(1)+'px';
  // móvil
  const PH = $('phone');
  if (PH){
    const has = i => i>=0 && P[i] && P[i].sc;
    let y;
    if (has(cur)) y = has(cur-1) ? 0 : 1150*(1-ease(lt/.45));
    else y = has(cur-1) ? 1150*ease(lt/.35) : 1150;
    PH.style.transform = `translateY(${y}px) rotate(${has(cur)?(-1.5+1.5*ease(lt/.5)):0}deg)`;
    $('fade').style.opacity = (1 - y/1150).toFixed(3);
    P.forEach((q,i) => { const sc = $('sc'+i); if (!sc) return; const on = i===cur || (i===cur-1 && !has(cur) && lt<.35); sc.style.opacity = on?1:0; if (on) sceneRender(sc, i===cur?lt:(t-q.t0), t); });
  }
  // frases
  P.forEach((q,i) => {
    const el = $('p'+i);
    if (i < cur){
      const o = (t - P[i+1].t0)/.22;
      el.style.opacity = Math.max(0,1-o); el.style.transform = `translateY(${-120*ease(o)}px)`;
      return;
    }
    if (i > cur){ el.style.opacity = 0; return; }
    el.style.opacity = 1; el.style.transform = 'none';
    const ws = el.querySelectorAll('.w'), n = ws.length;
    const d0 = i===0 ? .8 : 0;
    const span = Math.max(.35, Math.min((q.t1-q.t0-d0)*.7, n*.32));
    ws.forEach((w,j) => {
      const s = (lt - d0 - j*span/n)/.28;
      const b = back(s);
      w.style.opacity = Math.min(1, Math.max(0, s*2));
      w.style.transform = `translateY(${(1-b)*50}px) scale(${.55+.45*b})`;
      w._s = s;
    });
    el.querySelectorAll('.g').forEach(g => { const l = g.querySelectorAll('.w'); g.style.setProperty('--s', ease((l[l.length-1]._s-.5)/.8).toFixed(3)); });
    if (q.cta){
      const wd = el.querySelector('.word');
      wd.style.transform = `scale(${(1+.06*pulse).toFixed(3)})`;
      wd.style.boxShadow = `0 0 0 ${Math.round(30*(1-pulse))}px rgba(255,255,255,${(.25*pulse).toFixed(2)})`;
      el.querySelector('.arrow').style.transform = `translateX(${-18*Math.abs(Math.sin(t*Math.PI*BPM/60))}px)`;
      el.style.opacity = ease(lt/.3); el.style.transform = `translateY(${(1-ease(lt/.4))*80}px)`;
    }
  });
  $('bar').style.width = (100*Math.min(t/TOTAL,1)).toFixed(2)+'%';
}
"""


def words_html(text):
    """Separa en palabras animables; las palabras entre *asteriscos* van juntas en un grupo resaltado."""
    out, grp, hl = [], [], False
    for tok in text.split():
        clean = html.escape(tok.replace("*", ""))
        if tok.startswith("*") and not hl:
            hl = True
        span = f'<span class="w">{clean}</span>' if clean else ""
        if hl:
            if span: grp.append(span)
        elif span:
            out.append(span)
        if hl and tok.rstrip(".,;:!?…»”").endswith("*") and not (tok == "*"):
            hl = False
            out.append('<span class="g">' + " ".join(grp) + "</span>")
            grp = []
    if grp:
        out.append('<span class="g">' + " ".join(grp) + "</span>")
    return " ".join(out)


def page_html(theme, series, n, hook, phrases, word, bpm, four, total):
    bg, ac = theme
    blocks, meta = [], []
    phone = []
    for i, (t0, t1, text, sc) in enumerate(phrases):
        if sc:
            h, _ = scenes.build(sc, t1 - t0)
            phone.append(h.replace('<div class="scr', f'<div id="sc{i}" class="scr', 1))
        if text == "cta":
            blocks.append(f'<div class="cta" id="p{i}"><span class="w">¿Quieres</span> <span class="w">que</span> <span class="w">tu</span> '
                          f'<span class="w">agenda</span> <span class="g"><span class="w">funcione</span> <span class="w">sola?</span></span>'
                          f'<div class="btnrow"><span class="word">Comenta “{html.escape(word)}”</span><span class="arrow">👈</span></div>'
                          f'<div class="sub">Pruébala 15 días gratis · citasweb.es</div></div>')
            meta.append({"t0": t0, "t1": t1, "cta": True, "sc": bool(sc)})
        else:
            blocks.append(f'<div class="ph{" withsc" if sc else ""}" id="p{i}">{words_html(text)}</div>')
            meta.append({"t0": t0, "t1": t1, "cta": False, "sc": bool(sc)})
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>:root{{--bg:{bg};--ac:{ac}}}{CSS}</style></head>
<body><div id="grid"></div><div id="num">{n:02d}</div><div class="blob" id="b1"></div><div class="blob" id="b2"></div><div class="blob" id="b3"></div>
<div id="stage"><div class="top"><span class="kicker">{esc(series)} · #{n}</span><div class="hook">{esc(hook)}</div></div>
{''.join(blocks)}</div>
<div id="phone" style="transform:translateY(1150px)">{''.join(phone)}</div><div id="fade"></div>
<div class="bar"><i id="bar"></i></div>
<div class="foot"><div class="brand">{LOGO}<span>CitasWeb</span></div><span>citasweb.es</span></div>
<div id="flash"></div>
<script>window.PHR={json.dumps(meta)};window.BPM={bpm};window.FOUR={str(four).lower()};window.TOTAL={total};{JS}{scenes.JS}</script>
</body></html>"""


def main(cfg_path, audio_override=None):
    cfg_path = Path(cfg_path)
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    audio = audio_override or cfg["audio"]
    theme = THEMES.get(cfg.get("sector", "general"), THEMES["general"])
    word = cfg.get("word", "CITA")
    out_root = cfg_path.parent
    mcfg = cfg.get("music", {"styles": ["house", "pop", "lofi"], "volume": 0.6})
    outname = cfg.get("outname", "video.mp4")
    only = sys.argv[3:]  # opcional: slugs concretos
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1920})
        for v in cfg["videos"]:
            if only and v["slug"] not in only:
                continue
            d = out_root / v["slug"]
            d.mkdir(parents=True, exist_ok=True)
            start, end = v["start"], v["end"]
            vlen = end - start
            total = vlen + v.get("tail", 0)  # tail: segundos extra de silencio para la pantalla final
            ph = v["phrases"]
            phrases = []
            events = []
            for i, (t, text, *rest) in enumerate(ph):
                t0 = 0 if i == 0 else t - start
                t1 = (ph[i + 1][0] - start) if i + 1 < len(ph) else total
                sc = rest[0] if rest else None
                phrases.append((round(t0, 3), round(t1, 3), text, sc))
                if i > 0:
                    events.append((max(0, t0 - 0.12), "whoosh"))
                if sc:
                    events += [(t0 + et, kind) for et, kind in scenes.build(sc, t1 - t0)[1]]
                if text == "cta":
                    events.append((t0 + 0.35, "pop"))
            styles = (mcfg or {}).get("styles") or [(mcfg or {}).get("style", "house")]
            style = v.get("music_style") or styles[(v["n"] - 1) % len(styles)]
            sc = music.STYLES[style]
            pg.set_content(page_html(theme, cfg["series"], v["n"], v["hook"], phrases, word, sc["bpm"], sc["four"], total),
                           wait_until="networkidle")
            # portada: primera frase ya completa
            pg.evaluate(f"render({min(phrases[0][1] - 0.05, 2.5)})")
            pg.screenshot(path=str(d / "cover.jpg"), type="jpeg", quality=88)
            raw = d / "frames"
            raw.mkdir(exist_ok=True)
            nframes = int(total * FPS)
            for f in range(nframes):
                pg.evaluate(f"render({f / FPS:.4f})")
                pg.screenshot(path=str(raw / f"{f:05d}.jpg"), type="jpeg", quality=90)
            voice = (f"[1:a]afade=t=in:d=0.15,afade=t=out:st={vlen-0.4:.2f}:d=0.4,apad=pad_dur=6,"
                     f"loudnorm=I=-16:TP=-1.5,aresample=44100,atrim=0:{total:.3f}")  # apad: loudnorm se come los últimos 3 s
            fxwav = d / "sfx.wav"
            with wave.open(str(fxwav), "wb") as w:
                w.setnchannels(2); w.setsampwidth(2); w.setframerate(sfx.SR); w.writeframes(sfx.make_track(total, events).tobytes())
            extra_in = []
            if mcfg:
                wav = d / "music.wav"
                data = music.make(total + 0.5, style, seed=v.get("music_seed", v["n"]))
                with wave.open(str(wav), "wb") as w:
                    w.setnchannels(2); w.setsampwidth(2); w.setframerate(music.SR); w.writeframes(data.tobytes())
                extra_in = ["-i", str(wav), "-i", str(fxwav)]
                vol = mcfg.get("volume", 0.6)
                fc = (f"{voice},asplit=2[v1][v2];"
                      f"[2:a]volume={vol},afade=t=out:st={total-1.2:.2f}:d=1.2[m];"
                      f"[m][v2]sidechaincompress=threshold=0.1:ratio=2.5:attack=30:release=400:makeup=1[md];"
                      f"[v1][md][3:a]amix=inputs=3:normalize=0:duration=first,alimiter=limit=0.89[a]")
            else:
                extra_in = ["-i", str(fxwav)]
                fc = voice + "[v];[v][2:a]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.89[a]"
            subprocess.run([
                "ffmpeg", "-y", "-v", "error", "-framerate", str(FPS), "-i", str(raw / "%05d.jpg"),
                "-ss", f"{start}", "-t", f"{vlen}", "-i", audio, *extra_in,
                "-filter_complex", fc,
                "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
                "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart",
                str(d / outname)], check=True)
            shutil.rmtree(raw)
            fxwav.unlink()
            if mcfg:
                wav.unlink()
            print(d / outname, style)
        b.close()


if __name__ == "__main__":
    main(*sys.argv[1:3])
