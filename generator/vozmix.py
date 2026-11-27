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

sys.path.insert(0, str(Path(__file__).parent))
import looks  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SR = 44100
GAP = 0.18


# Datos de ejemplo por sector para las escenas de móvil (negocios ficticios).
SECT = {
    "barberia": ("Barbería Norte", "barberianorte", "barbería", [["Corte", "15 €", "30 min"], ["Corte + barba", "20 €", "45 min"], ["Degradado", "17 €", "40 min"]], "un corte"),
    "peluqueria": ("Salón Aura", "salonaura", "peluquería", [["Corte y peinado", "28 €", "45 min"], ["Color", "45 €", "90 min"], ["Mechas", "60 €", "2 h"]], "unas mechas"),
    "estetica": ("Studio Nails", "studionails", "centro de uñas", [["Manicura semi", "22 €", "45 min"], ["Uñas gel", "35 €", "75 min"], ["Pedicura", "28 €", "50 min"]], "uñas de gel"),
    "fisio": ("FisioCentro", "fisiocentro", "fisioterapeuta", [["Sesión fisio", "40 €", "50 min"], ["Masaje descarga", "35 €", "45 min"], ["Valoración", "30 €", "30 min"]], "una sesión"),
    "dental": ("Clínica Sonrisa", "clinicasonrisa", "dentista", [["Revisión", "Gratis", "20 min"], ["Limpieza", "45 €", "40 min"], ["Blanqueamiento", "180 €", "60 min"]], "una limpieza"),
    "vet": ("Vet Patitas", "vetpatitas", "veterinario", [["Consulta", "35 €", "30 min"], ["Vacuna", "40 €", "20 min"], ["Peluquería canina", "30 €", "60 min"]], "la vacuna"),
    "taller": ("Taller Ruiz", "tallerruiz", "taller", [["Cambio de aceite", "59 €", "45 min"], ["Pre-ITV", "35 €", "40 min"], ["Neumáticos", "Desde 60 €", "60 min"]], "el cambio de aceite"),
    "limpieza": ("Limpiezas Brillo", "limpiezasbrillo", "limpieza a domicilio", [["Limpieza 3 h", "45 €", "3 h"], ["Fin de obra", "Desde 120 €", "6 h"], ["Cristales", "30 €", "2 h"]], "una limpieza"),
    "restaurante": ("Casa Lola", "casalola", "restaurante", [["Mesa 2 pers.", "", "Cena"], ["Mesa 4 pers.", "", "Cena"], ["Menú del día", "14 €", "Comida"]], "mesa para 4"),
    "fitness": ("Entrena con Dani", "entrenacondani", "entrenador personal", [["Sesión 1 a 1", "35 €", "60 min"], ["Bono 8", "240 €", "8 sesiones"], ["Valoración", "Gratis", "30 min"]], "una sesión"),
    "general": ("Tu Negocio", "tunegocio", "negocio", [["Servicio 1", "25 €", "30 min"], ["Servicio 2", "40 €", "60 min"], ["Primera visita", "Gratis", "20 min"]], "una cita"),
}


def escena(n, sector):
    biz, sub, q, svcs, algo = SECT.get(sector, SECT["general"])
    web = {"type": "web", "biz": biz, "url": f"{sub}.citasweb.es", "services": svcs}
    agenda = lambda sl, **k: {"type": "agenda", "title": biz, "sub": k.get("sub", "Martes"), "slots": sl}
    return {
        34: {"type": "call", "name": "Cliente nuevo", "time": "17:32"},
        35: {"type": "chat", "name": "Cliente nuevo", "msgs": [["out", "¡Hola! Perdona, estaba con un cliente", "18:05"], ["in", "Nada, ya he reservado en otro sitio 🙏", "18:06"]]},
        36: {"type": "notif", "clock": "23:47", "items": [["WhatsApp", "Ana", f"¿Tienes hueco mañana para {algo}?"], ["WhatsApp", "Javi", "¿Y el sábado por la mañana?"], ["Instagram", "laura_92", "Hola!! precio??"]]},
        37: {"type": "chat", "name": "Marta", "msgs": [["out", "¿Te apunto el jueves a las 17:00?", "12:10"], ["in", "Ya te digo algo 👍", "12:31"]], "seen": True},
        38: {"type": "money", "lines": ["Ejemplo: 1 plantón = 25 €", "3 a la semana = 75 €"], "total": 300},
        39: {"type": "chat", "name": "Cliente", "msgs": [["in", f"¿Cuánto cuesta {algo}?", "10:02"], ["in", "¿Y cuánto tarda?", "10:02"], ["in", "¿Tenéis hueco hoy?", "10:03"]], "typing": True},
        41: {"type": "search", "query": f"{q} cerca de mí", "results": [["Otro negocio", "Reserva online · 4 min", True], [biz, "Sin web · sin horario", False]]},
        42: {"type": "notif", "date": "domingo, 19 de enero", "clock": "21:15", "items": [["WhatsApp", "Pedro", "¿Me cambias al martes?"], ["WhatsApp", "Sara", "No puedo el lunes 😥"], ["WhatsApp", "Luis", "¿Hay hueco el miércoles?"]]},
        44: web, 45: web, 46: web, 50: web,
        47: dict(web, time="02:14"), 55: dict(web, time="23:58"), 54: dict(web, url=f"www.{sub}.es"),
        48: {"type": "notif", "clock": "09:00", "items": [[biz, "Recordatorio de tu cita", "Mañana a las 10:00 · ¡Te esperamos!"]]},
        49: agenda([["10:00", "Ana · cancelada", "free", 0.5, "Libre"], ["10:00", "Javi · reservado", "booked", 1.4], ["11:30", "Marta", "busy"], ["12:30", "Libre", "free"]]),
        51: agenda([["10:00", "Laura · ocupado", "busy"], ["11:00", "Libre", "free"], ["12:00", "Nueva reserva", "booked", 1.0]], sub="Laura · Martes"),
        53: {"type": "search", "query": f"{q} cerca de mí", "results": [[biz, "Reserva online · abierto", True, 1.6], ["Otro negocio", "Sin web", False]]},
        56: agenda([["10:00", "Reservado", "booked", 0.4], ["11:00", "Reservado", "booked", 0.9], ["12:00", "Reservado", "booked", 1.4], ["13:00", "Reservado", "booked", 1.9]]),
    }.get(n)


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
    # escenas automáticas: como mucho 2 (una de problema y una de solución) si no se dan a mano
    if not scenes:
        auto = [k for k, n in enumerate(nums, 1) if escena(n, sector)]
        pick = [k for k in auto if nums[k - 1] < 44][:1] + [k for k in auto if nums[k - 1] >= 44][:1]
        scenes = {k: escena(nums[k - 1], sector) for k in pick}
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
                       "kicker": "CITASWEB", "look": looks.pick_look(slug, sector), "music_style": ["pop", "funk", "house", "disco", "lofi", "chill"][sum(map(ord, slug)) % 6],
                       "music_seed": sum(map(ord, slug)) % 97, "phrases": phrases}]}
    cj = ROOT / "videos" / f"{slug}.json"
    cj.write_text(json.dumps(cfg, ensure_ascii=False, indent=1))
    # voicevideo crea videos/<slug>/ junto a su json: el json va en videos/
    subprocess.run([sys.executable, str(ROOT / "generator/voicevideo.py"), str(cj), str(wav)], check=True)
    wav.unlink()
    print(d / "video.mp4")


if __name__ == "__main__":
    main(sys.argv[1:])
