# Rutina semanal de redes de CitasWeb

Este documento es el que sigue la tarea programada cada lunes. Si cambias algo de la estrategia, cámbialo aquí.

## Datos fijos
- Marca en Metricool: **citasweb.es**, blogId **7420076**, zona horaria **Europe/Madrid**.
- Redes: Instagram @citasweb.es y TikTok @citasweb.
- Web: https://citasweb.es/ (va en todos los textos).
- **Reparto de redes (desde la puesta en marcha del publicador propio):**
  - **TikTok → Metricool**, solo con `providers: [{"network":"tiktok"}]`. Plan gratis: **máximo 20 publicaciones publicadas al mes** (cada red cuenta por separado; los borradores no cuentan; lo que pase de 20 no se publica).
  - **Instagram → publicador propio** (`calendar/instagram.json`, ver `calendar/README.md`). Sin límite mensual práctico. Cada publicación nueva se añade al calendario con el mismo texto y medios (vídeo mp4 por URL raw de GitHub; imágenes en JPEG o se convierten solas), `ai` igual que la etiqueta de IA, y se hace commit + push.
  - **Facebook (página CitasWeb, id 61597065477463) → el mismo publicador**: cada entrada de `calendar/instagram.json` desde el 01/12/2026 sale también en la página. Para excluir una, `"facebook": false`. Necesita el secreto de GitHub `FB_PAGE_TOKEN` (clave de la página); mientras no exista, Facebook se salta sin error. No tocar el ajuste "Publicador Instagram" de la app: si se le añaden páginas deja de ser compatible con la API de Instagram.
- **Ritmo (decisión del dueño, 27/11/2026):**
  - **Instagram y Facebook: una publicación TODOS los días**, sin huecos (no tienen límite).
  - **TikTok: hasta 20 al mes** (límite de Metricool), solo en los mejores días y horas.
- **Mejores horas** (Metricool, noviembre 2026):
  - Instagram (y Facebook, que va con él): **10:00 todos los días** (lo mejor, de miércoles a viernes). Si ese día ya hay algo a las 10:00, usar las **18:00** (fuerte de martes a jueves). Fin de semana: 10:00.
  - TikTok: **de lunes a viernes, 10:00 o 18:00**; los mejores, **miércoles y jueves**. Evitar sábado y domingo salvo que no quede otra. 20 al mes ≈ 5 por semana.

## Pasos de cada ejecución
1. **Clonar este repositorio** (`Ant0r1no/citasweb-media`) e instalar lo necesario si falta (`playwright`).
2. **Métricas de los últimos 7 días** en Metricool:
   - Instagram, conector `evolution`: IGEV01 (seguidores), IGEV37 (contenido), IGEV23 (vistas de reels), IGEV06 (alcance), IGEV38 (interacciones), IGEV43 (seguidores ganados).
   - TikTok, conector `posts`: TKPO01, TKPO05, TKPO07 (vistas), TKPO08 (likes), TKPO13 (vídeo completo), TKPO15 (tiempo medio).
   - Señalar la publicación que mejor ha funcionado y la que peor, y si el estilo nuevo (desde el 14 de diciembre de 2026) supera al antiguo.
   - **A partir del 15 de enero de 2027**, en la primera ejecución: comparar el estilo antiguo (de octubre al 13 de diciembre) con el nuevo.
3. **Revisar el calendario** de las próximas 6 semanas: `calendar/instagram.json` (Instagram y Facebook) y `getScheduledPosts` (TikTok). Apuntar los días sin publicación en Instagram/Facebook y cuántas lleva TikTok en cada mes natural.
4. **Blog → redes:** seguir la sección "Blog → redes" de más abajo, que va antes de los carruseles genéricos.
5. **Rellenar los huecos** (prioridad: los más cercanos):
   - **Instagram + Facebook:** dejar cubiertos **todos los días de las próximas 3 semanas** (hasta 21 vídeos por ejecución si hace falta), a las mejores horas de arriba.
   - **TikTok:** con esos mismos vídeos, completar cada mes hasta **20, nunca más**, en los mejores huecos (lunes a viernes, 10:00/18:00, primero miércoles y jueves).
   - Alternar sectores y formatos; si un día ya tiene una serie de voz, no hace falta otro.
   - Revisar también `calendar/ESTADO.md` y avisar en el informe si hay publicaciones con problemas.
   - Huecos apuntados el 27/11/2026: Instagram/Facebook 7 en diciembre, 11 en enero, 18 en febrero, 23 en marzo y 30 en abril; TikTok libre: 1 en enero, 10 en febrero, 11 en marzo, 0 en abril.
