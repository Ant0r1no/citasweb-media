# Rutina semanal de redes de CitasWeb

Este documento es el que sigue la tarea programada cada lunes. Si cambias algo de la estrategia, cámbialo aquí.

## Datos fijos
- Marca en Metricool: **citasweb.es**, blogId **7420076**, zona horaria **Europe/Madrid**.
- Redes: Instagram @citasweb.es y TikTok @citasweb.
- Web: https://citasweb.es/ (va en todos los textos).
- Plan gratis de Metricool: **máximo 20 publicaciones al mes**, tanto si van a una red como a dos. Los borradores (`draft: true`) no cuentan.
- Mejores horas: **lunes 18:00, miércoles 10:00, jueves 18:00, viernes 10:00**.

## Pasos de cada ejecución
1. **Clonar este repositorio** (`Ant0r1no/citasweb-media`) e instalar lo necesario si falta (`playwright`).
2. **Métricas de los últimos 7 días** en Metricool:
   - Instagram, conector `evolution`: IGEV01 (seguidores), IGEV37 (contenido), IGEV23 (vistas de reels), IGEV06 (alcance), IGEV38 (interacciones), IGEV43 (seguidores ganados).
   - TikTok, conector `posts`: TKPO01, TKPO05, TKPO07 (vistas), TKPO08 (likes), TKPO13 (vídeo completo), TKPO15 (tiempo medio).
   - Señalar la publicación que mejor ha funcionado y la que peor, y si el estilo nuevo (desde el 14 de diciembre de 2026) supera al antiguo.
   - **A partir del 15 de enero de 2027**, en la primera ejecución: comparar el estilo antiguo (de octubre al 13 de diciembre) con el nuevo.
3. **Revisar el calendario** de las próximas 6 semanas con `getScheduledPosts`. Contar las publicaciones que no son borrador en cada mes natural.
4. **Rellenar los huecos.** Solo en meses con menos de 20, y en las mejores horas que estén libres, se crean carruseles nuevos. Como mucho **4 por ejecución**. Nunca hay que pasar de 20 en un mes.
5. **Crear cada carrusel:**
   - Crear `posts/AAAA-MM-DD-tema/post.json`; el formato está en `generator/render.py`. Son 5 o 6 diapositivas: portada con gancho, desarrollo y CTA con la palabra clave.
   - Ejecutar `python3 generator/render.py posts/.../post.json`, revisar las imágenes y hacer commit y push a `main`.
   - Las URL de los medios son `https://raw.githubusercontent.com/Ant0r1no/citasweb-media/main/posts/<carpeta>/slide-N.png`.
   - Programarlo con `createScheduledPost`: proveedores instagram (POST) y tiktok (`autoAddMusic: true`), `commercialContentOwnBrand: true` y texto alternativo en cada imagen.
6. **Informe final:** métricas, qué ha funcionado, qué se ha programado (fecha, tema y enlace de Metricool) y el recuento por mes. Enviarlo con PushNotification si está disponible y dejarlo también como resultado de la ejecución.

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
- No pasar de 20 publicaciones al mes.
- No subir nada que no sean imágenes de las publicaciones.

## Blog de citasweb.es (panel: citasweb.es/admin → Blog)
- Los artículos se guardan siempre como **borrador**. Los publica el dueño, salvo que pida lo contrario.
- **Dirección (URL):** el panel la genera a partir del título y la corta a unos 70 caracteres. Hay que escribirla a mano: corta, sin tildes, con la palabra clave (p. ej. `cita-previa-online-talleres-mecanicos`).
- Cada artículo lleva portada de 1200x630, hecha con `generator/cover.py` (las de ejemplo están en `blog/`).
- El texto va en markdown (`##` para títulos, `**negrita**`, `- ` para listas y `[texto](url)` para enlaces) y termina con el enlace "Pruébala gratis en citasweb.es".
- No inventar testimonios ni cifras. Precios: 50/60/80 €/mes + IVA, o 500/600/800 €/año (2 meses gratis). Prueba de 15 días sin tarjeta. Lista en 24-48 h. Web en tunegocio.citasweb.es; dominio propio a consultar.
