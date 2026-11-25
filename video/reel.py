"""Versión vertical para Instagram (Reels / historias): 1080×1920, ~42 s.

Uso:
  python3 video/reel.py html      → video/reel/*.html
  PW=$(npm root -g)/playwright node video/capturas.js reel   → PNG de cada escena
  python3 video/reel.py montaje   → video/ESLA-reel-instagram.mp4

Zonas seguras de Instagram: se deja libre la franja superior (~250 px) y la inferior (~380 px).
"""
import html
import re
import subprocess
import sys
import wave
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
SITE = ROOT.parent
OUT = ROOT / "reel"
OUT.mkdir(exist_ok=True)
W, H, FPS, FADE = 1080, 1920, 30, 0.6
e = html.escape

SCENES = ["intro", "firma", "areas", "fideicomisos", "equipo", "prensa", "aliada", "cierre"]
DURS = [5.0, 4.5, 5.0, 4.0, 5.0, 4.5, 4.5, 9.5]  # total 42 s

FONTS = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow:wght@300;400;500&family=Cinzel:wght@500;700&family=Manrope:wght@500;600;700&display=swap">'
MARK = ('<svg class="mark" viewBox="0 0 100 100"><rect x="2" y="2" width="96" height="96" rx="14" fill="#C07D46"/>'
        '<rect x="8" y="8" width="84" height="84" rx="10" fill="none" stroke="#FFF" stroke-width="2.4"/>'
        '<path d="M27 50 H73 V38 Q73 28 63 28 H37 Q27 28 27 38 V62 Q27 72 37 72 H70" fill="none" stroke="#FFF" stroke-width="12" stroke-linejoin="round"/></svg>')
CSS = """
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1080px;height:1920px;overflow:hidden}
body{font-family:Manrope,Arial,sans-serif;color:#DCE0EA;position:relative;background:radial-gradient(130% 90% at 20% 10%,#24345A 0%,#1F2B48 40%,#151E33 100%)}
.safe{position:absolute;left:90px;right:110px;top:260px;bottom:400px;display:flex;flex-direction:column}
.brand{display:flex;align-items:center;gap:22px}
.mark{width:84px;height:84px;flex:none}
.brand b{display:block;font:700 52px/1 Cinzel,serif;letter-spacing:.08em;color:#fff}
.brand span{display:block;margin-top:10px;font:500 15px/1 Cinzel,serif;letter-spacing:.2em;text-transform:uppercase;color:#D9B48C}
.kicker{font:700 24px/1.3 Manrope;letter-spacing:.22em;text-transform:uppercase;color:#D9B48C}
h1{font:400 78px/1.06 Barlow,Arial;color:#fff;margin:18px 0 26px}
h2{font:400 64px/1.08 Barlow,Arial;color:#fff;margin:16px 0 24px}
.rule{width:110px;height:4px;background:#AE7B4A;margin:4px 0 30px}
p.lead{font:300 38px/1.4 Barlow,Arial;color:#DCE0EA}
ul.list{list-style:none}
ul.list li{font:400 38px/1.25 Barlow;color:#fff;padding:16px 0 16px 38px;border-bottom:1px solid rgba(255,255,255,.14);position:relative}
ul.list li::before{content:"";position:absolute;left:0;top:36px;width:20px;height:3px;background:#AE7B4A}
.photo{border-radius:6px;overflow:hidden;box-shadow:0 24px 60px rgba(0,0,0,.5)}
.photo img{display:block;width:100%;height:100%;object-fit:cover}
.small{font:500 22px/1.5 Manrope;color:#9AA3B6}
"""


def doc(body, extra=""):
    return f'<!doctype html><html lang="es"><head><meta charset="utf-8">{FONTS}<style>{CSS}{extra}</style></head><body>{body}</body></html>'


def a(p):
    return f"../../assets/{p}"


