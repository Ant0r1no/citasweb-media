"""Escenas realistas de móvil para los vídeos de voz (llamada, chat, notificaciones, agenda, web de reservas…).

Cada escena devuelve (html, eventos). Los elementos llevan atributos que anima el JS de voicevideo.py:
  data-t="s"        aparece con rebote a los s segundos del inicio de la frase
  data-on="s"       recibe la clase "on" a los s segundos (cambios de estado: reservado, pulsado…)
  data-count="N"    contador de 0 a N (data-t inicio, data-dur duración)
  data-timer        cronómetro de llamada
  .shake            el móvil vibra mientras suena (data-ring="dur")
Los eventos [(segundo, tipo)] son los efectos de sonido sincronizados (ver sfx.py).
"""
import html

E = html.escape

STATUS = '<div class="sb"><span>{time}</span><span class="isl"></span><span class="sbi">●●●● ▮</span></div>'


def _status(time):
    return STATUS.format(time=E(time))


def call(sc, dur):
    ring = min(2.8, max(1.0, dur - 0.4))
    name = E(sc.get("name", "Cliente"))
    h = f'''<div class="scr callscr shake" data-ring="{ring:.2f}">{_status(sc.get("time", "17:32"))}
<div class="callsub">llamada entrante…</div><div class="callname">{name}</div>
<div class="avwrap"><i class="ring r1"></i><i class="ring r2"></i><div class="av big">{E(name[:1])}</div></div>
<div class="cbtns"><div class="cb red">✕</div><div class="cb green">✆</div></div></div>'''
    return h, [(0.15, f"ring:{ring:.2f}")]


def callon(sc, dur):
    name = E(sc.get("name", "Cliente"))
    h = f'''<div class="scr callscr">{_status(sc.get("time", "17:33"))}
<div class="callsub" data-timer>00:00</div><div class="callname">{name}</div>
<div class="avwrap"><div class="av big">{E(name[:1])}</div></div>
<div class="bubble-say" data-t="0.5">«¿Tienes hueco el martes?»</div>
<div class="cbtns"><div class="cb grey">🔇</div><div class="cb red">✕</div><div class="cb grey">🔊</div></div></div>'''
    return h, []


def chat(sc, dur):
    name = E(sc.get("name", "Cliente"))
    gap = sc.get("gap", 0.8)
    t = sc.get("start", 0.3)
    rows, ev = [], []
    for side, text, *rest in sc["msgs"]:
        hh = rest[0] if rest else sc.get("time", "")
        rows.append(f'<div class="msg {side}" data-t="{t:.2f}">{E(text)}<span class="mt">{E(hh)}{" ✓✓" if side == "out" else ""}</span></div>')
        ev.append((t, "ping" if side == "in" else "send"))
        t += gap
    if sc.get("seen"):
        rows.append(f'<div class="seen" data-t="{t:.2f}">Visto · sin respuesta</div>')
    if sc.get("typing"):
        rows.append(f'<div class="msg in typing" data-t="{t:.2f}"><b>•</b><b>•</b><b>•</b></div>')
    h = f'''<div class="scr chatscr">{_status(sc.get("time", "12:04"))}
<div class="chead"><span class="back">‹</span><div class="av">{E(name[:1])}</div><div><b>{name}</b><small>{E(sc.get("status", "en línea"))}</small></div></div>
<div class="cbody"><div class="day">{E(sc.get("day", "HOY"))}</div>{"".join(rows)}</div>
<div class="cinput"><span>Mensaje</span><i>➤</i></div></div>'''
    return h, ev


def notif(sc, dur):
    rows, ev = [], []
    t = sc.get("start", 0.35)
    for app, title, body in sc["items"]:
        rows.append(f'<div class="ncard" data-t="{t:.2f}"><div class="nic">{E(app[:1])}</div><div><small>{E(app)} · ahora</small><b>{E(title)}</b><p>{E(body)}</p></div></div>')
        ev.append((t, "ping"))
        t += sc.get("gap", 0.7)
    h = f'''<div class="scr lockscr">{_status("")}
<div class="ldate">{E(sc.get("date", "martes, 14 de enero"))}</div><div class="ltime">{E(sc.get("clock", "23:47"))}</div>
<div class="nlist">{"".join(rows)}</div></div>'''
    return h, ev


