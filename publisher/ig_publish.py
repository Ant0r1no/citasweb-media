#!/usr/bin/env python3
"""Publicador propio de Instagram y Facebook para CitasWeb (sustituye a Metricool para estas redes).

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

Facebook: cada entrada se publica también en la página CitasWeb (campos fb_status, fb_post_id,
fb_permalink). Pon "facebook": false en una entrada para que no salga en Facebook.
La clave de la página se saca de IG_ACCESS_TOKEN si se generó con los permisos de páginas.
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
HOSTS = ["https://graph.instagram.com/v26.0", "https://graph.facebook.com/v26.0"]
API = HOSTS[0]
IG_USER_ID = os.environ.get("IG_USER_ID", "17841421655402110")  # @citasweb.es (no es secreto)
RAW = "https://raw.githubusercontent.com/{repo}/main/"
MAX_LATE = timedelta(hours=12)   # si se pasa más de esto sin publicar, se marca "missed" y se avisa
MAX_TRIES = 3
FB_API = "https://graph.facebook.com/v26.0"
FB_PAGE_ID = os.environ.get("FB_PAGE_ID", "").strip()   # vacío = se detecta la página "CitasWeb"
FB_FROM = os.environ.get("FB_FROM", "2026-12-01")        # en Facebook solo se publica desde esta fecha

TOKEN = os.environ.get("IG_ACCESS_TOKEN", "").strip()
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


def publish(entry, uid, validate=False):
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
    if validate:
        return cid, "validado (contenedor listo, sin publicar)"
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


def connect():
    """Detecta qué servidor acepta la clave (inicio de sesión de Instagram o identificador de sistema de Meta)."""
    global API
    errors = []
    for host in HOSTS:
        API = host
        try:
            if "instagram" in host:
                me = api("GET", "me", fields="user_id,username")
                return me["user_id"], me.get("username")
            me = api("GET", IG_USER_ID, fields="id,username")
            return me["id"], me.get("username")
        except (IGError, requests.RequestException) as ex:
            errors.append(f"{host.split('/')[2]}: {ex}")
    raise IGError(" | ".join(errors))


def account():
    """Comprueba la conexión con Instagram (sin publicar nada)."""
    if not TOKEN:
        return "⚪ Sin conectar (falta el secreto IG_ACCESS_TOKEN)"
    try:
        _, user = connect()
        return f"🟢 Conectado como @{user} ({API.split('/')[2]})"
    except (IGError, requests.RequestException) as ex:
        return f"🔴 La clave no funciona: {str(ex)[:150]}"


def write_status(cal, now, acc=""):
    up = [e for e in cal if e.get("status") in ("pending", "error")]
    up.sort(key=lambda e: e["when"])
    done = [e for e in cal if e.get("status") == "published"]
    done.sort(key=lambda e: e.get("published_at", ""), reverse=True)
    bad = [e for e in cal if e.get("status") in ("error", "missed")]
    L = ["# Estado del publicador (Instagram y Facebook)", "",
         f"Última revisión: {now:%d/%m/%Y %H:%M} (hora de Madrid)", "", f"Cuenta: {acc}", "",
         f"En espera de activar: **{sum(1 for e in cal if e.get('status') == 'hold')}**", "",
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



# ───────────────────────── Facebook (página CitasWeb) ─────────────────────────
class FB:
    """Publica las mismas entradas en la página de Facebook con la clave de la página,
    que se obtiene en cada ejecución a partir de IG_ACCESS_TOKEN (no hay que guardar otra)."""

    def __init__(self):
        self.page = None
        self.token = None
        self.name = None
        self.why = ""

    def call(self, method, path, token=None, **params):
        params["access_token"] = token or self.token
        r = requests.request(method, f"{FB_API}/{path}", data=params if method == "POST" else None,
                             params=None if method == "POST" else params, timeout=120)
        try:
            data = r.json()
        except ValueError:
            raise IGError(f"HTTP {r.status_code}: respuesta no válida")
        if r.status_code >= 400 or "error" in data:
            err = data.get("error", {})
            raise IGError(f"{err.get('code', r.status_code)}: {err.get('message', r.text[:200])}")
        return data

    def connect(self):
        if not TOKEN:
            self.why = "falta IG_ACCESS_TOKEN"
            return False
        try:
            if FB_PAGE_ID:
                d = self.call("GET", FB_PAGE_ID, token=TOKEN, fields="id,name,access_token")
                pages = [d]
            else:
                pages = self.call("GET", "me/accounts", token=TOKEN, fields="id,name,access_token").get("data", [])
                pages = [p for p in pages if "citasweb" in p.get("name", "").lower()] or pages
            if not pages or not pages[0].get("access_token"):
                self.why = "la clave no tiene acceso a la página (hay que regenerarla con permisos de páginas)"
                return False
            self.page, self.name, self.token = pages[0]["id"], pages[0]["name"], pages[0]["access_token"]
            return True
        except (IGError, requests.RequestException) as ex:
            self.why = str(ex)[:150]
            return False

    def publish(self, entry):
        t = entry["type"].upper()
        cap = entry.get("caption", "")
        media = entry["media"]
        vids = [m for m in media if m.lower().split("?")[0].endswith((".mp4", ".mov"))]
        imgs = [m for m in media if m not in vids]
        if t == "REELS" or (t == "CAROUSEL" and not imgs):
            d = self.call("POST", f"{self.page}/videos", file_url=vids[0] if vids else media[0], description=cap)
            pid = d.get("id")
        elif t == "IMAGE" or len(imgs) == 1:
            d = self.call("POST", f"{self.page}/photos", url=to_jpeg_url(imgs[0]), message=cap)
            pid = d.get("post_id") or d.get("id")
        else:
            ids = [self.call("POST", f"{self.page}/photos", url=to_jpeg_url(m), published="false")["id"]
                   for m in imgs[:10]]
            att = {f"attached_media[{i}]": json.dumps({"media_fbid": x}) for i, x in enumerate(ids)}
            pid = self.call("POST", f"{self.page}/feed", message=cap, **att)["id"]
        return pid, f"https://www.facebook.com/{pid}"


def fb_due(cal, now):
    out = []
    for e in cal:
        if e["when"][:10] < FB_FROM or e.get("facebook") is False:
            continue
        if ONLY:
            if e["id"] == ONLY:
                out.append(e)
            continue
        if e.get("status") == "hold":
            continue
        st = e.get("fb_status", "pending")
        if st not in ("pending", "error") or e.get("fb_tries", 0) >= MAX_TRIES:
            continue
        when = datetime.fromisoformat(e["when"]).replace(tzinfo=TZ)
        if when > now:
            continue
        if now - when > MAX_LATE and st == "pending":
            e["fb_status"] = "missed"
            continue
        out.append(e)
    return out


def run_facebook(cal, now, problems):
    """Devuelve la línea de estado de Facebook para ESTADO.md."""
    fb = FB()
    if not fb.connect():
        return f"⚪ Facebook sin conectar: {fb.why}"
    due = fb_due(cal, now)
    print(f"Facebook ({fb.name}) · {len(due)} publicación(es) por hacer")
    for e in due:
        print(f"→ FB {e['id']}")
        if DRY:
            continue
        try:
            pid, link = fb.publish(e)
            e.update(fb_status="published", fb_post_id=pid, fb_permalink=link,
                     fb_published_at=datetime.now(TZ).isoformat(timespec="minutes"))
            e.pop("fb_error", None)
        except (IGError, requests.RequestException) as ex:
            e["fb_tries"] = e.get("fb_tries", 0) + 1
            e["fb_status"] = "error"
            e["fb_error"] = str(ex)[:300]
            problems.append({"id": "FB " + e["id"], "when": e["when"], "error": e["fb_error"]})
            print(f"   ERROR FB: {ex}")
    n = sum(1 for e in cal if e.get("fb_status") == "published")
    return f"🟢 Facebook conectado: página {fb.name} · publicadas allí: {n}"


VALIDATE = ROOT / "calendar" / "validar.txt"


def validate(cal):
    """Prueba sin publicar: crea el contenedor de las entradas listadas en calendar/validar.txt."""
    ids = [l.strip() for l in VALIDATE.read_text().splitlines() if l.strip()]
    uid, _ = connect()
    out = []
    for e in cal:
        if e["id"] in ids:
            try:
                _, msg = publish(e, uid, validate=True)
                out.append(f"- ✅ {e['id']}: {msg}")
            except (IGError, requests.RequestException) as ex:
                out.append(f"- ❌ {e['id']}: {ex}")
    VALIDATE.unlink()
    return "\n".join(out)


def main():
    cal = json.loads(CAL.read_text(encoding="utf-8"))
    now = datetime.now(TZ)
    vres = validate(cal) if VALIDATE.exists() and TOKEN and not DRY else ""
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
        uid, _ = connect()
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
    fbline = run_facebook(cal, now, problems) if not DRY or TOKEN else ""
    for e in cal:
        if e.get("status") == "missed" and not e.get("notified"):
            problems.append(e)
            e["notified"] = True
    if not DRY:
        CAL.write_text(json.dumps(cal, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        write_status(cal, now, account() + ("  \nFacebook: " + fbline if fbline else ""))
        if vres:
            STATUS.write_text(STATUS.read_text(encoding="utf-8") + "\n## Prueba sin publicar\n\n" + vres + "\n", encoding="utf-8")
        commit_push([str(CAL), str(STATUS), str(VALIDATE)], "Publicador Instagram: estado actualizado")
    if problems:
        Path(os.environ.get("RUNNER_TEMP", "/tmp"), "ig_problems.md").write_text(
            "\n".join(f"- **{e['id']}** ({e['when']}): {e.get('error', e['status'])}" for e in problems), encoding="utf-8")


if __name__ == "__main__":
    main()
