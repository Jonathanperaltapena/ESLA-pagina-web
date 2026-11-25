"""Música original de fondo para el video institucional de ESLA.

Composición propia, generada por síntesis (sin muestras ni obras de terceros), en Re mayor,
96 pulsos por minuto, 48 compases = 120 segundos. Carácter: épico, de logro y triunfo.
Estructura: introducción suave (8 c.) · crecida con timbales (8 c.) · tema (16 c.) ·
clímax con el tema una octava arriba (12 c.) · cadencia final (4 c.).

Uso: python3 video/musica.py video/musica.wav
"""
import sys
import wave

import numpy as np

SR = 44100
BPM = 96
BEAT = 60 / BPM
BAR = 4 * BEAT
BARS = 48
DUR = BARS * BAR
N = int(DUR * SR) + SR * 3
rng = np.random.default_rng(7)

L = np.zeros(N)
R = np.zeros(N)


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


NOTE = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}


def nm(s):
    name, octv = s[:-1], int(s[-1])
    return 12 * (octv + 1) + NOTE[name]


def env(n, a, d, s, r, total):
    """ADSR en muestras; total = duración de la nota (incluida la caída)."""
    e = np.ones(total) * s
    a_, d_, r_ = int(a * SR), int(d * SR), int(r * SR)
    a_ = min(a_, total)
    e[:a_] = np.linspace(0, 1, a_, endpoint=False)
    dd = min(d_, total - a_)
    if dd > 0:
        e[a_:a_ + dd] = np.linspace(1, s, dd, endpoint=False)
    if r_ > 0 and total > r_:
        e[-r_:] *= np.linspace(1, 0, r_)
    return e


def add(sig, t0, pan=0.0, gain=1.0):
    i = int(t0 * SR)
    j = min(N, i + len(sig))
    sig = sig[: j - i] * gain
    L[i:j] += sig * np.sqrt(0.5 * (1 - pan))
    R[i:j] += sig * np.sqrt(0.5 * (1 + pan))


def brass(freq, dur, vel=1.0):
    n = int((dur + 0.25) * SR)
    t = np.arange(n) / SR
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5.2 * t) * np.clip(t / 0.4, 0, 1)
    ph = 2 * np.pi * freq * np.cumsum(vib) / SR
    bright = np.clip(t / 0.08, 0, 1) * 0.6 + 0.4  # se abre el timbre al atacar
    sig = np.zeros(n)
    for h in range(1, 10):
        sig += np.sin(h * ph) / (h ** (1.55 - 0.45 * bright))
    return sig * env(n, 0.035, 0.12, 0.8, 0.22, n) * vel * 0.22


def strings(freqs, dur, vel=1.0):
    n = int((dur + 0.6) * SR)
    t = np.arange(n) / SR
    sig = np.zeros(n)
    for f in freqs:
        for det in (-0.0035, 0.0, 0.0035):
            ph = 2 * np.pi * f * (1 + det) * t + rng.uniform(0, 6.28)
            saw = np.zeros(n)
            for h in range(1, 7):
                saw += np.sin(h * ph) / h
            sig += saw
    return sig / (3 * len(freqs)) * env(n, 0.45, 0.3, 0.85, 0.6, n) * vel * 0.32


def bass(freq, dur, vel=1.0):
    n = int((dur + 0.2) * SR)
    t = np.arange(n) / SR
    sig = np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(4 * np.pi * freq * t) + 0.12 * np.sin(6 * np.pi * freq * t)
    return sig * env(n, 0.02, 0.2, 0.7, 0.18, n) * vel * 0.32


def timpani(freq, vel=1.0):
    n = int(1.6 * SR)
    t = np.arange(n) / SR
    f = freq * (1 + 0.06 * np.exp(-t * 18))
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = (np.sin(ph) + 0.45 * np.sin(1.5 * ph) + 0.25 * np.sin(1.99 * ph)) * np.exp(-t * 3.2)
    hit = rng.normal(0, 1, n) * np.exp(-t * 60) * 0.35
    return (body + hit) * vel * 0.42


def cymbal_swell(dur):
    n = int(dur * SR)
    noise = rng.normal(0, 1, n)
    noise = np.diff(np.concatenate([[0], noise]))  # tono brillante
    return noise * np.linspace(0, 1, n) ** 2.2 * 0.05


# Armonía: I–V–vi–IV en Re mayor, con cadencia al final
PROG = {"D": ["D3", "F#3", "A3", "D4"], "A": ["A2", "E3", "A3", "C#4"], "Bm": ["B2", "D3", "F#3", "B3"],
        "G": ["G2", "D3", "G3", "B3"], "Em": ["E3", "G3", "B3", "E4"]}
ROOT = {"D": "D2", "A": "A1", "Bm": "B1", "G": "G1", "Em": "E2"}
loop = ["D", "A", "Bm", "G"]
chords = [loop[i % 4] for i in range(44)] + ["G", "A", "D", "D"]

# Melodía original (nota, pulsos); 8 compases
THEME = [
    [("A4", 1), ("D5", 1.5), ("E5", 0.5), ("F#5", 1)],
    [("E5", 1.5), ("C#5", 0.5), ("A4", 2)],
    [("B4", 1), ("D5", 1), ("F#5", 1.5), ("E5", 0.5)],
    [("D5", 1), ("B4", 1), ("D5", 2)],
    [("F#5", 1), ("A5", 1.5), ("G5", 0.5), ("F#5", 1)],
    [("E5", 1.5), ("F#5", 0.5), ("E5", 1), ("C#5", 1)],
    [("D5", 1), ("F#5", 1), ("B5", 1.5), ("A5", 0.5)],
    [("G5", 1), ("F#5", 1), ("E5", 2)],
]
FINAL = [[("F#5", 1), ("G5", 1), ("A5", 2)], [("E5", 1), ("F#5", 1), ("G5", 1), ("E5", 1)], [("D5", 4)], []]