def build_html():
    src = (SITE / "index.html").read_text(encoding="utf-8")
    areas = [html.unescape(x) for x in re.findall(r'<article class="tile"[^>]*>\s*<div class="ph"><img[^>]*><h3><span lang="es">([^<]*)</span>', src)]
    team = re.findall(r'<div class="portrait">\s*<img src="assets/([^"]+)" alt="([^"]+)"', src)
    assert len(areas) == 10 and len(team) == 9, (len(areas), len(team))
    pages = {}
    pages["intro"] = doc(f'''<img class="bg" src="{a("img-justicia.jpg")}"><div class="shade"></div>
<div class="safe"><div class="brand">{MARK}<div><b>ESLA</b><span>Abogados Consultores</span></div></div>
<div style="margin-top:auto"><p class="kicker">Abogados consultores · Santo Domingo</p>
<h1 style="font-size:96px">Estructuramos sus negocios.<br>Defendemos sus contratos.</h1>
<p class="lead">Derecho mercantil, corporativo y fiduciario, y litigación civil y contractual.</p></div></div>''',
        ".bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:38% 40%}"
        ".shade{position:absolute;inset:0;background:linear-gradient(180deg,rgba(21,30,51,.55) 0%,rgba(21,30,51,.35) 35%,rgba(21,30,51,.92) 72%,#151E33 100%)}")
    pages["firma"] = doc(f'''<div class="safe"><p class="kicker">La firma</p><h2>Una firma dirigida por sus socios</h2><div class="rule"></div>
<div class="photo" style="height:700px"><img src="{a("socios-biblioteca.jpg")}" style="object-position:50% 30%"></div>
<ul class="list" style="margin-top:34px"><li>Atención directa de los socios</li><li>Honorarios claros por escrito</li><li>Más de 20 años de ejercicio</li></ul></div>''')
    lis = "".join(f"<li>{e(x)}</li>" for x in areas)
    pages["areas"] = doc(f'''<div class="safe"><p class="kicker">Áreas de práctica</p><h2>Diez áreas, un mismo estándar</h2><div class="rule"></div>
<ul class="list compact">{lis}</ul></div>''', ".compact li{font-size:34px;padding:12px 0 12px 36px}.compact li::before{top:30px}")
    pages["fideicomisos"] = doc(f'''<div class="photo top"><img src="{a("img-boveda.jpg")}"></div><div class="shade"></div>
<div class="safe" style="justify-content:flex-end"><p class="kicker">Ley 189-11</p><h2>Fideicomisos</h2><div class="rule"></div>
<ul class="list"><li>De administración</li><li>Inmobiliario</li><li>De garantía</li><li>Corporativo y societario</li></ul></div>''',
        ".top{position:absolute;left:0;right:0;top:0;height:1150px;border-radius:0;box-shadow:none}"
        ".shade{position:absolute;left:0;right:0;top:0;height:1150px;background:linear-gradient(180deg,rgba(21,30,51,.2),#151E33 98%)}")
    cells = "".join(f'<figure><img src="{a(f)}"><figcaption>{e(n)}</figcaption></figure>' for f, n in team)
    pages["equipo"] = doc(f'''<div class="safe"><p class="kicker">Nuestro equipo</p><h2>Socios, asociados y equipo</h2><div class="rule"></div>
<div class="grid">{cells}</div></div>''',
        ".grid{display:grid;grid-template-columns:repeat(3,1fr);gap:22px 20px}"
        ".grid figure{margin:0}.grid img{display:block;width:100%;height:330px;object-fit:cover;object-position:50% 15%;border-radius:4px}"
        ".grid figcaption{font:500 17px/1.3 Manrope;color:#DCE0EA;margin-top:8px}")
    pages["prensa"] = doc(f'''<div class="safe"><p class="kicker">Prensa y reconocimientos</p><h2>Reconocidos por nuestro trabajo</h2><div class="rule"></div>
<div class="photo" style="height:auto"><img src="{a("prensa-mercado-encabezado.jpg")}" style="height:auto"></div>
<ul class="list" style="margin-top:30px"><li>Top Lawyers · Revista Mercado, 2026</li><li>Libro Best Lawyers II · Revista Mercado</li>
<li>The Law Awards 2025 · LAQI</li><li>Certificación Q-ESG · LAQI Impact Summit</li><li>Seleccionada, Excellence in Law Awards 2025</li></ul></div>''',
        ".list li{font-size:34px}")
    pages["aliada"] = doc(f'''<div class="safe"><p class="kicker">Presencia internacional</p><h2>También en Filadelfia, EE. UU.</h2><div class="rule"></div>
<div class="row"><div class="photo" style="width:400px;height:500px;flex:none"><img src="{a("fjerez.jpg")}"></div>
<div><h3>Franny Jerez Morales</h3><p class="role">Aliada comercial</p><p class="txt">Apoyo migratorio y documental para la comunidad dominicana, en coordinación con ESLA.</p></div></div>
<ul class="list" style="margin-top:36px"><li>7810 Castor Avenue, Philadelphia, PA 19152</li><li>+1 (215) 618-7514</li></ul>
<p class="small" style="margin-top:22px">La Sra. Jerez Morales no es abogada y no ofrece asesoría legal. ESLA ejerce el derecho únicamente en la República Dominicana.</p></div>''',
        ".row{display:flex;gap:36px;align-items:flex-start}.row h3{font:500 44px/1.15 Barlow;color:#fff}"
        ".role{font:700 20px/1.4 Manrope;letter-spacing:.18em;text-transform:uppercase;color:#D9B48C;margin:10px 0 18px}.txt{font:300 32px/1.4 Barlow}")
    pages["cierre"] = doc(f'''<div class="safe"><div class="brand">{MARK}<div><b>ESLA</b><span>Abogados Consultores</span></div></div>
<h1 style="margin-top:110px">Agende su consulta</h1><div class="rule"></div>
<p class="kicker" style="margin-top:10px">WhatsApp</p><p class="big">+1 (829) 539-3700</p>
<ul class="list" style="margin-top:26px"><li>+1 (809) 960-2992</li><li>info@eslard.com</li><li>Av. Abraham Lincoln No. 605, Naco, Santo Domingo</li><li>@esla_rd · www.eslard.com</li></ul>
<p class="small" style="margin-top:auto">Contenido informativo; no constituye asesoría legal. Música original compuesta para ESLA. © 2026 ESLA Abogados Consultores, SRL.</p></div>''',
        ".big{font:400 92px/1.05 Barlow;color:#fff;margin-top:10px}.list li{font-size:34px}")
    for name in SCENES:
        (OUT / f"{name}.html").write_text(pages[name], encoding="utf-8")
    (OUT / "lista.txt").write_text("\n".join(SCENES), encoding="utf-8")
    print("ok html", len(SCENES))