def agenda(sc, dur):
    rows, ev = [], []
    for i, (hour, label, state, *rest) in enumerate(sc["slots"]):
        on = rest[0] if rest else None
        attr = f' data-on="{on:.2f}"' if on is not None else ""
        newlab = rest[1] if len(rest) > 1 else ""
        extra = f'<span class="after">{E(newlab)}</span>' if newlab else ""
        rows.append(f'<div class="slot {state}" data-t="{0.15 + i * 0.07:.2f}"{attr}><span class="hr">{E(hour)}</span><span class="lb">{E(label)}</span>{extra}</div>')
        if on is not None:
            ev.append((on, {"booked": "pop", "noshow": "buzz", "pending": "tick"}.get(state, "pop")))
    days = "".join(f'<span class="{"sel" if d == sc.get("sel", "M") else ""}">{d}</span>' for d in "LMXJVSD")
    h = f'''<div class="scr agscr">{_status(sc.get("time", "09:12"))}
<div class="aghead"><b>{E(sc.get("title", "Agenda"))}</b><small>{E(sc.get("sub", "Martes"))}</small></div>
<div class="agdays">{days}</div><div class="slots">{"".join(rows)}</div></div>'''
    return h, ev


def web(sc, dur):
    biz = E(sc.get("biz", "Tu Barbería"))
    svcs = sc.get("services", [["Corte", "15 €", "30 min"], ["Corte + barba", "20 €", "45 min"], ["Degradado", "17 €", "40 min"]])
    times = sc.get("times", ["10:00", "11:00", "12:30", "17:00", "18:30", "19:00"])
    pick = sc.get("pick", 1)
    s_rows = "".join(f'<div class="svc{" on-able" if i == 0 else ""}" data-t="{0.15 + i * 0.08:.2f}"{" data-on=\"0.45\"" if i == 0 else ""}><b>{E(a)}</b><small>{E(c)}</small><span>{E(b)}</span></div>' for i, (a, b, c) in enumerate(svcs))
    chips = "".join(f'<span class="chip"{f" data-on=\"1.0\"" if i == pick else ""}>{E(x)}</span>' for i, x in enumerate(times))
    h = f'''<div class="scr webscr">{_status(sc.get("time", "22:41"))}
<div class="url">🔒 {E(sc.get("url", "tubarberia.citasweb.es"))}</div>
<div class="whead"><div class="wlogo">{biz[:1]}</div><b>{biz}</b><small>Reserva tu cita online</small></div>
<div class="svcs">{s_rows}</div><div class="wlbl" data-t="0.6">{E(sc.get("day", "Martes"))} · elige hora</div><div class="chips" data-t="0.65">{chips}</div>
<div class="wbtn" data-t="0.8" data-on="1.5">Reservar</div>
<div class="tap" data-tap="0.45:52:46,1.0:{50 + (pick % 3) * 0:.0f}:73,1.5:50:86"></div>
<div class="ok" data-on="1.85"><div class="okc">✓</div><b>¡Reserva confirmada!</b><small>{E(sc.get("day", "Martes"))} · {E(times[pick])}</small></div></div>'''
    return h, [(0.45, "tap"), (1.0, "tap"), (1.5, "tap"), (1.85, "ding")]


def money(sc, dur):
    lines = sc.get("lines", ["1 plantón = 25 €", "3 por semana = 75 €"])
    rows = "".join(f'<div class="mline" data-t="{0.2 + i * 0.6:.2f}">{E(x)}</div>' for i, x in enumerate(lines))
    t0 = 0.2 + len(lines) * 0.6
    total = sc.get("total", 300)
    h = f'''<div class="scr moneyscr">{_status(sc.get("time", "20:15"))}
<div class="mtitle">Lo que pierdes al mes</div>{rows}
<div class="mtotal" data-t="{t0:.2f}">−<span data-count="{total}" data-t="{t0:.2f}" data-dur="1.1">0</span> €</div>
<div class="mbar" data-t="{t0:.2f}"><i data-grow="{t0:.2f}:1.1"></i></div></div>'''
    return h, [(0.2 + i * 0.6, "tick") for i in range(len(lines))] + [(t0 + 1.1, "cash")]


