"""Efectos de sonido sintetizados (originales, sin derechos de terceros) para los vídeos de voz.

make_track(seconds, events) -> np.int16 estéreo 44.1 kHz con cada efecto colocado en su segundo.
Eventos: (segundo, tipo). Tipos: whoosh, ring:<dur>, ping, send, tap, pop, ding, buzz, tick, cash.
"""
import numpy as np
from scipy.signal import lfilter

SR = 44100
RNG = np.random.default_rng(7)


def _t(d):
    return np.arange(int(d * SR)) / SR


def _env(n, a, r):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / r)


def tone(f, d, a=0.002, r=0.12, harm=(1, 0.3, 0.1)):
    t = _t(d)
    x = sum(h * np.sin(2 * np.pi * f * (i + 1) * t) for i, h in enumerate(harm))
    return x * _env(len(t), a, r)


def whoosh(d=0.45):
    n = int(d * SR)
    noise = RNG.uniform(-1, 1, n)
    out = np.zeros(n)
    # barrido de un paso-banda simple: mezcla de pasa-bajos con corte creciente
    seg = 64
    y = 0.0
    for i in range(0, n, seg):
        p = i / n
        fc = 300 + 5000 * np.sin(np.pi * p) ** 2
        a = np.exp(-2 * np.pi * fc / SR)
        blk = noise[i:i + seg]
        yb = np.empty_like(blk)
        for k, v in enumerate(blk):
            y = (1 - a) * v + a * y
            yb[k] = y
        out[i:i + seg] = yb
    out = out - lfilter([1], [1, -0.995], out) * 0.005
    env = np.sin(np.pi * np.linspace(0, 1, n)) ** 2
    return out * env * 3.0


def ring(d=2.5):
    """Tono de llamada original: arpegio rápido tipo marimba que se repite."""
    pat = [1318.5, 1568.0, 1975.5, 1568.0, 1318.5, 1568.0, 1975.5, 2349.3]
    out = np.zeros(int(d * SR))
    t = 0.0
    while t < d:
        for k, f in enumerate(pat):
            s = int((t + k * 0.075) * SR)
            if s >= len(out):
                break
            x = tone(f, 0.25, r=0.06, harm=(1, 0.5, 0.15))
            e = min(len(out), s + len(x))
            out[s:e] += x[: e - s] * 0.6
        t += 0.9
    return out


def ping():
    return _mix([(0, tone(1318.5, 0.35, r=0.09)), (0.08, tone(1975.5, 0.45, r=0.12))])


def send():
    t = _t(0.12)
    f = 900 - 500 * t / 0.12
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(len(t), 0.002, 0.04) * 0.6


def tap():
    n = int(0.03 * SR)
    return RNG.uniform(-1, 1, n) * np.exp(-np.arange(n) / SR / 0.004) * 0.7 + tone(2200, 0.03, r=0.006) * 0.3


def pop():
    t = _t(0.1)
    f = 300 + 900 * np.exp(-t * 40)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(len(t), 0.001, 0.03)


def ding():
    return _mix([(0, tone(1046.5, 0.6, r=0.25)), (0.09, tone(1318.5, 0.6, r=0.25)), (0.18, tone(1568, 0.9, r=0.35))]) * 0.8


def buzz():
    t = _t(0.35)
    x = np.sign(np.sin(2 * np.pi * 110 * t)) * 0.5 + np.sin(2 * np.pi * 220 * t) * 0.3
    return x * _env(len(t), 0.005, 0.12) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 14 * t)))


def tick():
    return tone(1800, 0.05, r=0.012, harm=(1, 0.2)) * 0.7


def cash():
    return _mix([(0, tick()), (0.06, tone(2637, 0.7, r=0.2, harm=(1, 0.4, 0.2))), (0.12, tone(3136, 0.7, r=0.25, harm=(1, 0.3)))])


def _mix(parts):
    L = max(int(o * SR) + len(x) for o, x in parts)
    out = np.zeros(L)
    for o, x in parts:
        s = int(o * SR)
        out[s:s + len(x)] += x
    return out


GAIN = {"whoosh": 0.22, "ring": 0.30, "ping": 0.45, "send": 0.30, "tap": 0.35, "pop": 0.40,
        "ding": 0.45, "buzz": 0.30, "tick": 0.35, "cash": 0.45}


def make_track(seconds, events):
    n = int(seconds * SR)
    L = np.zeros(n)
    for at, kind in events:
        name, _, arg = kind.partition(":")
        if name == "ring":
            x = ring(float(arg or 2.5))
        else:
            x = globals()[name]()
        x = x * GAIN[name]
        s = int(at * SR)
        if s >= n or s < 0:
            continue
        e = min(n, s + len(x))
        L[s:e] += x[: e - s]
    L = np.clip(L, -0.95, 0.95)
    st = np.stack([L, L], axis=1)
    return (st * 32767).astype(np.int16)
