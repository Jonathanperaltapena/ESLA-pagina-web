"""Monta el video institucional: cuadros + acercamiento lento + fundidos + música.

Uso: python3 video/montaje.py   →  video/ESLA-video-institucional.mp4 (1920×1080, 30 fps)
Requiere: video/cuadros/*.png (video/capturas.js) y video/musica.wav (video/musica.py).
"""
import subprocess
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
FPS, W, H = 30, 1920, 1080
FADE = 0.8
names = (ROOT / "cuadros" / "lista.txt").read_text().split()
durs = [6.0] + [6.0] * (len(names) - 2) + [14.5]
starts = np.concatenate([[0], np.cumsum(durs)[:-1]])
TOTAL = float(sum(durs))
IMGS = {}


def img(i):
    if i not in IMGS:
        IMGS[i] = Image.open(ROOT / "cuadros" / f"{names[i]}.png").convert("RGB")
    return IMGS[i]


def render(i, local):
    """Cuadro i en su instante local (s), con acercamiento lento del 0 al 5 %."""
    im = img(i)
    sw = im.width / W
    p = min(max(local / durs[i], 0), 1)
    p = p * p * (3 - 2 * p)  # suavizado
    zoom = 1.0 + (0.035 if i == len(names) - 1 else 0.05) * p
    a = sw / zoom
    cx, cy = 0.5 * im.width, 0.5 * im.height
    data = (a, 0, cx - a * W / 2, 0, a, cy - a * H / 2)
    return np.asarray(im.transform((W, H), Image.AFFINE, data, resample=Image.BICUBIC), dtype=np.float32)


def frame(n):
    t = n / FPS
    i = int(np.searchsorted(starts, t, side="right") - 1)
    local = t - starts[i]
    out = render(i, local)
    rem = durs[i] - local
    if rem < FADE and i + 1 < len(names):
        a = 1 - rem / FADE
        a = a * a * (3 - 2 * a)
        out = out * (1 - a) + render(i + 1, local - durs[i]) * a
    if t < 1.0:
        out *= t
    if TOTAL - t < 2.0:
        out *= max(TOTAL - t, 0) / 2.0
    return np.clip(out, 0, 255).astype(np.uint8).tobytes()


if __name__ == "__main__":
    nframes = int(round(TOTAL * FPS))
    out = ROOT / "ESLA-video-institucional.mp4"
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", str(ROOT / "musica.wav"),
           "-filter:a", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
           "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-profile:v", "high",
           "-movflags", "+faststart", "-shortest", str(out)]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(4) as pool:
        for k, buf in enumerate(pool.imap(frame, range(nframes), chunksize=8)):
            ff.stdin.write(buf)
            if k % 600 == 0:
                print(f"{k}/{nframes}", flush=True)
    ff.stdin.close()
    ff.wait()
    print("ok", out, f"{TOTAL:.1f} s", nframes, "cuadros")