def build_music():
    """Recorte de video/musica.wav: tema (37,5–70 s) + cadencia final (112,5–122,5 s)."""
    with wave.open(str(ROOT / "musica.wav")) as w:
        sr = w.getframerate()
        x = np.frombuffer(w.readframes(w.getnframes()), "<i2").reshape(-1, 2).astype(np.float32) / 32768
    A = x[int(37.5 * sr):int(70.0 * sr)].copy()
    B = x[int(112.5 * sr):int(122.5 * sr)].copy()
    xf = int(0.35 * sr)
    ramp = np.linspace(0, 1, xf)[:, None]
    mix = np.concatenate([A[:-xf], A[-xf:] * (1 - ramp) + B[:xf] * ramp, B[xf:]])
    fi = int(0.4 * sr)
    mix[:fi] *= np.linspace(0, 1, fi)[:, None]
    out = ROOT / "musica-reel.wav"
    with wave.open(str(out), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((np.clip(mix, -1, 1) * 32767).astype("<i2").tobytes())
    return out, len(mix) / sr


IMGS = {}
STARTS = np.concatenate([[0], np.cumsum(DURS)[:-1]])
TOTAL = float(sum(DURS))


def img(i):
    if i not in IMGS:
        IMGS[i] = Image.open(OUT / f"{SCENES[i]}.png").convert("RGB")
    return IMGS[i]


def render(i, local):
    im = img(i)
    sw = im.width / W
    p = min(max(local / DURS[i], 0), 1)
    p = p * p * (3 - 2 * p)
    z = 1.0 + 0.04 * p
    k = sw / z
    cx, cy = 0.5 * im.width, 0.5 * im.height
    return np.asarray(im.transform((W, H), Image.AFFINE, (k, 0, cx - k * W / 2, 0, k, cy - k * H / 2), resample=Image.BICUBIC), dtype=np.float32)


def frame(n):
    t = n / FPS
    i = int(np.searchsorted(STARTS, t, side="right") - 1)
    local = t - STARTS[i]
    out = render(i, local)
    rem = DURS[i] - local
    if rem < FADE and i + 1 < len(SCENES):
        q = 1 - rem / FADE
        q = q * q * (3 - 2 * q)
        out = out * (1 - q) + render(i + 1, local - DURS[i]) * q
    if t < 0.5:
        out *= t / 0.5
    if TOTAL - t < 1.2:
        out *= max(TOTAL - t, 0) / 1.2
    return np.clip(out, 0, 255).astype(np.uint8).tobytes()


def montaje():
    music, mdur = build_music()
    print(f"música {mdur:.1f} s · video {TOTAL:.1f} s")
    nframes = int(round(TOTAL * FPS))
    out = ROOT / "ESLA-reel-instagram.mp4"
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", str(music), "-filter:a", f"atrim=0:{TOTAL},afade=t=out:st={TOTAL - 1.5}:d=1.5,loudnorm=I=-14:TP=-1.5:LRA=11",
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
           "-pix_fmt", "yuv420p", "-profile:v", "high", "-movflags", "+faststart", "-shortest", str(out)]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(4) as pool:
        for buf in pool.imap(frame, range(nframes), chunksize=8):
            ff.stdin.write(buf)
    ff.stdin.close()
    ff.wait()
    print("ok", out)


if __name__ == "__main__":
    build_html() if sys.argv[1] == "html" else montaje()
