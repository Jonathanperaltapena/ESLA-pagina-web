"""Genera los cuadros (HTML) del video institucional a partir del libro impreso.

Uso: python3 video/cuadros.py   →  video/cuadros/*.html  (luego video/capturas.js los convierte en PNG)
"""
import html
import re
import subprocess
from pathlib import Path

import segno

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "video" / "cuadros"
OUT.mkdir(parents=True, exist_ok=True)
PDF = ROOT / "impresos" / "ESLA-presentacion-institucional.pdf"
e = html.escape

# Páginas del libro en PNG (150 ppp)
subprocess.run(["pdftoppm", "-r", "150", "-png", "-f", "3", "-l", "19", str(PDF), str(OUT / "pag")], check=True)

src = (ROOT / "index.html").read_text(encoding="utf-8")
areas = [re.sub(r"<[^>]+>", "", html.unescape(a)) for a in
         re.findall(r'<article class="tile"[^>]*>\s*<div class="ph"><img[^>]*><h3><span lang="es">([^<]*)</span>', src)]
assert len(areas) == 10

SEG = [  # (página, antetítulo, título, línea)
    (3, "Quiénes somos", "La firma", "Una firma dominicana dirigida por sus socios, con atención directa y honorarios claros por escrito."),
    (4, "Áreas de práctica", f"{areas[0]} · {areas[1]}", "Diez áreas de práctica, cada una con su base legal a la vista."),
    (5, "Áreas de práctica", f"{areas[2]} · {areas[3]}", "Contratos que se cumplen y que se defienden, hasta la Suprema Corte de Justicia."),
    (6, "Áreas de práctica", f"{areas[4]} · {areas[5]}", "Defensa penal y recuperación de créditos, con orden y estrategia."),
    (7, "Áreas de práctica", f"{areas[6]} · {areas[7]}", "Patrimonio familiar ordenado y operaciones inmobiliarias seguras."),
    (8, "Áreas de práctica", f"{areas[8]} · {areas[9]}", "Rigor notarial y acompañamiento a las familias con prudencia y reserva."),
    (9, "Ley 189-11", "Fideicomisos: cuatro figuras", "Administración, inmobiliario, garantía y corporativo."),
    (10, "Nuestro equipo", "Socios", "Lic. Jonathan Abel Peralta Peña · Licda. Miriam Estévez Lavandier"),
    (11, "Nuestro equipo", "Asociados", "Especialistas a cargo de cada área de práctica."),
    (12, "Nuestro equipo", "El equipo y responsables por área", "Cada asunto, con un responsable identificado."),
    (13, "Presencia internacional", "Aliada en Estados Unidos", "Franny Jerez Morales, en Filadelfia, Pensilvania: apoyo migratorio y documental para la comunidad dominicana."),
    (14, "Publicaciones y prensa", "Prensa y reconocimientos", "Revista Mercado · The Law Awards 2025 · Certificación Q-ESG"),
    (15, "Publicaciones y prensa", "Entrevistas y publicaciones", "Nuestra visión de la práctica legal, en sus propias palabras."),
    (16, "Publicaciones y prensa", "Próximas publicaciones", "Guías prácticas para inversionistas, empresas y familias."),
    (17, "Referencia", "Legislación de interés", "Las normas que más consultan nuestros clientes."),
    (18, "Nuestro método", "Cómo trabajamos", "Del primer contacto a la ejecución, con transparencia en cada paso."),
    (19, "Hablemos", "Contacto", "Av. Abraham Lincoln No. 605, Naco, Santo Domingo"),
]

FONTS = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow:wght@300;400;500&family=Cinzel:wght@500;700&family=Manrope:wght@500;600;700&display=swap">'
MARK = ('<svg class="mark" viewBox="0 0 100 100"><rect x="2" y="2" width="96" height="96" rx="14" fill="#C07D46"/>'
        '<rect x="8" y="8" width="84" height="84" rx="10" fill="none" stroke="#FFF" stroke-width="2.4"/>'
        '<path d="M27 50 H73 V38 Q73 28 63 28 H37 Q27 28 27 38 V62 Q27 72 37 72 H70" fill="none" stroke="#FFF" stroke-width="12" stroke-linejoin="round"/></svg>')
CSS = """
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1920px;height:1080px;overflow:hidden;background:#151E33}
body{font-family:Manrope,Arial,sans-serif;color:#DCE0EA;position:relative;background:radial-gradient(120% 140% at 15% 20%,#24345A 0%,#1F2B48 38%,#151E33 100%)}
.brand{display:flex;align-items:center;gap:22px}
.mark{width:74px;height:74px;flex:none}
.brand b{display:block;font:700 44px/1 Cinzel,serif;letter-spacing:.08em;color:#fff}
.brand span{display:block;margin-top:9px;font:500 13px/1 Cinzel,serif;letter-spacing:.2em;text-transform:uppercase;color:#D9B48C}
.kicker{font:700 20px/1.3 Manrope;letter-spacing:.24em;text-transform:uppercase;color:#D9B48C}
.left{position:absolute;left:150px;top:0;bottom:0;width:820px;display:flex;flex-direction:column;justify-content:center}
.left h1{font:400 70px/1.08 Barlow,Arial;color:#fff;margin:22px 0 30px}
.left .rule{width:120px;height:3px;background:#AE7B4A;margin-bottom:30px}
.left p{font:300 30px/1.45 Barlow,Arial;color:#DCE0EA;max-width:740px}
.foot{position:absolute;left:150px;bottom:70px;display:flex;align-items:center;gap:18px}
.foot .mark{width:44px;height:44px}
.foot span{font:600 15px/1 Manrope;letter-spacing:.22em;text-transform:uppercase;color:#9AA3B6}
.page{position:absolute;right:150px;top:70px;height:940px;box-shadow:0 30px 70px rgba(0,0,0,.55),0 0 0 1px rgba(255,255,255,.06)}
.counter{position:absolute;right:150px;bottom:28px;font:500 16px/1 Barlow;letter-spacing:.16em;color:#9AA3B6}
"""