BUILDERS = {"call": call, "callon": callon, "chat": chat, "notif": notif, "agenda": agenda, "web": web, "money": money}


def build(sc, dur):
    return BUILDERS[sc["type"]](sc, dur)


CSS = """
#phone{position:absolute;left:50%;top:790px;width:600px;height:1220px;margin-left:-300px;border-radius:78px;background:#0c0c0c;
 box-shadow:0 0 0 12px #2a2a2a,0 0 0 14px #444,0 60px 120px #000c;overflow:hidden;will-change:transform}
.scr{position:absolute;inset:0;opacity:0;font-family:'Inter','Poppins',sans-serif;color:#fff;overflow:hidden}
.sb{display:flex;justify-content:space-between;align-items:center;padding:26px 52px 0;font-size:26px;font-weight:700;height:80px}
.isl{width:170px;height:46px;border-radius:30px;background:#000;display:block}.sbi{font-size:16px;letter-spacing:2px}
.av{width:72px;height:72px;border-radius:50%;background:linear-gradient(135deg,#7a8aa0,#4a5568);display:flex;align-items:center;justify-content:center;font-weight:800;font-size:34px;color:#fff;flex:none}
.av.big{width:180px;height:180px;font-size:84px;position:relative;z-index:2}
/* llamada */
.callscr{background:linear-gradient(180deg,#2b3a4a,#0e141b)}
.callsub{text-align:center;margin-top:40px;font-size:32px;color:#ffffffaa}
.callname{text-align:center;font-size:66px;font-weight:600;margin-top:10px}
.avwrap{position:relative;width:180px;height:180px;margin:40px auto 0}
.ring{position:absolute;inset:0;border-radius:50%;border:4px solid #ffffff55}
.cbtns{position:absolute;left:0;right:0;top:600px;display:flex;justify-content:space-around;padding:0 60px}
.cb{width:130px;height:130px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:56px;font-weight:800}
.cb.red{background:#ff3b30}.cb.green{background:#34c759}.cb.grey{background:#ffffff26}
.bubble-say{margin:30px 60px 0;background:#ffffff1f;border-radius:30px;padding:24px 30px;font-size:36px;text-align:center;font-style:italic}
/* chat */
.chatscr{background:#0b141a}
.chead{display:flex;align-items:center;gap:20px;padding:18px 30px;background:#1f2c34}
.chead b{display:block;font-size:32px}.chead small{font-size:22px;color:#8696a0}.back{font-size:56px;color:#53bdeb}
.cbody{padding:20px 26px;background-image:radial-gradient(#ffffff08 2px,transparent 2px);background-size:36px 36px;height:900px}
.day{margin:6px auto 20px;width:max-content;background:#1f2c34;color:#8696a0;font-size:20px;padding:8px 18px;border-radius:12px}
.msg{max-width:78%;padding:16px 22px 30px;border-radius:22px;font-size:32px;line-height:1.25;margin:12px 0;position:relative;width:max-content;opacity:0}
.msg.in{background:#202c33;border-top-left-radius:6px}
.msg.out{background:#005c4b;margin-left:auto;border-top-right-radius:6px}
.mt{position:absolute;right:16px;bottom:6px;font-size:18px;color:#ffffff88}
.msg.out .mt{color:#53bdeb}
.seen{text-align:right;font-size:22px;color:#8696a0;margin-top:8px;opacity:0}
.typing b{display:inline-block;font-size:40px;margin:0 3px;color:#8696a0}
.cinput{position:absolute;left:20px;right:20px;bottom:60px;display:flex;gap:16px;align-items:center}
.cinput span{flex:1;background:#2a3942;border-radius:40px;padding:22px 30px;color:#8696a0;font-size:28px}
.cinput i{width:80px;height:80px;border-radius:50%;background:#00a884;display:flex;align-items:center;justify-content:center;font-style:normal;font-size:34px}
/* bloqueo */
.lockscr{background:radial-gradient(circle at 30% 20%,#3a2f5a,#120f1f 70%)}
.ldate{text-align:center;margin-top:40px;font-size:32px;font-weight:600;color:#ffffffcc}
.ltime{text-align:center;font-size:160px;font-weight:700;letter-spacing:-6px;line-height:1}
.nlist{padding:36px 30px 0}
.ncard{display:flex;gap:20px;background:#ffffff26;backdrop-filter:blur(20px);border-radius:34px;padding:24px 26px;margin-bottom:18px;opacity:0}
.nic{width:66px;height:66px;border-radius:16px;background:#25d366;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:32px;flex:none}
.ncard small{font-size:20px;color:#ffffffaa}.ncard b{display:block;font-size:28px;margin-top:4px}.ncard p{font-size:28px;color:#ffffffdd;margin-top:2px}
/* agenda */
.agscr{background:#f4f5f7;color:#111}
.aghead{padding:20px 40px 0}.aghead b{font-size:48px;display:block}.aghead small{font-size:26px;color:#666}
.agdays{display:flex;justify-content:space-between;padding:24px 40px;font-size:26px;font-weight:700;color:#888}
.agdays .sel{background:var(--ac);color:var(--bg);border-radius:50%;width:52px;height:52px;display:flex;align-items:center;justify-content:center}
.slots{padding:0 30px}
.slot{display:flex;align-items:center;gap:22px;background:#fff;border-radius:24px;padding:22px 26px;margin-bottom:14px;font-size:30px;box-shadow:0 2px 8px #0001;opacity:0;position:relative;overflow:hidden;border:3px solid transparent}
.slot .hr{font-weight:800;width:100px;color:#333}.slot .lb{flex:1;font-weight:600}
.slot.busy{background:#e9ebef;color:#666}
.slot.free{border-color:#34c759}.slot.free .lb{color:#1f9d47}
.slot.pending{background:repeating-linear-gradient(45deg,#fff3d6,#fff3d6 16px,#ffe8ad 16px,#ffe8ad 32px)}.slot.pending .lb{color:#a86b00}
.slot .after{position:absolute;inset:0;display:flex;align-items:center;padding-left:150px;font-weight:800;opacity:0}
.slot.booked.on{background:#34c759;color:#fff}.slot.booked.on .hr{color:#fff}.slot.booked .after{background:#34c759;color:#fff}.slot.booked.on .after{opacity:1}
.slot.noshow.on{background:#ffe1df}.slot.noshow .after{background:#ff3b30;color:#fff}.slot.noshow.on .after{opacity:1}
.slot.pending.on .after{opacity:1;background:#ff9f0a;color:#fff}
/* web */
.webscr{background:#fff;color:#111}
.url{margin:6px 30px 0;background:#eef0f3;border-radius:20px;padding:14px 22px;font-size:22px;color:#555}
.whead{text-align:center;padding:26px 0 10px}.wlogo{width:96px;height:96px;margin:0 auto 12px;border-radius:24px;background:var(--bg);color:var(--ac);display:flex;align-items:center;justify-content:center;font-size:52px;font-weight:900}
.whead b{display:block;font-size:40px}.whead small{font-size:24px;color:#777}
.svcs{padding:10px 30px}
.svc{display:flex;align-items:center;gap:14px;border:3px solid #e5e7eb;border-radius:22px;padding:20px 24px;margin-bottom:12px;opacity:0}
.svc b{font-size:30px}.svc small{font-size:22px;color:#888;flex:1}.svc span{font-size:30px;font-weight:800}
.svc.on{border-color:var(--ac);background:#fff8e6}
.wlbl{padding:14px 34px 6px;font-size:26px;font-weight:700;color:#444;opacity:0}
.chips{display:flex;flex-wrap:wrap;gap:12px;padding:6px 30px;opacity:0}
.chip{border:3px solid #e5e7eb;border-radius:18px;padding:14px 22px;font-size:26px;font-weight:700}
.chip.on{background:var(--bg);color:var(--ac);border-color:var(--bg)}
.wbtn{margin:22px 30px 0;background:var(--ac);color:var(--bg);text-align:center;font-size:34px;font-weight:800;border-radius:24px;padding:26px;opacity:0}
.wbtn.on{filter:brightness(.85)}
.tap{position:absolute;width:90px;height:90px;border-radius:50%;background:#0003;border:4px solid #fff;opacity:0;margin:-45px 0 0 -45px;z-index:5}
.ok{position:absolute;inset:0;background:#ffffffee;display:flex;flex-direction:column;align-items:center;justify-content:center;opacity:0}
.ok.on{opacity:1}.okc{width:180px;height:180px;border-radius:50%;background:#34c759;color:#fff;font-size:110px;display:flex;align-items:center;justify-content:center;font-weight:900;margin-bottom:30px}
.ok b{font-size:44px}.ok small{font-size:30px;color:#666;margin-top:10px}
/* dinero */
.moneyscr{background:linear-gradient(180deg,#1a0f0f,#0b0b0b)}
.mtitle{text-align:center;font-size:34px;color:#ffffffaa;margin-top:30px}
.mline{text-align:center;font-size:52px;font-weight:700;margin-top:26px;opacity:0}
.mtotal{text-align:center;font-size:150px;font-weight:900;color:#ff453a;margin-top:30px;opacity:0;letter-spacing:-4px}
.mbar{margin:30px 70px;height:22px;background:#ffffff1a;border-radius:20px;overflow:hidden;opacity:0}.mbar i{display:block;height:100%;width:0;background:#ff453a}
"""

