# Calendario de Instagram

Instagram se publica con nuestro propio publicador (no con Metricool). TikTok sigue en Metricool.

- `instagram.json`: la lista de publicaciones. Cada una: `id`, `when` (hora de Madrid, `AAAA-MM-DDTHH:MM`),
  `type` (`REELS`, `CAROUSEL` o `IMAGE`), `media` (URLs públicas), `cover` (portada del reel, opcional),
  `caption`, `ai` (etiqueta de IA) y `status` (`pending` → `published` / `error` / `missed`).
- `ESTADO.md`: resumen que actualiza el publicador cada hora (próximas, publicadas y problemas).
- `cache/`: imágenes convertidas a JPEG (la API de Instagram solo acepta JPEG).

El publicador (`publisher/ig_publish.py`) se ejecuta cada hora en GitHub Actions. Si algo falla, abre una
incidencia (Issue) en el repositorio y GitHub te avisa por correo. La clave se guarda como secreto
`IG_ACCESS_TOKEN` en GitHub; nunca en este repositorio.
