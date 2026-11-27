# (anclaje: primeras palabras dichas, texto en pantalla, escena o None)
SALON = [["Corte mujer", "18 €", "45 min"], ["Color", "35 €", "90 min"], ["Balayage", "60 €", "2 h 30"]]
WEB = lambda day, pick, time: {"type": "web", "biz": "Salón Lucía", "url": "salonlucia.citasweb.es", "day": day, "pick": pick, "time": time, "services": SALON}
D = {
1: ("La agenda *al 35 %*", [
  ("esta es", "Esta es *Lucía*. Peluquera, con su propio salón", None),
  ("y la", "Y la agenda… *al 35 %*", {"type": "agenda", "title": "Agenda", "sub": "Martes", "sel": "M", "slots": [["10:00", "Libre", "free"], ["11:00", "Marta · Corte", "busy"], ["12:30", "Libre", "free"], ["16:00", "Libre", "free"], ["17:30", "Elena · Color", "busy"], ["19:00", "Libre", "free"]]}),
  ("y el", "Y el teléfono sonando con las manos *llenas de tinte*", {"type": "call", "name": "Número desconocido", "time": "11:24"}),
  ("durante", "*21 días* para llenar su agenda, paso a paso", None),
  ("síguenos", "Síguenos: *mañana empieza el reto*", None)]),
2: ("*6 llamadas* perdidas", [
  ("día 2", "Martes por la mañana. Lucía, *con unas mechas*", None),
  ("una dos", "Una, dos… *seis llamadas perdidas*", {"type": "notif", "clock": "11:40", "date": "martes, 1 de diciembre", "items": [["Teléfono", "6 llamadas perdidas", "Número desconocido y 5 más"]]}),
  ("cuando por", "Cuando devuelve las llamadas, *dos ya han reservado en otro sitio*", None),
  ("el problema", "El problema no es que no llamen. *Es que no puede contestar*", None)]),
3: ("Domingo, *22:14*", [
  ("día 3", "Domingo, 10 de la noche… *y contestando WhatsApps*", {"type": "chat", "name": "Clienta", "time": "22:14", "day": "DOMINGO", "msgs": [["in", "¿Tienes hueco el jueves?", "22:11"], ["in", "¿Cuánto cuesta el balayage?", "22:14"]], "gap": 1.0}),
  ("hoy toma", "Hoy decide *dejar de ser su propia recepcionista*", None),
  ("pero antes", "Pero antes, *que la encuentren*", None),
  ("mañana", "Mañana: *Google*", None)]),
4: ("Su *perfil de Google*", [
  ("día 4", "Cuando buscan *«peluquería cerca de mí»*… sale Google", {"type": "search", "query": "peluquería cerca de mí", "time": "19:40", "results": [["Peluquería Centro", "3 fotos · Horario sin actualizar", False], ["Salón Lucía", "Fotos nuevas · Servicios · Horario", True, 2.6], ["Estudio Nuria", "Web propia · Reserva online", True]]}),
  ("lucía revisa", "3 fotos viejas, horario mal y *ni un servicio*", None),
  ("lo arregla", "Lo arregla *en 20 minutos*", None),
  ("es gratis", "Es gratis. *Puedes hacerlo hoy*", None)]),
5: ("*Precios* a la vista", [
  ("día 5", "El mensaje que más recibe: *«¿cuánto cuesta?»*", {"type": "chat", "name": "Clienta", "time": "16:20", "msgs": [["in", "Hola, ¿cuánto cuesta un color?", "16:20"]], "seen": True}),
  ("y muchos", "Si no ven el precio, *ni preguntan: se van*", None),
  ("hoy pone", "Hoy pone sus precios *a la vista*", WEB("Viernes", 2, "16:25")),
  ("menos mensajes", "Menos mensajes y clientas que *llegan sabiendo lo que pagan*", None)]),
6: ("El *enlace* de la bio", [
  ("día 6", "En su Instagram ponía *«pide cita por WhatsApp»*", None),
  ("hoy cambia", "Hoy pone un enlace: *ve huecos y reserva sola*", WEB("Sábado", 3, "13:02")),
  ("ya no", "Ya no hace falta *escribirle*", None),
  ("y lo", "Y lo mejor llega *esta noche*", None)]),
7: ("Semana 1: *35 % → 48 %*", [
  ("día 7", "Una semana de reto", None),
  ("perfil de", "Google arreglado, *precios a la vista* y enlace para reservar", None),
  ("la agenda", "Del 35 % al *48 %*", None),
  ("una reserva", "Una reserva a las 23:30… *sin coger el móvil*", {"type": "notif", "clock": "23:31", "date": "sábado, 5 de diciembre", "items": [["CitasWeb", "Nueva reserva", "Martes 11:00 · Corte mujer"]]}),
  ("la semana", "Ahora, a por *los que se le escapan*", None)]),
8: ("La *respuesta automática*", [
  ("día 8", "Los WhatsApps siguen llegando, *y está bien*", None),
  ("pero ahora", "Cuando no puede contestar, *salta un mensaje automático*", {"type": "chat", "name": "Salón Lucía", "time": "15:03", "msgs": [["in", "Hola! ¿Tienes hueco mañana?", "15:02"], ["out", "Estoy con una clienta 💇‍♀️ Reserva aquí: salonlucia.citasweb.es", "15:02"]], "gap": 1.1}),
  ("quien escribe", "Quien escribe a las 3 *ya no espera hasta las 8*", None),
  ("mañana", "Mañana: lo que pasó *a medianoche*", None)]),
9: ("Reserva a las *23:47*", [
  ("día 9", "Miércoles, *23:47*", {"type": "notif", "clock": "23:47", "date": "miércoles, 9 de diciembre", "items": [["CitasWeb", "Reserva confirmada", "Viernes 10:00 · Corte y color"]]}),
  ("antes eso", "Antes: un mensaje *sin contestar hasta el día siguiente*", None),
  ("hoy es", "Hoy: *reserva confirmada*. Viernes a las 10", None),
  ("lucía lo", "Ella lo ve por la mañana, *con el café*", None),
  ("tu negocio", "Tu negocio cierra. *Tu agenda, no*", None)]),
10: ("Cada servicio, *su tiempo*", [
  ("día 10", "Un balayage *no ocupa lo mismo* que un corte", None),
  ("y cuando", "Apuntando a mano: *citas juntas o huecos muertos*", None),
  ("ahora cada", "Ahora cada servicio tiene *su duración real*", {"type": "agenda", "title": "Agenda", "sub": "Miércoles", "sel": "X", "slots": [["10:00", "Ana · Corte · 45 min", "busy"], ["10:45", "Rocío · Balayage · 2 h 30", "busy"], ["13:15", "Libre", "booked", 1.4, "✓ Reservado · Corte"], ["16:00", "Libre", "free"]]}),
  ("se acabaron", "Se acabaron *los días descuadrados*", None)]),
11: ("Adiós a los *plantones*", [
  ("día 11", "*3 plantones* a la semana", None),
  ("no era", "No es mala fe: *se les olvida*", None),
  ("hoy activa", "Hoy activa los *recordatorios automáticos*", {"type": "notif", "clock": "10:00", "date": "jueves, 10 de diciembre", "items": [["CitasWeb", "Recordatorio de tu cita", "Mañana a las 10:00 · Salón Lucía"], ["CitasWeb", "Cita confirmada ✓", "¡Te esperamos!"]], "gap": 1.0}),
  ("lo que", "Lo que más los reduce no es enfadarse. *Es recordar*", None)]),
12: ("Cancela… *y se rellena*", [
  ("día 12", "Una clienta *cancela la cita de las 5*", None),
  ("antes ese", "Antes, ese hueco *se quedaba vacío*", None),
  ("ahora al", "Ahora vuelve a estar libre… *y en 20 minutos lo reserva otra*", {"type": "agenda", "title": "Agenda", "sub": "Viernes", "sel": "V", "slots": [["16:00", "Pilar · Color", "busy"], ["17:00", "Cancelada", "noshow", 0.6, "✕ Cancelada"], ["17:00", "Libre", "booked", 1.8, "✓ Reservado · Corte"], ["18:30", "Lola · Peinado", "busy"]]}),
  ("lucía no", "Y Lucía *no ha hecho nada*", None)]),
13: ("Huecos de *última hora*", [
  ("día 13", "Siempre queda *algún hueco suelto*", None),
  ("lucía ha", "Sube una historia: *«Hueco hoy a las 12»*", WEB("Hoy", 2, "09:40")),
  ("quien lo", "Quien lo ve primero, *se lo queda*", None),
  ("sin llamadas", "Sin llamadas. *Sin «ya te digo algo»*", None)]),
14: ("Semana 2: *48 % → 72 %*", [
  ("día 14", "Dos semanas de reto", None),
  ("respuesta", "Respuesta automática, reservas 24 h *y recordatorios*", None),
  ("la agenda", "Agenda *al 72 %*", None),
  ("y hoy", "Es domingo… *y no ha contestado ni un mensaje*", None),
  ("la última", "Última semana: *que vuelvan*", None)]),
15: ("Las *reseñas*", [
  ("día 15", "¿Qué miras al elegir peluquería? *Las reseñas*", None),
  ("lucía tenía", "Clientas encantadas… *y casi ninguna reseña*", None),
  ("hoy empieza", "Ahora la pide *al terminar cada cita*", {"type": "chat", "name": "Marta", "time": "13:10", "msgs": [["out", "¡Gracias por venir, Marta! ¿Nos dejas tu opinión? ⭐", "13:09"], ["in", "¡Claro! Me encanta cómo ha quedado 😍", "13:10"]], "gap": 1.1}),
  ("sin presionar", "Sin presionar. *Solo pidiéndolo*", None)]),
16: ("Contestar *cada reseña*", [
  ("día 16", "Lucía contesta *todas sus reseñas*", None),
  ("las buenas", "Las buenas, con un gracias. *La regular, con calma*", None),
  ("quien lee", "Quien lo lee ve a alguien que *cuida a sus clientas*", None)]),
17: ("Que vuelvan *a tiempo*", [
  ("día 17", "Viene cada 6 semanas… *y a veces tarda 10*", None),
  ("ahora al", "Al terminar, *le deja reservada la siguiente*", {"type": "notif", "clock": "12:30", "date": "miércoles, 16 de diciembre", "items": [["CitasWeb", "Próxima cita reservada", "27 de enero · 10:00 · Color"]]}),
  ("las clientas", "Vuelven a tiempo y la agenda *se llena con semanas de antelación*", None)]),
18: ("La sorpresa de *doña Carmen*", [
  ("día 18", "Doña Carmen, *74 años*. Quince viniendo", None),
  ("lucía pensaba", "Lucía pensaba que *nunca reservaría por internet*", None),
  ("hoy le", "Hoy le llega *su reserva desde el móvil*", {"type": "notif", "clock": "17:05", "date": "jueves, 17 de diciembre", "items": [["CitasWeb", "Nueva reserva", "Carmen · Sábado 10:00 · Peinado"]]}),
  ("si es", "Si es fácil, *lo usa todo el mundo*", None)]),
19: ("Llenar el *día flojo*", [
  ("día 19", "El martes por la mañana era *el agujero de la semana*", None),
  ("hoy lo", "Lanza algo especial *solo para los martes*", WEB("Martes", 1, "20:10")),
  ("conocer", "Conocer tu día flojo es *la mitad del trabajo*", None)]),
20: ("*Móvil en silencio*", [
  ("día 20", "Cierra el sábado *a su hora*", None),
  ("pone el", "Móvil en silencio *y a cenar*", None),
  ("por primera", "Por primera vez en meses, *sin contestar a nadie*", None),
  ("las reservas", "Las reservas entran solas. *Los recordatorios salen solos*", {"type": "notif", "clock": "22:15", "date": "sábado, 19 de diciembre", "items": [["CitasWeb", "Nueva reserva", "Lunes 10:00 · Balayage"], ["CitasWeb", "Recordatorio enviado", "3 clientas de mañana"]], "gap": 0.9}),
  ("mañana es", "Mañana, *el último día*", None)]),
21: ("Fin del reto: *35 % → 90 %*", [
  ("día 21", "Fin del reto. *Del 35 % al 90 %*", None),
  ("no ha", "No es magia: *que te encuentren, que no se escapen y que vuelvan*", None),
  ("lucía es", "Lucía es inventada. *Los pasos son reales*", None),
  ("te dejamos", "Tu web y tu agenda *listas en 24-48 h*. 15 días gratis, sin tarjeta", WEB("Lunes", 1, "10:00"))]),
}
PCT = [35, 35, 35, 36, 38, 41, 44, 48, 51, 54, 57, 60, 64, 68, 72, 75, 77, 80, 83, 86, 88, 90]  # PCT[n] = día n, PCT[0] = inicio