6. **Crear cada carrusel:**
   - Crear `posts/AAAA-MM-DD-tema/post.json`; el formato está en `generator/render.py`. Son 5 o 6 diapositivas: portada con gancho, desarrollo y CTA con la palabra clave.
   - **Se publica como mini vídeo, no como fotos** (decisión del dueño, 27/11/2026): ejecutar `python3 generator/slideshow.py posts/.../post.json` → crea `video.mp4` (vertical, animado, con música y efectos) y `cover.jpg`. Revisar unos fotogramas y hacer commit y push a `main`.
   - Cada vídeo sale con transición, animación de texto, fondo, barra y música distintos del anterior (se elige solo y se apunta en `posts/_estilos.json`; no borrar ese archivo). No forzar el mismo estilo en dos seguidos.
   - En el texto no poner "Desliza": es un vídeo.
   - Instagram + Facebook: añadir la entrada a `calendar/instagram.json` con `type: "REELS"`, `media: [.../video.mp4]` y `cover: .../cover.jpg`.
   - TikTok: `createScheduledPost` solo con tiktok, el mismo `video.mp4` como medio, `videoThumbnailUrl` con la portada y `commercialContentOwnBrand: true`.
7. **Informe final:** recordatorio del artículo que toca publicar esa semana, métricas, qué ha funcionado, qué se ha programado (fecha, tema y enlace de Metricool) y el recuento por mes. Enviarlo con PushNotification si está disponible y dejarlo también como resultado de la ejecución.

## Estilo de los textos (el nuevo)
- Gancho corto en la primera línea, 3 o 4 líneas en total.
- Formato: `💬 Comenta "PALABRA" y te enseño cómo quedaría la tuya`, luego `👉 https://citasweb.es/` y **5 hashtags** como máximo.
- No es un anuncio. Debe aportar algo: humor del día a día del sector, una cuenta de dinero perdido, un truco práctico (Google Maps, reseñas, recordatorios) o una lista de "tipos de clientes".
- No inventar testimonios, clientes, cifras de estudios ni historias en primera persona ("he visitado…"). Las cuentas tienen que ser hipotéticas y presentarse como tales.
- Ir alternando sectores y no repetir dos seguidos ni el mismo sector que el post anterior del calendario.
- Palabras clave por sector: BARBER, PELU, MESA, RESTAURANTE, CARTA, GOURMET, TALLER, FISIO, DENTAL, BEAUTY, LIMPIEZA, SERVICIOS, VET, CITA, CLASE, ENTRENO, NUTRI, TATTOO, RELAX.
- Sectores del generador (colores): general, barberia, peluqueria, estetica, restaurante, taller, fisio, dental, limpieza, vet, fitness.

## Etiqueta de IA
- Todo vídeo con voz sintética (generada aquí) va con `instagramData.isAiGenerated: true` y `tiktokData.isAigc: true`. Los reels programados hasta febrero de 2027 ya están marcados.
- No usar voces de ElevenLabs del plan gratis: no permite uso comercial.

## Qué no hacer
- No borrar ni editar publicaciones que ya existen. No tocar los borradores de la serie "Día X".
- No pasar de 20 publicaciones al mes en TikTok (Metricool).
- No subir nada que no sean imágenes de las publicaciones.

## Blog de citasweb.es (panel: citasweb.es/admin → Blog)
- Los artículos se guardan siempre como **borrador**. Los publica el dueño, salvo que pida lo contrario.
- **Dirección (URL):** el panel la genera a partir del título y la corta a unos 70 caracteres. Hay que escribirla a mano: corta, sin tildes, con la palabra clave (p. ej. `cita-previa-online-talleres-mecanicos`).
- Cada artículo lleva portada de 1200x630, hecha con `generator/cover.py` (las de ejemplo están en `blog/`).
- El texto va en markdown (`##` para títulos, `**negrita**`, `- ` para listas y `[texto](url)` para enlaces) y termina con el enlace "Pruébala gratis en citasweb.es".
- No inventar testimonios ni cifras. Precios: 50/60/80 €/mes + IVA, o 500/600/800 €/año (2 meses gratis). Prueba de 15 días sin tarjeta. Lista en 24-48 h. Web en tunegocio.citasweb.es; dominio propio a consultar.

