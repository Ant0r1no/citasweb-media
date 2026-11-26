#!/usr/bin/env python3
"""Publicador propio de Instagram para CitasWeb (sustituye a Metricool para Instagram).

Lee calendar/instagram.json, publica lo que toca con la API oficial de Instagram
(Instagram API with Instagram Login) y guarda el resultado en el mismo archivo.
Se ejecuta cada hora desde GitHub Actions (.github/workflows/instagram.yml).

Variables de entorno:
  IG_ACCESS_TOKEN  clave de acceso de larga duración (secreto de GitHub; nunca en el repo)
  DRY_RUN=1        no publica nada, solo muestra lo que haría
  ONLY_ID=<id>     publica solo esa entrada aunque no sea su hora (prueba manual)

Formato de cada entrada del calendario:
  {"id": "...", "when": "2026-12-02T10:00", "type": "REELS" | "CAROUSEL" | "IMAGE",
   "media": ["https://..."], "cover": "https://...jpg" | null, "caption": "...",
   "ai": false, "status": "pending"}
"when" es hora de Madrid. Tras publicar: status "published", ig_media_id, permalink, published_at.
Si falla: status "error" y "error" con el motivo (se reintenta hasta 3 veces en ejecuciones siguientes).
"""
import hashlib
import io
import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

ROOT = Path(__file__).resolve().parent.parent
CAL = ROOT / "calendar" / "instagram.json"
CACHE = ROOT / "calendar" / "cache"
STATUS = ROOT / "calendar" / "ESTADO.md"
TZ = ZoneInfo("Europe/Madrid")
API = "https://graph.instagram.com/v26.0"
RAW = "https://raw.githubusercontent.com/{repo}/main/"
MAX_LATE = timedelta(hours=12)   # si se pasa más de esto sin publicar, se marca "missed" y se avisa
MAX_TRIES = 3

TOKEN = os.environ.get("IG_ACCESS_TOKEN", "")
DRY = os.environ.get("DRY_RUN") == "1"
ONLY = os.environ.get("ONLY_ID") or None
REPO = os.environ.get("GITHUB_REPOSITORY", "Ant0r1no/citasweb-media")


class IGError(Exception):
    pass


def api(method, path, **params):
    params["access_token"] = TOKEN
    r = requests.request(method, f"{API}/{path}", params=params, timeout=60)
    try:
        data = r.json()
    except ValueError:
        raise IGError(f"HTTP {r.status_code}: respuesta no válida")
    if r.status_code >= 400 or "error" in data:
        err = data.get("error", {})
        raise IGError(f"{err.get('code', r.status_code)}: {err.get('message', r.text[:200])}")
    return data


def to_jpeg_url(url):
    """La API solo acepta JPEG para imágenes: convierte PNG/WebP y lo sirve desde el repo."""
    if url.lower().split("?")[0].endswith((".jpg", ".jpeg")):
        return url
    from PIL import Image
    name = hashlib.sha1(url.encode()).hexdigest()[:16] + ".jpg"
    out = CACHE / name
    if not out.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        im = Image.open(io.BytesIO(r.content)).convert("RGB")
        im.save(out, "JPEG", quality=92)
        commit_push([str(out)], f"Caché JPEG para Instagram ({name})")
        time.sleep(20)  # dar tiempo a raw.githubusercontent.com
    return RAW.format(repo=REPO) + f"calendar/cache/{name}"


def wait_ready(cid, timeout=600):
    t0 = time.time()
    while time.time() - t0 < timeout:
        st = api("GET", cid, fields="status_code,status").get("status_code")
        if st == "FINISHED":
            return
        if st in ("ERROR", "EXPIRED"):
            raise IGError(f"el contenedor terminó en {st}")
        time.sleep(10)
    raise IGError("el vídeo tardó demasiado en procesarse")


def publish(entry, uid):
    t = entry["type"].upper()
    cap = entry.get("caption", "")
    ai = "true" if entry.get("ai") else "false"
    media = entry["media"]
    if t == "REELS":
        p = dict(media_type="REELS", video_url=media[0], caption=cap, share_to_feed="true", is_ai_generated=ai)
        if entry.get("cover"):
            p["cover_url"] = to_jpeg_url(entry["cover"])
        cid = api("POST", f"{uid}/media", **p)["id"]
        wait_ready(cid)
    elif t == "IMAGE":
        cid = api("POST", f"{uid}/media", image_url=to_jpeg_url(media[0]), caption=cap, is_ai_generated=ai)["id"]
        wait_ready(cid, 120)
    elif t == "CAROUSEL":
        kids = []
        for m in media[:10]:
            if m.lower().split("?")[0].endswith((".mp4", ".mov")):
                k = api("POST", f"{uid}/media", media_type="VIDEO", video_url=m, is_carousel_item="true")["id"]
            else:
                k = api("POST", f"{uid}/media", image_url=to_jpeg_url(m), is_carousel_item="true")["id"]
            wait_ready(k)
            kids.append(k)
        cid = api("POST", f"{uid}/media", media_type="CAROUSEL", children=",".join(kids), caption=cap, is_ai_generated=ai)["id"]
        wait_ready(cid, 120)
    else:
        raise IGError(f"tipo desconocido: {t}")
    mid = api("POST", f"{uid}/media_publish", creation_id=cid)["id"]
    link = api("GET", mid, fields="permalink").get("permalink", "")
    return mid, link


