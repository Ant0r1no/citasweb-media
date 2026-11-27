T = {
1: "Esta es Lucía: peluquera, con su propio salón y la agenda al 35 %. Durante 21 días vamos a llenarla, paso a paso.",
2: "Seis llamadas perdidas en una mañana. Dos ya han reservado en otro sitio. El problema no es que no llamen…",
3: "Domingo, 22:14, y Lucía sigue contestando WhatsApps. Hoy toma una decisión.",
4: "Primer paso, y gratis: arreglar su perfil de Google. 20 minutos. ¿Cómo está el tuyo?",
5: "«¿Cuánto cuesta?» es el mensaje que más recibe. Hoy pone sus precios a la vista.",
6: "Cambia el «pide cita por WhatsApp» de su Instagram por un enlace para reservar sola.",
7: "Balance de la semana 1: del 35 % al 48 %. Y una reserva a las 23:30 sin coger el móvil.",
8: "Cuando no puede contestar, salta un mensaje automático con su enlace de reservas.",
9: "Miércoles, 23:47: antes era un mensaje sin contestar. Hoy, una reserva confirmada.",
10: "Un balayage no ocupa lo mismo que un corte. Cada servicio, con su duración real.",
11: "Tres plantones a la semana. Lo que más los reduce no es enfadarse: es recordar.",
12: "Una clienta cancela… y en 20 minutos otra persona reserva ese hueco.",
13: "El truco para los huecos de última hora: una historia y el enlace para reservar.",
14: "Balance de la semana 2: agenda al 72 %. Y es domingo sin contestar ni un mensaje.",
15: "Clientas encantadas y casi ninguna reseña. Hoy empieza a pedirlas.",
16: "Contestar cada reseña: las buenas con un gracias, la regular con calma.",
17: "Que vuelvan a tiempo: al terminar, la siguiente cita ya queda reservada.",
18: "Doña Carmen, 74 años, acaba de reservar desde el móvil.",
19: "Cómo llenar el día más flojo de la semana.",
20: "Sábado, móvil en silencio y a cenar. Las reservas entran solas.",
21: "Fin del reto: del 35 % al 90 %. Lucía es inventada; los pasos, reales. ¿Hacemos el tuyo?",
}
def caption(n):
    head = f"La agenda de Lucía · Día {n}/21 💇‍♀️"
    tail = ('💬 Comenta "RETO" y te ayudamos a hacer el tuyo (15 días gratis, sin tarjeta)' if n == 21
            else f"🔔 Sigue el reto: mañana, día {n+1}")
    return (f"{head}\n\n{T[n]}\n\n📌 Historia ficticia para enseñarte cómo funciona: Lucía y sus cifras son inventadas; los pasos, reales.\n\n"
            f"{tail}\n👉 https://citasweb.es/\n\n#peluqueria #reservasonline #agendaonline #autonomos #retocitasweb")
