#!/usr/bin/env python3
"""Música de fondo original (sintetizada, sin derechos de terceros) para los vídeos.

Uso: python3 generator/music.py salida.wav segundos [estilo] [semilla]
Estilos: "house" (por defecto, alegre, 120 BPM), "lofi" (relajado, 88 BPM), "pop" (enérgico, 128 BPM).
"""
import sys
import numpy as np
import wave

SR = 44100
NOTE = {n: i for i, n in enumerate(["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"])}


def freq(name, octave):
    return 440.0 * 2 ** ((NOTE[name] + 12 * (octave + 1) - 69) / 12)


def env(n, a=0.005, d=0.1, s=0.6, r=0.1, length=None):
    length = length or n
    t = np.arange(n) / SR
    e = np.ones(n) * s
    ai, di, ri = int(a * SR), int(d * SR), int(r * SR)
    if ai: e[:ai] = np.linspace(0, 1, ai)
    if di: e[ai:ai + di] = np.linspace(1, s, min(di, max(0, n - ai)))[: max(0, min(di, n - ai))]
    if ri and n > ri: e[-ri:] *= np.linspace(1, 0, ri)
    return e


def saw(f, n, detune=0.0):
    t = np.arange(n) / SR
    out = np.zeros(n)
    for d in (-detune, 0, detune):
        ph = (t * f * (1 + d)) % 1.0
        out += 2 * ph - 1
    return out / 3


def lowpass(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.zeros_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc = (1 - a) * x[i] + a * acc
        y[i] = acc
    return y


def lowpass_fast(x, cutoff, passes=2):
    # filtro de un polo vectorizado por bloques (suficiente para pads)
    from scipy.signal import lfilter
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = x
    for _ in range(passes):
        y = lfilter([1 - a], [1, -a], y)
    return y


def kick(n):
    t = np.arange(n) / SR
    f = 50 + 120 * np.exp(-t * 35)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 7)


def clap(n, rng):
    t = np.arange(n) / SR
    noise = rng.uniform(-1, 1, n)
    from scipy.signal import lfilter
    noise = lfilter([1, -0.95], [1], noise)
    e = np.exp(-t * 18) * (1 + 0.6 * np.exp(-((t - 0.012) * 400) ** 2))
    return noise * e * 0.6


def hat(n, rng, open_=False):
    t = np.arange(n) / SR
    noise = rng.uniform(-1, 1, n)
    from scipy.signal import lfilter
    noise = lfilter([1, -1], [1, -0.3], noise)
    return noise * np.exp(-t * (12 if open_ else 60)) * 0.35


STYLES = {
    "house": dict(bpm=120, prog=[("A", "m"), ("F", ""), ("C", ""), ("G", "")], swing=0.0, four=True),
    "pop": dict(bpm=128, prog=[("C", ""), ("G", ""), ("A", "m"), ("F", "")], swing=0.0, four=True),
    "lofi": dict(bpm=88, prog=[("D", "m7"), ("G", "7"), ("C", "maj7"), ("A", "m7")], swing=0.12, four=False),
}


def chord_notes(root, kind):
    r = NOTE[root]
    ints = {"": [0, 4, 7], "m": [0, 3, 7], "m7": [0, 3, 7, 10], "7": [0, 4, 7, 10], "maj7": [0, 4, 7, 11]}[kind]
    names = list(NOTE.keys())
    return [(names[(r + i) % 12], 3 + (r + i) // 12) for i in ints]


def make(seconds, style="house", seed=1):
    cfg = STYLES[style]
    rng = np.random.default_rng(seed)
    bpm = cfg["bpm"]
    beat = 60 / bpm
    bar = 4 * beat
    total = int((seconds + 1) * SR)
    L = np.zeros(total)
    R = np.zeros(total)
    drums = np.zeros(total)
    side = np.ones(total)  # sidechain envelope del bombo
    nbars = int(np.ceil(seconds / bar)) + 1
    prog = cfg["prog"]
    for b in range(nbars):
        root, kind = prog[b % len(prog)]
        notes = chord_notes(root, kind)
        t0 = int(b * bar * SR)
        n = int(bar * SR)
        if t0 >= total: break
        n = min(n, total - t0)
        # pad
        pad = np.zeros(n)
        for nm, oc in notes:
            pad += saw(freq(nm, oc + 1), n, detune=0.004)
        pad = lowpass_fast(pad, 1400) * env(n, a=0.05, d=0.2, s=0.8, r=0.08) * 0.16
        L[t0:t0 + n] += pad
        R[t0:t0 + n] += pad
        # bajo (corcheas)
        bf = freq(root, 2)
        for k in range(8):
            s = t0 + int(k * beat / 2 * SR)
            m = int(beat / 2 * SR * 0.9)
            if s + m > total: break
            if not cfg["four"] and k % 2: continue
            x = saw(bf * (2 if k % 4 == 3 else 1), m)
            x = lowpass_fast(x, 600) * env(m, a=0.003, d=0.08, s=0.5, r=0.03) * 0.32
            L[s:s + m] += x
            R[s:s + m] += x
        # arpegio pluck (semicorcheas)
        arp = [notes[i % len(notes)] for i in (0, 1, 2, 1, 0, 2, 1, 2)]
        for k in range(16):
            if rng.random() < (0.25 if style == "lofi" else 0.1): continue
            nm, oc = arp[k % len(arp)]
            sw = cfg["swing"] * beat / 2 if k % 2 else 0
            s = t0 + int((k * beat / 4 + sw) * SR)
            m = int(beat / 4 * SR * 0.95)
            if s + m > total: break
            x = saw(freq(nm, oc + 2), m)
            x = lowpass_fast(x, 2600) * env(m, a=0.002, d=0.06, s=0.15, r=0.03) * 0.09
            pan = 0.35 if k % 2 else -0.35
            L[s:s + m] += x * (1 - pan)
            R[s:s + m] += x * (1 + pan)
        # batería
        for k in range(4):
            s = t0 + int(k * beat * SR)
            if cfg["four"] or k in (0, 2):
                m = min(int(0.35 * SR), total - s)
                if m > 0:
                    drums[s:s + m] += kick(m) * 0.9
                    sc = 1 - 0.65 * np.exp(-np.arange(m) / SR * 9)
                    side[s:s + m] = np.minimum(side[s:s + m], sc)
            if k in (1, 3):
                m = min(int(0.25 * SR), total - s)
                if m > 0: drums[s:s + m] += clap(m, rng) * (0.8 if cfg["four"] else 0.5)
            for h in range(2):
                hs = s + int((h * beat / 2 + (cfg["swing"] * beat / 2 if h else 0)) * SR)
                m = min(int(0.12 * SR), total - hs)
                if m > 0 and (h == 1 or style != "house"):
                    drums[hs:hs + m] += hat(m, rng, open_=(h == 1 and style == "house")) * (1 if h else 0.6)
    L *= side
    R *= side
    L += drums
    R += drums
    # intro y final suaves
    fi, fo = int(0.8 * SR), int(1.5 * SR)
    for ch in (L, R):
        ch[:fi] *= np.linspace(0, 1, fi)
        ch[-fo:] *= np.linspace(1, 0, fo)
    st = np.stack([L, R], axis=1)[: int(seconds * SR)]
    st /= np.max(np.abs(st)) + 1e-9
    return (st * 0.89 * 32767).astype(np.int16)


if __name__ == "__main__":
    out, secs = sys.argv[1], float(sys.argv[2])
    style = sys.argv[3] if len(sys.argv) > 3 else "house"
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    data = make(secs, style, seed)
    with wave.open(out, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(data.tobytes())
    print(out)
