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

## Puesta en marcha (cambio de Metricool al publicador propio)

Estado actual: las 58 publicaciones de Instagram de diciembre a marzo están en el calendario con
`status: "hold"` (en espera). Mientras tanto, Metricool sigue publicando en Instagram y TikTok.

Pasos cuando el usuario guarde el secreto `IG_ACCESS_TOKEN`:

1. Esperar a la siguiente ejecución horaria (o lanzar a mano "Publicar en Instagram" con *dry_run*) y comprobar
   en `ESTADO.md` que pone **🟢 Conectado como @citasweb.es**.
2. Elegir la fecha de corte (el primer día sin publicaciones ya hechas por Metricool en Instagram) y ejecutar
   `python3 publisher/activar.py AAAA-MM-DD`, commit y push.
3. En Metricool, para cada publicación desde esa fecha: dejar solo `providers: [{"network":"tiktok"}]` y quitar
   `instagramData` (updateScheduledPost con el contenido completo).
4. Diciembre tiene 25 publicaciones en TikTok (límite 20): pasar a borrador las 5 publicaciones de foto solo-TikTok
   del 1 al 5 de diciembre (las de vídeo rinden más). Enero (20), febrero (10) y marzo (8) ya caben.
5. Actualizar el PLAYBOOK quitando la frase "Hasta que el publicador esté probado…".

Si el 1 de diciembre aún no hay clave: plan B = dejar cada mes en ~10 publicaciones a dos redes en Metricool y pasar
el resto a borrador (cuenta doble: 1 post en Instagram + TikTok = 2 del límite de 20).