## Blog → redes (dentro de la rutina de cada lunes)
El blog **lo publica el dueño** a mano, desde su panel. Claude no publica en la web.
1. **Recordatorio:** en el informe del lunes, indicar qué borrador toca publicar esa semana, siguiendo este orden (saltar los que ya estén publicados en citasweb.es/blog):
   1. Caso real: Nexus Barber Studio (/blog/caso-real-nexus-barber-studio-murcia)
   2. Cómo reducir los clientes que no se presentan (/blog/reducir-clientes-que-no-se-presentan)
   3. Reservas de mesa online (/blog/reservas-de-mesa-online-bares-restaurantes)
   4. Cita previa para talleres (/blog/cita-previa-online-talleres-mecanicos)
   5. Cómo salir en Google Maps (/blog/como-salir-en-google-maps-negocio-local)
   6. Agenda online para clínicas (/blog/agenda-online-clinicas-consultas)
   7. Estética y uñas (/blog/reservas-online-centros-estetica-unas)
   8. WhatsApp o agenda online (/blog/whatsapp-o-agenda-online-citas)
   9. Web propia o plataforma (/blog/web-propia-o-plataforma-de-reservas)
2. **Detectar artículos publicados:** leer https://citasweb.es/sitemap.xml (con WebFetch) y compararlo con `blog/promocionados.txt`.
3. **Promoción:** por cada artículo publicado que no esté promocionado, crear un carrusel (5-6 diapositivas) con lo mejor del artículo, terminando en "en el blog · citasweb.es/blog · enlace en la bio". Programarlo en la **primera mejor hora libre**, aunque sea en un mes posterior, sin pasar nunca de 20 al mes. Los carruseles del blog tienen **prioridad** sobre los carruseles genéricos. Después, añadir la línea correspondiente a `blog/promocionados.txt` y hacer commit.
4. Si se acaban los borradores, avisar en el informe y proponer al dueño 3 temas nuevos.
- **No publicar la valoración "4,9" de la web de Nexus Barber:** no viene de Google.

## Vídeos con la voz del dueño
- El dueño graba todos los guiones seguidos ("Vídeo uno… [guion]", con una pausa entre cada uno) y manda el audio por el chat.
- Se transcribe con faster-whisper (modelo small; hay que pasarle el audio como muestras de 16 kHz porque la librería av falla con mp3), se crea `videos/<serie>.json` con los tiempos de cada frase (sin incluir el "Vídeo uno" del principio) y se ejecuta `python3 generator/voicevideo.py videos/<serie>.json <audio>`.
- Música de fondo: siempre. `voicevideo.py` genera una base musical ORIGINAL con `generator/music.py` (sin derechos de terceros, así no la silencian en Instagram ni TikTok) y la mezcla bajo la voz con "ducking" (baja sola cuando se habla). En el JSON: `"music": {"styles": ["house","pop","lofi"], "volume": 0.6}` (se alterna un estilo por vídeo; 0.6 es el nivel aprobado: la música se nota y la voz se entiende) y `"outname": "video-vN.mp4"` (nombre nuevo en cada versión).
- Escenas de móvil y efectos de sonido: siempre (herramienta propia, gratis). Cada frase puede llevar como 3er elemento una escena de `generator/scenes.py`: `call` (llamada entrante que vibra), `callon` (llamada en curso), `chat` (mensajes que llegan), `notif` (pantalla de bloqueo con notificaciones), `agenda` (huecos libres/pendientes/reservados/plantón), `web` (reserva en la web con «¡Reserva confirmada!») y `money` (contador de dinero perdido). Ver ejemplos en `videos/tipos.json`. Los efectos de sonido (`generator/sfx.py`: timbre, ping, toque, ding, transición…) se colocan solos sincronizados con cada escena. El gancho se ve grande desde el fotograma 0. Al menos la mitad de las frases deberían llevar escena.
- Animación: siempre. `voicevideo.py` anima cada fotograma (palabras que aparecen al ritmo de la voz, resaltado que se pinta, fondo en movimiento que late con la música, número grande de la serie, botón final que late). Tarda ~1,5 min por vídeo; se pueden lanzar varios en paralelo pasando el slug como 3er argumento. Para cambiar un vídeo ya programado hay que subirlo con un NOMBRE NUEVO y actualizar el post en Metricool (Metricool copia el archivo al programar). En TikTok, `autoAddMusic` en false para los vídeos que ya llevan música.
- Se programan como REEL (Instagram) y vídeo (TikTok), con `videoThumbnailUrl` apuntando a cover.jpg. Si la voz es suya, `isAiGenerated: false`.
- Programados: Tipos de clientes #1 (5 ene 18:00), #2 (4 feb 18:00), #3 (8 feb 18:00), #4 (11 feb 18:00).
