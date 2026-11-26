#!/usr/bin/env python3
"""Monta vídeos verticales (1080x1920) a partir de una grabación de voz y un JSON de frases con tiempos.

Uso: python3 generator/voicevideo.py videos/tipos.json [ruta_audio]
Para cada vídeo crea videos/<slug>/video.mp4 (y cover.jpg con la portada).
Formato del JSON: ver videos/tipos.json. "cta" como texto muestra la pantalla final "Comenta CITA".
"""
import json
import subprocess
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).parent))
from render import THEMES, LOGO, esc  # noqa: E402
import music  # noqa: E402
import wave  # noqa: E402

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
body{width:1080px;height:1920px;background:var(--bg);color:#fff;font-family:'Poppins','Inter',sans-serif;position:relative;overflow:hidden}
.glow{position:absolute;width:1200px;height:1200px;border-radius:50%;background:var(--ac);opacity:.14;filter:blur(150px);right:-500px;top:-400px}
.top{position:absolute;left:80px;right:80px;top:170px}
.kicker{display:inline-block;background:var(--ac);color:var(--bg);font-weight:800;font-size:34px;letter-spacing:4px;padding:12px 28px;border-radius:999px}
.hook{margin-top:34px;font-size:64px;font-weight:800;line-height:1.08;letter-spacing:-1px}
.hook em,.ph em,.cta em{font-style:normal;color:var(--ac)}
.ph{position:absolute;left:80px;right:80px;top:760px;font-size:84px;font-weight:800;line-height:1.12;letter-spacing:-1.5px}
.bar{position:absolute;left:80px;right:80px;bottom:300px;height:10px;background:#ffffff22;border-radius:9px;overflow:hidden}
.bar i{display:block;height:100%;background:var(--ac)}
.foot{position:absolute;left:80px;right:80px;bottom:190px;display:flex;justify-content:space-between;align-items:center;font-size:38px;font-weight:700}
.brand{display:flex;align-items:center;gap:16px}.brand svg{width:58px;height:58px;color:var(--ac)}
.cta{position:absolute;left:80px;right:80px;top:700px;font-size:96px;font-weight:800;line-height:1.08}
.word{display:inline-block;margin-top:50px;border:7px solid var(--ac);color:var(--ac);font-size:80px;font-weight:800;padding:20px 48px;border-radius:34px}
.sub{font-size:46px;color:#ffffffcc;font-weight:600;margin-top:40px}
"""


def frame_html(theme, series, n, hook, text, progress, word):
    bg, ac = theme
    if text == "cta":
        mid = (f'<div class="cta">¿Quieres que tu agenda <em>funcione sola</em>?'
               f'<div><span class="word">Comenta “{esc(word)}”</span></div>'
               f'<div class="sub">Pruébala 15 días gratis · citasweb.es</div></div>')
    else:
        mid = f'<div class="ph">{esc(text)}</div>'
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>:root{{--bg:{bg};--ac:{ac}}}{CSS}</style></head>
<body><div class="glow"></div><div class="top"><span class="kicker">{esc(series)} · #{n}</span>
<div class="hook">{esc(hook)}</div></div>{mid}
<div class="bar"><i style="width:{progress:.1f}%"></i></div>
<div class="foot"><div class="brand">{LOGO}<span>CitasWeb</span></div><span>citasweb.es</span></div></body></html>"""


def main(cfg_path, audio_override=None):
    cfg_path = Path(cfg_path)
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    audio = audio_override or cfg["audio"]
    theme = THEMES.get(cfg.get("sector", "general"), THEMES["general"])
    word = cfg.get("word", "CITA")
    out_root = cfg_path.parent
    mcfg = cfg.get("music", {"style": "house", "volume": 0.30})  # {"style":..,"volume":..} o null para sin música
    outname = cfg.get("outname", "video.mp4")
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1920})
        for v in cfg["videos"]:
            d = out_root / v["slug"]
            d.mkdir(parents=True, exist_ok=True)
            start, end = v["start"], v["end"]
            total = end - start
            phrases = v["phrases"]
            concat = []
            for i, (t, text) in enumerate(phrases):
                t0 = 0 if i == 0 else t - start
                t1 = (phrases[i + 1][0] - start) if i + 1 < len(phrases) else total
                prog = 100 * t1 / total
                pg.set_content(frame_html(theme, cfg["series"], v["n"], v["hook"], text, prog, word), wait_until="networkidle")
                f = d / f"f{i:02d}.png"
                pg.screenshot(path=str(f))
                concat.append((f, t1 - t0))
            # portada: primer fotograma
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(concat[0][0]), "-q:v", "3", str(d / "cover.jpg")], check=True)
            lst = d / "list.txt"
            lines = []
            for f, dur in concat:
                lines += [f"file '{f.name}'", f"duration {dur:.3f}"]
            lines.append(f"file '{concat[-1][0].name}'")
            lst.write_text("\n".join(lines))
            voice = f"[1:a]afade=t=in:d=0.15,afade=t=out:st={total-0.4:.2f}:d=0.4,loudnorm=I=-16:TP=-1.5"
            extra_in = []
            if mcfg:
                styles = mcfg.get("styles") or [mcfg.get("style", "house")]
                style = v.get("music_style") or styles[(v["n"] - 1) % len(styles)]
                wav = d / "music.wav"
                data = music.make(total + 0.5, style, seed=v.get("music_seed", v["n"]))
                with wave.open(str(wav), "wb") as w:
                    w.setnchannels(2); w.setsampwidth(2); w.setframerate(music.SR); w.writeframes(data.tobytes())
                extra_in = ["-i", str(wav)]
                vol = mcfg.get("volume", 0.30)
                fc = (f"{voice},asplit=2[v1][v2];"
                      f"[2:a]volume={vol},afade=t=out:st={total-1.2:.2f}:d=1.2[m];"
                      f"[m][v2]sidechaincompress=threshold=0.04:ratio=6:attack=15:release=350[md];"
                      f"[v1][md]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.89[a]")
            else:
                fc = voice + "[a]"
            subprocess.run([
                "ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
                "-ss", f"{start}", "-t", f"{total}", "-i", audio, *extra_in,
                "-filter_complex", fc,
                "-map", "0:v", "-map", "[a]", "-r", "30", "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
                "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart",
                str(d / outname)], check=True)
            for f, _ in concat:
                f.unlink()
            lst.unlink()
            if mcfg:
                wav.unlink()
            print(d / outname)
        b.close()


if __name__ == "__main__":
    main(*sys.argv[1:3])
