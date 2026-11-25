"""Reels verticales cortos (≈18 s), uno por área de práctica, para Instagram (sin audio: la música se agrega en Instagram).

Uso:
  python3 video/reels_areas.py html        → video/reels/*.html  (40 escenas)
  PW=$(npm root -g)/playwright node video/capturas.js reels
  python3 video/reels_areas.py montaje     → video/reels-areas/ESLA-reel-NN-<area>.mp4

El contenido (nombre, base legal, descripción y servicios) sale de index.html.
"""
import html
import re
import subprocess
import sys
import unicodedata
import wave
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
SITE = ROOT.parent
OUT = ROOT / "reels"
OUT.mkdir(exist_ok=True)
FINAL = ROOT / "reels-areas"
FINAL.mkdir(exist_ok=True)
W, H, FPS, FADE = 1080, 1920, 30, 0.5
DURS = [3.6, 4.6, 5.0, 5.3]  # 18,5 s
e = html.escape

HOOKS = {
    "Corporativo y Societario": "¿Su empresa tiene sus estatutos y actas al día?",
    "Fideicomisos": "¿Quiere proteger su patrimonio o desarrollar un proyecto con reglas claras?",
    "Contratos y Mercantil": "¿Firmaría un contrato sin conocer sus puntos débiles?",
    "Litigación Civil y Arbitraje": "¿Un contrato incumplido le está costando dinero?",
    "Derecho Penal": "¿Enfrenta un proceso penal o fue víctima de un delito económico?",
    "Cobros y Recuperación": "¿Tiene facturas vencidas que no logra cobrar?",
    "Planificación Patrimonial y Sucesoral": "¿Está preparada su familia empresaria para la siguiente generación?",
    "Inmobiliario y Registral": "¿Va a comprar un inmueble? Verifique antes de firmar.",
    "Servicios Notariales": "¿Necesita un poder, una declaración jurada o legalizar una firma?",
    "Familia y Adopciones": "Los asuntos de familia merecen prudencia y reserva.",
}

FONTS = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow:wght@300;400;500&family=Cinzel:wght@500;700&family=Manrope:wght@500;600;700&display=swap">'
MARK = ('<svg class="mark" viewBox="0 0 100 100"><rect x="2" y="2" width="96" height="96" rx="14" fill="#C07D46"/>'
        '<rect x="8" y="8" width="84" height="84" rx="10" fill="none" stroke="#FFF" stroke-width="2.4"/>'
        '<path d="M27 50 H73 V38 Q73 28 63 28 H37 Q27 28 27 38 V62 Q27 72 37 72 H70" fill="none" stroke="#FFF" stroke-width="12" stroke-linejoin="round"/></svg>')
CSS = """
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1080px;height:1920px;overflow:hidden}
body{font-family:Manrope,Arial,sans-serif;color:#DCE0EA;position:relative;background:radial-gradient(130% 90% at 20% 10%,#24345A 0%,#1F2B48 40%,#151E33 100%)}
.safe{position:absolute;left:90px;right:110px;top:260px;bottom:400px;display:flex;flex-direction:column}
.top{position:absolute;left:0;right:0;top:0;height:1100px;overflow:hidden}
.top img{width:100%;height:100%;object-fit:cover}
.top::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(21,30,51,.35) 0%,rgba(21,30,51,.25) 40%,#151E33 100%)}
.brand{display:flex;align-items:center;gap:18px}
.mark{width:64px;height:64px;flex:none}
.brand b{display:block;font:700 40px/1 Cinzel,serif;letter-spacing:.08em;color:#fff}
.brand span{display:block;margin-top:8px;font:500 12px/1 Cinzel,serif;letter-spacing:.2em;text-transform:uppercase;color:#D9B48C}
.kicker{font:700 23px/1.3 Manrope;letter-spacing:.22em;text-transform:uppercase;color:#D9B48C}
h1{font:400 92px/1.04 Barlow,Arial;color:#fff;margin:16px 0 26px}
h2{font:400 66px/1.08 Barlow,Arial;color:#fff;margin:14px 0 22px}
.rule{width:110px;height:4px;background:#AE7B4A;margin:2px 0 30px}
p.lead{font:300 42px/1.38 Barlow,Arial;color:#fff}
p.ref{font:700 22px/1.5 Manrope;letter-spacing:.12em;text-transform:uppercase;color:#D9B48C;margin-top:34px}
ul.list{list-style:none}
ul.list li{font:400 44px/1.22 Barlow;color:#fff;padding:22px 0 22px 42px;border-bottom:1px solid rgba(255,255,255,.14);position:relative}
ul.list li::before{content:"";position:absolute;left:0;top:46px;width:22px;height:3px;background:#AE7B4A}
.series{font:600 20px/1 Manrope;letter-spacing:.2em;color:#9AA3B6}
.big{font:400 96px/1.05 Barlow;color:#fff;margin-top:8px}
.small{font:500 21px/1.5 Manrope;color:#9AA3B6}
"""


def doc(body):
    return f'<!doctype html><html lang="es"><head><meta charset="utf-8">{FONTS}<style>{CSS}</style></head><body>{body}</body></html>'


def es(fragment):
    f = re.sub(r'<span lang="en">.*?</span>', "", fragment, flags=re.S)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", f))).strip()


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def areas():
    src = (SITE / "index.html").read_text(encoding="utf-8")
    sec = src[src.index('id="areas"'):]
    out = []
    for art in re.findall(r'<article class="tile"[^>]*>(.*?)</article>', sec, re.S):
        out.append(dict(
            img=re.search(r'<img src="([^"]+)"', art).group(1),
            name=es(re.search(r"<h3>(.*?)</h3>", art, re.S).group(1)),
            ref=es(re.search(r'<span class="ref">(.*?)</span>\s*<p>', art, re.S).group(1)),
            desc=es(re.search(r"</span>\s*<p>(.*?)</p>", art, re.S).group(1)),
            items=[es(x) for x in re.findall(r"<li>(.*?)</li>", art, re.S)],
        ))
    assert len(out) == 10
    return out


