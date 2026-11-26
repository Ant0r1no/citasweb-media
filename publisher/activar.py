#!/usr/bin/env python3
"""Activa las publicaciones en espera ("hold") del calendario de Instagram a partir de una fecha.

Uso: python3 publisher/activar.py 2026-12-01
Las anteriores a esa fecha se quedan en "hold" (no se publican).
"""
import json
import sys
from pathlib import Path

CAL = Path(__file__).resolve().parent.parent / "calendar" / "instagram.json"
desde = sys.argv[1]
cal = json.loads(CAL.read_text(encoding="utf-8"))
n = 0
for e in cal:
    if e.get("status") == "hold" and e["when"][:10] >= desde:
        e["status"] = "pending"
        n += 1
CAL.write_text(json.dumps(cal, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(f"{n} publicaciones activadas desde {desde}")
