#!/usr/bin/env python3
"""Convierte las diapositivas verticales de un post en un vídeo (reel/TikTok).

Uso: python3 generator/video.py posts/<carpeta> [segundos_por_diapositiva]
Usa slide-N.png (1080x1920) y crea video.mp4 con transiciones suaves y zoom lento.
"""
import glob
import subprocess
import sys
from pathlib import Path

folder = Path(sys.argv[1])
dur = float(sys.argv[2]) if len(sys.argv) > 2 else 3.2
slides = sorted(glob.glob(str(folder / "slide-*.png")), key=lambda x: int(x.split("-")[-1].split(".")[0]))
fade = 0.4
inputs, filters = [], []
for i, s in enumerate(slides):
    inputs += ["-i", s]
    frames = int(dur * 30)
    filters.append(
        f"[{i}:v]scale=1188:2112,zoompan=z='min(zoom+0.0006,1.06)':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30,format=yuv420p,setsar=1[v{i}]"
    )
chain, last, offset = "", "v0", 0.0
for i in range(1, len(slides)):
    offset += dur - fade
    out = f"x{i}"
    chain += f";[{last}][v{i}]xfade=transition=slideleft:duration={fade}:offset={offset:.2f}[{out}]"
    last = out
fc = ";".join(filters) + chain
cmd = ["ffmpeg", "-y", *inputs, "-filter_complex", fc, "-map", f"[{last}]", "-c:v", "libx264",
       "-preset", "veryfast", "-crf", "22", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(folder / "video.mp4")]
subprocess.run(cmd, check=True, capture_output=True)
print(folder / "video.mp4")