def play_melody(bars, start_bar, transpose=0, vel=1.0, pan=0.15, harmony=False):
    for k, bar in enumerate(bars):
        t = (start_bar + k) * BAR
        for note, beats in bar:
            f = midi(nm(note) + transpose)
            add(brass(f, beats * BEAT * 0.95, vel), t, pan)
            if harmony:  # segunda voz una tercera abajo (aprox.: sexta menor abajo en octava)
                add(brass(f * 0.7937, beats * BEAT * 0.95, vel * 0.55), t, -0.25)
            t += beats * BEAT


for b, ch in enumerate(chords):
    t = b * BAR
    section_vel = 0.55 if b < 8 else 0.8 if b < 16 else 1.0
    add(strings([midi(nm(x)) for x in PROG[ch]], BAR, section_vel), t, 0.0)
    if b >= 4:
        r = midi(nm(ROOT[ch]))
        for half in (0, 2):
            add(bass(r, 2 * BEAT, section_vel), t + half * BEAT, 0.0)
    if 8 <= b < 44:  # timbales en 1 y 3; redoble al final de cada frase de 8
        tf = midi(nm("D2")) if ch in ("D", "Bm") else midi(nm("A1"))
        add(timpani(tf, 0.7 if b < 16 else 1.0), t, -0.1)
        add(timpani(tf, 0.5 if b < 16 else 0.75), t + 2 * BEAT, -0.1)
        if b % 8 == 7:
            for k in range(8):
                add(timpani(tf, 0.35 + 0.08 * k), t + 2 * BEAT + k * BEAT / 4, -0.1)
    if 8 <= b < 16 and b % 2 == 0:  # fanfarria corta en la crecida
        for k, nt in enumerate(["D4", "D4", "A4"]):
            add(brass(midi(nm(nt)), BEAT * (0.4 if k < 2 else 1.6), 0.55), t + k * BEAT * 0.5, -0.3)

add(cymbal_swell(2 * BAR), 14 * BAR)
add(cymbal_swell(2 * BAR), 30 * BAR)
play_melody(THEME, 16, 0, 0.85)
play_melody(THEME, 24, 0, 0.95, harmony=True)
play_melody(THEME, 32, 0, 1.05, harmony=True, pan=0.1)
play_melody(THEME[:4], 40, 0, 1.05, harmony=True)
play_melody(FINAL, 44, 0, 1.1, harmony=True)
# Acorde final sostenido con timbal
t_end = 46 * BAR
add(strings([midi(nm(x)) for x in ["D3", "A3", "D4", "F#4", "A4"]], 2 * BAR + 1.5, 1.1), t_end)
add(brass(midi(nm("D4")), 2 * BAR, 0.8), t_end, -0.2)
add(brass(midi(nm("A4")), 2 * BAR, 0.7), t_end, 0.2)
add(timpani(midi(nm("D2")), 1.1), t_end)

# Reverberación de sala (convolución con respuesta sintética)
ir_n = int(2.2 * SR)
ti = np.arange(ir_n) / SR
ir = rng.normal(0, 1, ir_n) * np.exp(-ti * 3.0)
ir[0] = 0
ir /= np.sqrt(np.sum(ir ** 2))


def reverb(x, wet=0.22):
    m = 1 << int(np.ceil(np.log2(len(x) + ir_n)))
    y = np.fft.irfft(np.fft.rfft(x, m) * np.fft.rfft(ir, m), m)[: len(x)]
    return x * (1 - wet) + y * wet * 1.3


L, R = reverb(L), reverb(R)


def eq(x):
    # Ecualización: corta subgraves (<35 Hz), baja 5 dB los graves y 2 dB los medios graves; realza el brillo
    m = 1 << int(np.ceil(np.log2(len(x))))
    X = np.fft.rfft(x, m)
    f = np.fft.rfftfreq(m, 1 / SR)
    g = np.ones_like(f)
    g *= 1 / np.sqrt(1 + (35 / np.maximum(f, 1)) ** 8)
    g *= np.where(f < 140, 10 ** (-5 / 20), np.where(f < 320, 10 ** (-2 / 20), 1.0))
    g *= np.where((f > 2500) & (f < 9000), 10 ** (1.5 / 20), 1.0)
    return np.fft.irfft(X * g, m)[: len(x)]


L, R = eq(L), eq(R)
stereo = np.stack([L, R], axis=1)[: int((DUR + 2.5) * SR)]
# Compresión suave y normalización a -1 dBFS
stereo = np.tanh(stereo * 1.15) / 1.15
fade_in = int(1.0 * SR)
stereo[:fade_in] *= np.linspace(0, 1, fade_in)[:, None]
fade_out = int(3.0 * SR)
stereo[-fade_out:] *= np.linspace(1, 0, fade_out)[:, None]
stereo *= 10 ** (-1 / 20) / np.max(np.abs(stereo))

out = sys.argv[1] if len(sys.argv) > 1 else "musica.wav"
with wave.open(out, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((stereo * 32767).astype("<i2").tobytes())
print("ok", out, f"{len(stereo) / SR:.1f} s")