def build_html():
    names = []
    for k, ar in enumerate(areas(), 1):
        tag = f"{k:02d}"
        series = f'<p class="series">ÁREAS DE PRÁCTICA · {tag}/10</p>'
        scenes = [
            f'''<div class="top"><img src="../../{ar["img"]}"></div>
<div class="safe"><div class="brand">{MARK}<div><b>ESLA</b><span>Abogados Consultores</span></div></div>
<div style="margin-top:auto">{series}<h1>{e(ar["name"])}</h1><div class="rule"></div><p class="lead">{e(HOOKS[ar["name"]])}</p></div></div>''',
            f'''<div class="safe" style="justify-content:center">{series}<h2>{e(ar["name"])}</h2><div class="rule"></div>
<p class="lead">{e(ar["desc"])}</p><p class="ref">Base legal: {e(ar["ref"])}</p></div>''',
            f'''<div class="safe" style="justify-content:center"><p class="kicker">Cómo le ayudamos</p><h2>{e(ar["name"])}</h2><div class="rule"></div>
<ul class="list">{"".join(f"<li>{e(x)}</li>" for x in ar["items"])}</ul></div>''',
            f'''<div class="safe"><div class="brand">{MARK}<div><b>ESLA</b><span>Abogados Consultores</span></div></div>
<h2 style="margin-top:120px">¿Necesita asesoría en {e(ar["name"].lower() if ar["name"] not in ("Fideicomisos",) else "fideicomisos")}?</h2><div class="rule"></div>
<p class="kicker">Escríbanos por WhatsApp</p><p class="big">+1 (829) 539-3700</p>
<p class="lead" style="margin-top:34px;font-size:36px">info@eslard.com · @esla_rd</p>
<p class="small" style="margin-top:auto">Contenido informativo; no constituye asesoría legal. El contacto no crea una relación abogado-cliente.</p></div>''',
        ]
        for j, body in enumerate(scenes):
            n = f"r{tag}_{j}"
            (OUT / f"{n}.html").write_text(doc(body), encoding="utf-8")
            names.append(n)
    (OUT / "lista.txt").write_text("\n".join(names), encoding="utf-8")
    print("ok html", len(names))


# ------------------------------------------------------------------ montaje
CUR = {}


def render(i, local):
    im = CUR["imgs"][i]
    sw = im.width / W
    p = min(max(local / DURS[i], 0), 1)
    p = p * p * (3 - 2 * p)
    z = 1.0 + (0.06 if i == 0 else 0.03) * p
    k = sw / z
    cx, cy = 0.5 * im.width, 0.5 * im.height
    return np.asarray(im.transform((W, H), Image.AFFINE, (k, 0, cx - k * W / 2, 0, k, cy - k * H / 2), resample=Image.BICUBIC), dtype=np.float32)


def frame(n):
    starts = np.concatenate([[0], np.cumsum(DURS)[:-1]])
    total = sum(DURS)
    t = n / FPS
    i = int(np.searchsorted(starts, t, side="right") - 1)
    local = t - starts[i]
    out = render(i, local)
    rem = DURS[i] - local
    if rem < FADE and i + 1 < len(DURS):
        q = 1 - rem / FADE
        q = q * q * (3 - 2 * q)
        out = out * (1 - q) + render(i + 1, local - DURS[i]) * q
    if t < 0.3:
        out *= t / 0.3
    if total - t < 0.8:
        out *= max(total - t, 0) / 0.8
    return np.clip(out, 0, 255).astype(np.uint8).tobytes()


def init(tag):
    CUR["imgs"] = [Image.open(OUT / f"r{tag}_{j}.png").convert("RGB") for j in range(4)]


def music(k):
    """Tema (5 compases desde el c. 16, 24 o 32) + acorde final (c. 46)."""
    with wave.open(str(ROOT / "musica.wav")) as w:
        sr = w.getframerate()
        x = np.frombuffer(w.readframes(w.getnframes()), "<i2").reshape(-1, 2).astype(np.float32) / 32768
    bar = 2.5
    start = [16, 24, 32][k % 3] * bar
    A = x[int(start * sr):int((start + 5 * bar) * sr)].copy()
    B = x[int(46 * bar * sr):int(122.5 * sr)].copy()
    xf = int(0.3 * sr)
    r = np.linspace(0, 1, xf)[:, None]
    mix = np.concatenate([A[:-xf], A[-xf:] * (1 - r) + B[:xf] * r, B[xf:]])
    fi = int(0.25 * sr)
    mix[:fi] *= np.linspace(0, 1, fi)[:, None]
    out = OUT / f"musica-{k}.wav"
    with wave.open(str(out), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((np.clip(mix, -1, 1) * 32767).astype("<i2").tobytes())
    return out


def montaje():
    total = sum(DURS)
    nframes = int(round(total * FPS))
    for k, ar in enumerate(areas(), 1):
        tag = f"{k:02d}"
        out = FINAL / f"ESLA-reel-{tag}-{slug(ar['name'])}.mp4"
        cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
               "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
               "-pix_fmt", "yuv420p", "-profile:v", "high", "-movflags", "+faststart", str(out)]
        ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        with Pool(4, initializer=init, initargs=(tag,)) as pool:
            for buf in pool.imap(frame, range(nframes), chunksize=6):
                ff.stdin.write(buf)
        ff.stdin.close()
        ff.wait()
        print("ok", out.name, flush=True)


if __name__ == "__main__":
    build_html() if sys.argv[1] == "html" else montaje()