JS = r"""
function sceneRender(el, lt, t){
  el.querySelectorAll('[data-t]').forEach(x => {
    if (x.hasAttribute('data-count')) return;
    const s = (lt - parseFloat(x.dataset.t))/.35, b = back(s);
    x.style.opacity = Math.min(1, Math.max(0, s*2.5));
    x.style.transform = `translateY(${(1-b)*40}px) scale(${.85+.15*b})`;
  });
  el.querySelectorAll('[data-on]').forEach(x => x.classList.toggle('on', lt >= parseFloat(x.dataset.on)));
  el.querySelectorAll('[data-count]').forEach(x => {
    const p = ease((lt - parseFloat(x.dataset.t))/parseFloat(x.dataset.dur));
    x.textContent = Math.round(parseFloat(x.dataset.count)*p);
  });
  el.querySelectorAll('[data-grow]').forEach(x => { const [a,d] = x.dataset.grow.split(':').map(parseFloat); x.style.width = (100*ease((lt-a)/d))+'%'; });
  el.querySelectorAll('[data-timer]').forEach(x => { const s = Math.max(0, Math.floor(lt)); x.textContent = '00:' + String(s).padStart(2,'0'); });
  el.querySelectorAll('[data-ring]').forEach(x => {
    const r = parseFloat(x.dataset.ring), on = lt > .15 && lt < .15 + r && ((lt-.15) % .9) < .6;
    x.style.transform = on ? `translateX(${7*Math.sin(lt*70)}px) rotate(${.8*Math.sin(lt*55)}deg)` : 'none';
    x.querySelectorAll('.ring').forEach((g,i) => { const q = ((lt + i*.6) % 1.2)/1.2; g.style.transform = `scale(${1+q*.9})`; g.style.opacity = lt < .15 + r ? (1-q).toFixed(2) : 0; });
  });
  el.querySelectorAll('[data-tap]').forEach(x => {
    let o = 0, L = 0, T = 0;
    x.dataset.tap.split(',').forEach(e => { const [tt,l,tp] = e.split(':').map(parseFloat); const d = lt - tt; if (d > -.25 && d < .3){ o = d < 0 ? 1 + d/.25 : 1 - d/.3; L = l; T = tp; } });
    x.style.opacity = Math.max(0,o).toFixed(2); x.style.left = L + '%'; x.style.top = T + '%';
  });
}
"""