def doc(body, extra=""):
    return f'<!doctype html><html lang="es"><head><meta charset="utf-8">{FONTS}<style>{CSS}{extra}</style></head><body>{body}</body></html>'


files = []
# Intro
intro = doc(f'''<img class="bg" src="../../assets/img-justicia.jpg">
<div class="shade"></div>
<div class="in">
  <div class="brand">{MARK}<div><b>ESLA</b><span>Abogados Consultores</span></div></div>
  <p class="kicker" style="margin-top:90px">Presentación institucional</p>
  <h1>Estructuramos sus negocios.<br>Defendemos sus contratos.</h1>
  <p class="sub">Derecho mercantil, corporativo y fiduciario, y litigación civil y contractual, con los socios al frente de cada asunto.</p>
</div>''', """
.bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:50% 30%}
.shade{position:absolute;inset:0;background:linear-gradient(90deg,rgba(21,30,51,.94) 0%,rgba(21,30,51,.78) 45%,rgba(21,30,51,.35) 100%)}
.in{position:absolute;left:150px;top:0;bottom:0;width:1100px;display:flex;flex-direction:column;justify-content:center}
.in h1{font:400 86px/1.05 Barlow;color:#fff;margin:22px 0 30px}
.in .sub{font:300 32px/1.45 Barlow;max-width:900px}
.mark{width:96px;height:96px}.brand b{font-size:58px}.brand span{font-size:16px}
""")
(OUT / "s00.html").write_text(intro, encoding="utf-8")
files.append("s00")

for i, (pg, k, t, line) in enumerate(SEG, 1):
    body = f'''<div class="left"><p class="kicker">{e(k)}</p><h1>{e(t)}</h1><div class="rule"></div><p>{e(line)}</p></div>
<div class="foot">{MARK}<span>ESLA Abogados Consultores</span></div>
<img class="page" src="pag-{pg:02d}.png">'''
    (OUT / f"s{i:02d}.html").write_text(doc(body), encoding="utf-8")
    files.append(f"s{i:02d}")

wa = segno.make("https://wa.me/18295393700?text=Hola%2C%20ESLA%20Abogados%20Consultores.%20Me%20gustar%C3%ADa%20agendar%20una%20consulta.%20Mi%20nombre%20es%3A%20", error="m").svg_inline(scale=8, border=2, dark="#1F2B48", light="#FFFFFF")
outro = doc(f'''<div class="o">
  <div class="brand">{MARK}<div><b>ESLA</b><span>Abogados Consultores</span></div></div>
  <h1>Hablemos de su próximo paso.</h1>
  <ul>
    <li><span>WhatsApp</span>+1 (829) 539-3700</li>
    <li><span>Teléfono</span>+1 (809) 960-2992</li>
    <li><span>Correo</span>info@eslard.com</li>
    <li><span>Oficina</span>Av. Abraham Lincoln No. 605, Naco, Santo Domingo</li>
    <li><span>Web · Instagram</span>www.eslard.com · @esla_rd</li>
    <li><span>Filadelfia (EE. UU.)</span>7810 Castor Avenue · +1 (215) 618-7514</li>
  </ul>
</div>
<figure class="qr">{wa}<figcaption>Escríbanos por WhatsApp</figcaption></figure>
<p class="legal">La información de esta presentación es general y no constituye asesoría legal. El contacto con la firma no crea una relación abogado-cliente hasta que el encargo se formaliza por escrito.<br>Música original compuesta para ESLA Abogados Consultores. Créditos fotográficos en la presentación impresa. © 2026 ESLA Abogados Consultores, SRL.</p>''', """
.o{position:absolute;left:150px;top:110px;width:1100px}
.o h1{font:400 70px/1.08 Barlow;color:#fff;margin:56px 0 34px}
.o ul{list-style:none}
.o li{font:400 32px/1.3 Barlow;color:#fff;padding:16px 0;border-bottom:1px solid rgba(255,255,255,.14);display:flex;gap:30px}
.o li span{width:250px;flex:none;font:700 16px/2.4 Manrope;letter-spacing:.2em;text-transform:uppercase;color:#D9B48C}
.qr{position:absolute;right:190px;top:330px;width:400px;text-align:center}
.qr svg{width:400px;height:400px;display:block;border-radius:6px}
.qr figcaption{margin-top:22px;font:700 17px/1 Manrope;letter-spacing:.2em;text-transform:uppercase;color:#D9B48C}
.legal{position:absolute;left:150px;right:150px;bottom:50px;font:500 14px/1.6 Manrope;color:#8C95A8}
""")
(OUT / "s99.html").write_text(outro, encoding="utf-8")
files.append("s99")
(OUT / "lista.txt").write_text("\n".join(files), encoding="utf-8")
print("ok", len(files), "cuadros")