def commit_push(paths, msg):
    if not os.environ.get("GITHUB_ACTIONS"):
        return
    os.system('git config user.name "citasweb-bot" && git config user.email "bot@users.noreply.github.com"')
    os.system("git add " + " ".join(f'"{p}"' for p in paths))
    os.system(f'git commit -q -m "{msg}" || true')
    for _ in range(3):
        if os.system("git pull -q --rebase origin main && git push -q origin main") == 0:
            return
        time.sleep(5)


def write_status(cal, now):
    up = [e for e in cal if e.get("status") in ("pending", "error")]
    up.sort(key=lambda e: e["when"])
    done = [e for e in cal if e.get("status") == "published"]
    done.sort(key=lambda e: e.get("published_at", ""), reverse=True)
    bad = [e for e in cal if e.get("status") in ("error", "missed")]
    L = ["# Estado del publicador de Instagram", "",
         f"Última revisión: {now:%d/%m/%Y %H:%M} (hora de Madrid)", "",
         f"- Pendientes: **{len(up)}** · Publicadas: **{len(done)}** · Con problemas: **{len(bad)}**", ""]
    if bad:
        L += ["## ⚠️ Con problemas", "", "| Fecha | Publicación | Motivo |", "|---|---|---|"]
        L += [f"| {e['when'].replace('T', ' ')} | {e['id']} | {e.get('error', e['status'])} |" for e in bad]
        L.append("")
    L += ["## Próximas", "", "| Fecha | Tipo | Publicación |", "|---|---|---|"]
    L += [f"| {e['when'].replace('T', ' ')} | {e['type']} | {e['id']} |" for e in up[:15]]
    L += ["", "## Últimas publicadas", "", "| Fecha | Publicación | Enlace |", "|---|---|---|"]
    L += [f"| {e.get('published_at', '')[:16].replace('T', ' ')} | {e['id']} | {e.get('permalink', '')} |" for e in done[:10]]
    STATUS.write_text("\n".join(L) + "\n", encoding="utf-8")


def main():
    cal = json.loads(CAL.read_text(encoding="utf-8"))
    now = datetime.now(TZ)
    due = []
    for e in cal:
        if ONLY:
            if e["id"] == ONLY:
                due.append(e)
            continue
        st = e.get("status", "pending")
        if st not in ("pending", "error") or e.get("tries", 0) >= MAX_TRIES:
            continue
        when = datetime.fromisoformat(e["when"]).replace(tzinfo=TZ)
        if when > now:
            continue
        if now - when > MAX_LATE and st == "pending":
            e["status"] = "missed"
            e["error"] = "no se publicó a tiempo (más de 12 h de retraso)"
            continue
        due.append(e)
    print(f"{now:%Y-%m-%d %H:%M} · {len(due)} publicación(es) por hacer")
    problems = []
    if due and not DRY:
        if not TOKEN:
            sys.exit("Falta el secreto IG_ACCESS_TOKEN")
        uid = api("GET", "me", fields="user_id,username")["user_id"]
    for e in due:
        print(f"→ {e['id']} ({e['type']}, {e['when']})")
        if DRY:
            continue
        try:
            mid, link = publish(e, uid)
            e.update(status="published", ig_media_id=mid, permalink=link,
                     published_at=datetime.now(TZ).isoformat(timespec="minutes"))
            e.pop("error", None)
            print(f"   publicada: {link}")
        except (IGError, requests.RequestException) as ex:
            e["tries"] = e.get("tries", 0) + 1
            e["status"] = "error"
            e["error"] = str(ex)[:300]
            problems.append(e)
            print(f"   ERROR: {ex}")
    for e in cal:
        if e.get("status") == "missed" and not e.get("notified"):
            problems.append(e)
            e["notified"] = True
    if not DRY:
        CAL.write_text(json.dumps(cal, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        write_status(cal, now)
        commit_push([str(CAL), str(STATUS)], "Publicador Instagram: estado actualizado")
    if problems:
        Path(os.environ.get("RUNNER_TEMP", "/tmp"), "ig_problems.md").write_text(
            "\n".join(f"- **{e['id']}** ({e['when']}): {e.get('error', e['status'])}" for e in problems), encoding="utf-8")


if __name__ == "__main__":
    main()
