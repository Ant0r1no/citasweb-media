#!/usr/bin/env python3
"""Monta un vídeo con la voz del dueño combinando frases del banco (voz/NN.mp3).

Uso:
  python3 generator/vozmix.py <slug> <sector> "<gancho en pantalla>" <n1> <n2> ... [--escena k=json]

- Las frases se pegan en orden con una pausa corta, se crea videos/<slug>/voz.wav y
  videos/<slug>.json (configuración de generator/voicevideo.py), y se renderiza el vídeo.
- El texto en pantalla de cada frase es el de voz/indice.json. Se puede resaltar una
  parte poniéndola entre *asteriscos* con --texto k="Texto con *resalte*".
- --escena k='{"type":"call",...}' añade una escena de móvil a la frase número k (1 = primera).
- La última frase debe ser un cierre (64-80); después sale la pantalla final con la palabra clave.
"""
import json
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SR = 44100
GAP = 0.18


def load(n):
    a = subprocess.run(["ffmpeg", "-v", "error", "-i", str(ROOT / f"voz/{n:02d}.mp3"), "-f", "s16le",
                        "-ac", "1", "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(a, np.int16)


def main(argv):
    slug, sector, hook = argv[0], argv[1], argv[2]
    nums, scenes, texts = [], {}, {}
    for a in argv[3:]:
        if a.startswith("--escena"):
            continue
        if "=" in a and a.split("=", 1)[0].isdigit():
            k, v = a.split("=", 1)
            if v.strip().startswith("{"):
                scenes[int(k)] = json.loads(v)
            else:
                texts[int(k)] = v
        elif a.isdigit():
            nums.append(int(a))
    idx = {i["n"]: i for i in json.loads((ROOT / "voz/indice.json").read_text())}
    word = "CITA"
    last = idx[nums[-1]]["texto"]
    if last.startswith("Comenta "):
        word = last.split()[1]
    parts, phrases, t = [], [], 0.0
    for k, n in enumerate(nums, 1):
        a = load(n)
        phrases.append([round(t, 3), texts.get(k, idx[n]["texto"])] + ([scenes[k]] if k in scenes else []))
        parts += [a, np.zeros(int(GAP * SR), np.int16)]
        t += len(a) / SR + GAP
    audio = np.concatenate(parts)
    d = ROOT / "videos" / slug
    d.mkdir(parents=True, exist_ok=True)
    wav = d / "voz.wav"
    with wave.open(str(wav), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(audio.tobytes())
    end = round(t - GAP, 3)
    phrases.append([end, "cta"])
    cfg = {"audio": str(wav), "sector": sector, "series": "CITASWEB", "word": word, "outname": "video.mp4",
           "music": {"styles": ["pop", "funk", "house", "disco", "lofi", "chill"], "volume": 0.6},
           "videos": [{"slug": slug, "n": 1, "hook": hook, "start": 0, "end": end, "tail": 2.6,
                       "kicker": "CITASWEB", "music_style": ["pop", "funk", "house", "disco", "lofi", "chill"][sum(map(ord, slug)) % 6],
                       "music_seed": sum(map(ord, slug)) % 97, "phrases": phrases}]}
    cj = ROOT / "videos" / f"{slug}.json"
    cj.write_text(json.dumps(cfg, ensure_ascii=False, indent=1))
    # voicevideo crea videos/<slug>/ junto a su json: el json va en videos/
    subprocess.run([sys.executable, str(ROOT / "generator/voicevideo.py"), str(cj), str(wav)], check=True)
    wav.unlink()
    print(d / "video.mp4")


if __name__ == "__main__":
    main(sys.argv[1:])
