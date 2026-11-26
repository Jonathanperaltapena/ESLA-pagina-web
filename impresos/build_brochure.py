"""Genera la presentación institucional impresa (tipo libro) a partir de index.html.

Uso:  python3 impresos/build_brochure.py
Salida: impresos/brochure.html  (luego impresos/pdf.js lo convierte en PDF tamaño Carta)

El contenido sale de index.html (versión en español), así que el libro se mantiene
al día con la página: áreas, fideicomisos, equipo, prensa, legislación y contacto.
"""
import html
import re
from pathlib import Path

import segno

ROOT = Path(__file__).resolve().parent.parent
SRC = (ROOT / "index.html").read_text(encoding="utf-8")
OUT = ROOT / "impresos" / "brochure.html"
EDICION = "Noviembre de 2026"


# ------------------------------------------------------------------ helpers
def es(fragment: str) -> str:
    """Texto en español de un fragmento HTML de la página."""
    f = re.sub(r'<span lang="en">.*?</span>', "", fragment, flags=re.S)
    f = re.sub(r'<a [^>]*lang="en"[^>]*>.*?</a>', "", f, flags=re.S)
    f = re.sub(r"<svg.*?</svg>", "", f, flags=re.S)
    f = re.sub(r"<[^>]+>", "", f)
    return re.sub(r"\s+", " ", html.unescape(f)).strip()


def one(pattern, text, default=""):
    m = re.search(pattern, text, re.S)
    return m.group(1) if m else default


def section(id_):
    a = SRC.index(f'id="{id_}"')
    b = SRC.index("</section>", a)
    return SRC[a:b]


def qr(url, scale=3):
    return segno.make(url, error="m").svg_inline(scale=scale, border=0, dark="#1F2B48")


e = html.escape

# ------------------------------------------------------------------ content
firm = section("firma")
firm_text = es(one(r'<p>\s*(<span lang="es">ESLA Abogados.*?)</p>', firm))
firm_quote = es(one(r'<p class="firm-quote">(.*?)<small>', firm))
firm_quote_src = es(one(r"<small>(.*?)</small>", firm))

dual = re.findall(r'<figure>.*?<img src="([^"]+)".*?<span class="kicker">(.*?)</span>\s*<h3>(.*?)</h3>\s*<p>(.*?)</p>', SRC[SRC.index('class="dual"'):], re.S)[:2]
dual = [(img, es(k), es(h), es(p)) for img, k, h, p in dual]

areas_sec = section("areas")
areas_intro = es(one(r'<p class="intro">(.*?)</p>', areas_sec))
tiles = []
for art in re.findall(r'<article class="tile"[^>]*>(.*?)</article>', areas_sec, re.S):
    tiles.append(dict(
        img=one(r'<img src="([^"]+)"', art),
        name=es(one(r"<h3>(.*?)</h3>", art)),
        ref=es(one(r'<span class="ref">(.*?)</span>\s*<p>', art)),
        desc=es(one(r"</span>\s*<p>(.*?)</p>", art)),
        items=[es(li) for li in re.findall(r"<li>(.*?)</li>", art)],
    ))
assert len(tiles) == 10, len(tiles)

fid = section("fideicomisos")
fid_title = es(one(r"<h2[^>]*>(.*?)</h2>", fid))
fid_intro = es(one(r'<p class="intro">(.*?)</p>', fid))
trusts = []
for art in re.findall(r'<article class="trust"[^>]*>(.*?)</article>', fid, re.S):
    trusts.append(dict(img=one(r'<img src="([^"]+)"', art), n=es(one(r'<span class="n">(.*?)</span>', art)),
                       name=es(one(r"<h3>(.*?)</h3>", art)), desc=es(one(r"</h3><p>(.*?)</p>", art))))
assert len(trusts) == 4

strip = [(es(q), es(s)) for q, s in re.findall(r"<li><q>(.*?)</q><small>(.*?)</small></li>", SRC)]

team_sec = section("socios")
team_intro = es(one(r'<p class="intro">(.*?)</p>', team_sec))
groups = {}
for title, block in re.findall(r'<h3 class="sub-title"[^>]*>(.*?)</h3>\s*<div class="partners">(.*?)\n    </div>\n', team_sec, re.S):
    people = []
    for art in re.findall(r'<article class="partner[^"]*">(.*?)</article>', block, re.S):
        cv = []
        for dt, dd in re.findall(r"<dt>(.*?)</dt>\s*<dd>(.*?)</dd>", art, re.S):
            lis = re.findall(r"<li>(.*?)</li>", dd, re.S)
            cv.append((es(dt), [es(x) for x in lis] if lis else [es(dd)]))
        people.append(dict(img=one(r'<img src="([^"]+)"', art), name=es(one(r"<h3>(.*?)</h3>", art)),
                           role=es(one(r'<div class="role">(.*?)</div>', art)),
                           bio=es(one(r"</div>\s*</div>\s*<p>(.*?)</p>", art)), cv=cv,
                           note=es(one(r'<p class="ally-note">(.*?)</p>', art))))
    groups[es(title)] = people
leads = [(es(a), es(re.sub(r"<br>", " y ", b))) for a, b in re.findall(r"<li><span>(<span lang.*?</span>)</span><span>(.*?)</span></li>", team_sec[team_sec.index("areas-lead"):])]

news_sec = section("noticias")
press = dict(
    kicker=es(one(r'<article class="press">.*?<span class="kicker">(.*?)</span>\s*<h3>', news_sec)),
    title=es(one(r'<article class="press">.*?<h3>(.*?)</h3>', news_sec)),
    text=es(one(r'<article class="press">.*?</h3>\s*<p>(.*?)</p>', news_sec)),
    quote=es(one(r"<blockquote>(.*?)</blockquote>", news_sec)),
    url=one(r'<article class="press">.*?<a class="btn btn-navy" href="([^"]+)"', news_sec),
)
news = []
for art in re.findall(r"<article>\s*<time.*?</article>", news_sec[news_sec.index('<div class="news">'):], re.S):
    news.append(dict(when=es(one(r"<time[^>]*>(.*?)</time>", art)), title=es(one(r"<h3>(.*?)</h3>", art)),
                     text=es(one(r"</h3>\s*<p>(.*?)</p>", art)), url=html.unescape(one(r'<a class="more" href="([^"]+)"', art))))
videos = [(html.unescape(u), img, es(h)) for u, img, h in re.findall(r'<a class="video[^"]*" href="([^"]+)"[^>]*>\s*<div class="ph"><img src="([^"]+)".*?<h4>(.*?)</h4>', news_sec, re.S)]
upcoming = [(es(s), es(h), es(p)) for s, h, p in re.findall(r'<span class="soon">(.*?)</span><h4>(.*?)</h4><p>(.*?)</p>', news_sec)]

leg = section("legislacion")
leg_intro = es(one(r'<p class="intro">(.*?)</p>', leg))
law_groups = []
for title, block in re.findall(r'<div class="law-group">\s*<h3>(.*?)</h3>\s*<ul>(.*?)</ul>', leg, re.S):
    laws = []
    for li in re.findall(r"<li>(.*?)</li>", block, re.S):
        laws.append((es(one(r'<span class="law-no">(.*?)</span>', li)), es(one(r'<span class="law-name">(.*?)</span>(?=<span class="law-note">|<a)', li)),
                     es(one(r'<span class="law-note">(.*?)</span>(?=<a)', li))))
    law_groups.append((es(title), laws))
leg_note = es(one(r'<p class="laws-note">(.*?)</p>', leg))

credits = [es(li) for li in re.findall(r"<li>([^<]*?(?:«|&laquo;).*?Flickr</a></li>)", SRC)]
credits = [re.sub(r"\s*·\s*Flickr$", "", c) for c in credits]

WA = "https://wa.me/18295393700?text=" + "Hola%2C%20ESLA%20Abogados%20Consultores.%20Me%20gustar%C3%ADa%20agendar%20una%20consulta.%20Mi%20nombre%20es%3A%20"
MAIL = "mailto:info@eslard.com?subject=Consulta%20desde%20la%20presentaci%C3%B3n%20institucional"
MAPS = html.unescape(one(r'href="(https://www.google.com/maps[^"]+)"', SRC))

# ------------------------------------------------------------------ pages
pages = []
TOTAL = 20


def page(body, cls="", n=None, head=""):
    foot = ""
    if n:
        side = "r" if n % 2 else "l"
        foot = (f'<div class="run {side}"><span>ESLA Abogados Consultores</span><span>{e(head)}</span></div>'
                f'<div class="folio {side}">{n:02d}</div>')
    pages.append(f'<section class="page {cls}">{body}{foot}</section>')


def h(kicker, title):
    return f'<p class="kicker">{e(kicker)}</p><h2>{e(title)}</h2>'


mark = '<svg class="mark" viewBox="0 0 100 100"><use href="#esla-mark"/></svg>'

# 1 · Portada
page(f'''<div class="cover-photo"><img src="../assets/img-justicia.jpg" alt=""></div>
<div class="cover-body">
  <div class="cover-brand">{mark}<div><b>ESLA</b><span>Abogados Consultores</span></div></div>
  <div class="cover-title"><p class="kicker light">Presentación institucional</p>
  <h1>Estructuramos sus negocios.<br>Defendemos sus contratos.</h1>
  <p class="lead">Derecho mercantil, corporativo y fiduciario, y litigación civil y contractual, con los socios al frente de cada asunto.</p></div>
  <p class="cover-foot">Santo Domingo, República Dominicana · {EDICION}</p>
</div>''', "cover")

# 2 · Índice
toc = [("La firma", 3), ("Áreas de práctica", 4),
       ("Fideicomisos: cuatro figuras", 9), ("Socios", 10), ("Asociados", 11), ("El equipo y responsables por área", 12),
       ("Aliada en Estados Unidos", 13), ("Prensa y reconocimientos", 14), ("Entrevistas y publicaciones", 15), ("Próximas publicaciones", 16),
       ("Legislación de interés", 17), ("Cómo trabajamos", 18), ("Contacto", 19)]
page(f'''{h("Contenido", "Índice")}
<ol class="toc">{"".join(f'<li><span>{e(t)}</span><i></i><b>{p:02d}</b></li>' for t, p in toc)}</ol>
<div class="toc-note"><p>Este documento recoge, en formato impreso, la información de nuestro sitio web. Los códigos QR le llevan directamente a WhatsApp, al correo de la firma y a las entrevistas y publicaciones citadas.</p></div>''', n=2, head="Índice")

# 3 · La firma
page(f'''{h("Quiénes somos", "La firma")}
<div class="firm">
  <div class="firm-text"><p class="lead dark">{e(firm_text)}</p>
  <blockquote>{e(firm_quote)}<cite>{e(firm_quote_src)}</cite></blockquote>
  <ul class="pillars">
    <li><b>Atención directa de los socios</b><span>Los socios dirigen cada mandato, con un responsable por área de práctica.</span></li>
    <li><b>Honorarios claros por escrito</b><span>Antes de empezar, usted conoce el alcance del trabajo y su costo.</span></li>
    <li><b>Prevención primero</b><span>El mejor litigio es el que se evita con un buen documento; el que no se puede evitar se prepara desde el primer día.</span></li>
  </ul></div>
  <figure class="firm-photo"><img src="../assets/socios-biblioteca.jpg" alt=""><figcaption>Los socios fundadores, Lic. Jonathan Abel Peralta Peña y Licda. Miriam Estévez Lavandier.</figcaption></figure>
</div>
<div class="duo-mini">{"".join(f'<div><p class="kicker">{e(k)}</p><h3>{e(t)}</h3><p>{e(p)}</p></div>' for img, k, t, p in dual)}</div>''', n=3, head="La firma")

# 5–9 · Áreas de práctica (2 por página)
def area_block(t, i):
    return (f'<article class="area"><div class="ph"><img src="../{t["img"]}" alt=""><span class="num">{i:02d}</span></div>'
            f'<div class="area-body"><h3>{e(t["name"])}</h3><p class="ref">{e(t["ref"])}</p><p>{e(t["desc"])}</p>'
            f'<ul>{"".join(f"<li>{e(x)}</li>" for x in t["items"])}</ul></div></article>')


for k in range(5):
    pair = tiles[2 * k: 2 * k + 2]
    top = h("Áreas de práctica", "Lo que hacemos") + f'<p class="intro">{e(areas_intro)}</p>' if k == 0 else ""
    page(f'{top}<div class="areas{" first" if k == 0 else ""}">{"".join(area_block(t, 2 * k + j + 1) for j, t in enumerate(pair))}</div>',
         n=4 + k, head="Áreas de práctica")

# 10 · Fideicomisos
page(f'''{h("Ley 189-11", fid_title)}<p class="intro">{e(fid_intro)}</p>
<div class="trusts">{"".join(f'<article><div class="ph"><img src="../{t["img"]}" alt=""></div><div><span class="n">{e(t["n"])}</span><h3>Fideicomiso {e(t["name"].lower())}</h3><p>{e(t["desc"])}</p></div></article>' for t in trusts)}</div>
<p class="note">ESLA publica en su sitio web un texto consolidado no oficial de la Ley 189-11, con todas sus modificaciones, para consulta de clientes.</p>''', n=9, head="Fideicomisos")


# 11 · Socios
def cv_html(cv):
    rows = []
    for dt, items in cv:
        rows.append(f'<dt>{e(dt)}</dt><dd>{"<br>".join(e(x) for x in items)}</dd>')
    return f'<dl>{"".join(rows)}</dl>'


socios = groups["Socios"]
page(f'''{h("Nuestro equipo", "Socios")}<p class="intro">{e(team_intro)}</p>
<div class="partners">{"".join(f'<article><div class="portrait"><img src="../{p["img"]}" alt=""></div><div class="pb"><h3>{e(p["name"])}</h3><p class="role">{e(p["role"])}</p><p>{e(p["bio"])}</p>{cv_html(p["cv"])}</div></article>' for p in socios)}</div>''',
     n=10, head="Nuestro equipo")

# 12 · Asociados
asoc = groups["Asociados"]
page(f'''{h("Nuestro equipo", "Asociados")}
<div class="assoc">{"".join(f'<article><div class="portrait"><img src="../{p["img"]}" alt=""></div><div class="pb"><h3>{e(p["name"])}</h3><p class="role">{e(p["role"])}</p><p>{e(p["bio"])}</p>{cv_html([c for c in p["cv"] if c[0] in ("Formación", "Correo")])}</div></article>' for p in asoc)}</div>''',
     n=11, head="Nuestro equipo")

# 13 · El equipo + responsables
eq = groups["El equipo"]
page(f'''{h("Nuestro equipo", "El equipo")}
<div class="staff">{"".join(f'<article><div class="portrait"><img src="../{p["img"]}" alt=""></div><div class="pb"><h3>{e(p["name"])}</h3><p class="role">{e(p["role"])}</p>{cv_html(p["cv"])}</div></article>' for p in eq)}</div>
<h2 class="h2-small">Responsables por área</h2>
<table class="leads">{"".join(f'<tr><th>{e(a)}</th><td>{e(b)}</td></tr>' for a, b in leads)}</table>''', n=12, head="Nuestro equipo")

# 13 · Aliada en Estados Unidos
ally = groups["Aliada en Estados Unidos"][0]
ally_services = next(items for dt, items in ally["cv"] if dt.startswith("Servicios"))
ally_addr = next(items for dt, items in ally["cv"] if dt == "Dirección")[0]
ally_tel = next(items for dt, items in ally["cv"] if dt == "Teléfono")[0]
ally_portrait = (f'<img src="../{ally["img"]}" alt="">' if ally["img"] else '<span class="initials">FJ</span>')
page(f'''{h("Presencia internacional", "Aliada en Estados Unidos")}
<p class="intro">Para los clientes y las familias dominicanas que viven en los Estados Unidos, ESLA cuenta con una aliada en Filadelfia, Pensilvania, que coordina con la firma los asuntos que deben resolverse en la República Dominicana.</p>
<div class="ally">
  <div class="portrait">{ally_portrait}</div>
  <div class="pb"><h3>{e(ally["name"])}</h3><p class="role">{e(ally["role"])}</p><p>{e(ally["bio"])}</p>
  <dl><dt>Dirección</dt><dd>{e(ally_addr)}</dd><dt>Teléfono</dt><dd>{e(ally_tel)}</dd></dl></div>
</div>
<h2 class="h2-small">Servicios en Filadelfia</h2>
<ul class="ally-services">{"".join(f"<li>{e(x)}</li>" for x in ally_services)}</ul>
<p class="ally-note">{e(ally["note"])}</p>''', n=13, head="Aliada en Estados Unidos")

# 14 · Prensa y reconocimientos
page(f'''{h("Publicaciones y prensa", "Prensa y reconocimientos")}
<article class="press"><img src="../assets/prensa-mercado-encabezado.jpg" alt="">
<p class="kicker">{e(press["kicker"])}</p><h3>{e(press["title"])}</h3><p>{e(press["text"])}</p>
<blockquote>{e(press["quote"])}</blockquote>
<div class="qr-row"><div class="qr">{qr(press["url"])}</div><p>Lea el reportaje en la edición digital de Revista Mercado.</p></div></article>
<ul class="strip">{"".join(f'<li><b>{e(q)}</b><span>{e(s)}</span></li>' for q, s in strip)}</ul>''', n=14, head="Publicaciones y prensa")

# 15 · Entrevistas y noticias
page(f'''{h("Publicaciones y prensa", "Entrevistas y publicaciones")}
<div class="videos">{"".join(f'<article><div class="ph"><img src="../{img}" alt=""></div><div class="vb"><h3>{e(t)}</h3><p>Mercado Media Network · YouTube</p><div class="qr">{qr(u, 2)}</div></div></article>' for u, img, t in videos)}</div>
<div class="news">{"".join(f'<article><p class="kicker">{e(n_["when"])}</p><h3>{e(n_["title"])}</h3><p>{e(n_["text"])}</p></article>' for n_ in news)}</div>''',
     n=15, head="Publicaciones y prensa")

# 16 · Próximas publicaciones
feat, rest = upcoming[0], upcoming[1:]
page(f'''{h("Publicaciones y prensa", "Próximas publicaciones")}
<p class="intro">Guías prácticas que publicaremos en nuestro sitio web. Si le interesa alguna, escríbanos y se la enviaremos en cuanto esté disponible.</p>
<article class="feat"><p class="kicker light">{e(feat[0])}</p><h3>{e(feat[1])}</h3><p>{e(feat[2])}</p></article>
<div class="upc">{"".join(f'<article><p class="kicker">{e(s)}</p><h3>{e(t)}</h3><p>{e(p)}</p></article>' for s, t, p in rest)}</div>''', n=16, head="Publicaciones y prensa")

# 17 · Legislación
page(f'''{h("Referencia", "Legislación de interés")}<p class="intro">{e(leg_intro)}</p>
<div class="laws">{"".join(f'<div><h3>{e(g)}</h3><ul>{"".join(f"<li><b>{e(no)}</b><span>{e(name)}{(chr(10) + e(note)) if note and len(note) < 120 else ""}</span></li>" for no, name, note in laws)}</ul></div>' for g, laws in law_groups)}</div>
<p class="note">{e(leg_note)} Los textos completos, incluidos los consolidados no oficiales preparados por ESLA, están disponibles para descarga en nuestro sitio web.</p>''', n=17, head="Legislación de interés")

# 18 · Cómo trabajamos
steps = [
    ("Primer contacto", "Escríbanos por correo o WhatsApp, o llámenos. Basta con una breve descripción del asunto: no envíe información confidencial en esta etapa."),
    ("Verificación de conflictos", "Antes de reunirnos, confirmamos que no existe conflicto de interés con otros clientes o partes del asunto."),
    ("Reunión con un socio", "Le confirmamos fecha y hora con uno de los socios para conocer el caso, sus objetivos y los documentos disponibles."),
    ("Propuesta por escrito", "Le enviamos el alcance del trabajo y los honorarios por escrito, sin sorpresas."),
    ("Ejecución y seguimiento", "Formalizado el mandato, el responsable del área dirige el asunto y le mantiene informado de cada etapa."),
]
page(f'''{h("Nuestro método", "Cómo trabajamos")}
<ol class="steps">{"".join(f'<li><span class="sn">{i:02d}</span><div><h3>{e(t)}</h3><p>{e(d)}</p></div></li>' for i, (t, d) in enumerate(steps, 1))}</ol>
<div class="box"><p><b>Confidencialidad.</b> El contacto inicial no crea una relación abogado-cliente; esta nace cuando la firma acepta el encargo por escrito. La información que nos confíe se protege por el secreto profesional y conforme a la Ley 172-13 sobre Protección Integral de los Datos Personales.</p></div>''',
     n=18, head="Cómo trabajamos")

# 19 · Contacto
page(f'''{h("Hablemos", "Contacto")}
<p class="intro">Escríbanos o llámenos y le confirmaremos fecha y hora con uno de los socios.</p>
<div class="contact">
  <dl>
    <dt>Oficina</dt><dd>Av. Abraham Lincoln No. 605, Naco<br>Santo Domingo de Guzmán, Distrito Nacional<br>República Dominicana, C.P. 10119</dd>
    <dt>Teléfono oficina</dt><dd>+1 (809) 960-2992</dd>
    <dt>Teléfono y WhatsApp</dt><dd>+1 (829) 539-3700</dd>
    <dt>Correo</dt><dd>info@eslard.com</dd>
    <dt>Horario</dt><dd>Lunes a viernes, 8:30 a. m. – 5:00 p. m.</dd>
    <dt>Sitio web e Instagram</dt><dd>www.eslard.com · @esla_rd</dd>
    <dt>Aliada en Filadelfia (EE. UU.)</dt><dd>Franny Jerez Morales · 7810 Castor Avenue, Philadelphia, PA 19152 · +1 (215) 618-7514</dd>
  </dl>
  <div class="qrs">
    <figure><div class="qr">{qr(WA, 4)}</div><figcaption>WhatsApp</figcaption></figure>
    <figure><div class="qr">{qr(MAIL, 4)}</div><figcaption>Correo</figcaption></figure>
    <figure><div class="qr">{qr(MAPS, 4)}</div><figcaption>Cómo llegar</figcaption></figure>
  </div>
</div>''', n=19, head="Contacto")

# 20 · Contraportada
page(f'''<div class="back">
  <div class="back-brand">{mark}<div><b>ESLA</b><span>Abogados Consultores</span></div></div>
  <p class="back-line">Av. Abraham Lincoln No. 605, Naco, Santo Domingo · +1 (809) 960-2992 · info@eslard.com · www.eslard.com</p>
  <p class="back-line small">Aliada en Filadelfia (EE. UU.): 7810 Castor Avenue, Philadelphia, PA 19152 · +1 (215) 618-7514</p>
  <div class="back-small">
    <p>La información de este documento es general y no constituye asesoría legal. El contacto con la firma no crea una relación abogado-cliente hasta que el encargo se formaliza por escrito. Las referencias legislativas están actualizadas a {EDICION.lower()}; la versión con valor legal es la publicada en la Gaceta Oficial.</p>
    <p><b>Créditos fotográficos.</b> Fotografías del equipo y la oficina: ESLA Abogados Consultores. Demás imágenes, con licencia Creative Commons vía Openverse/Flickr: {e("; ".join(credits))}.</p>
    <p>© 2026 ESLA Abogados Consultores, SRL. Todos los derechos reservados.</p>
  </div>
</div>''', "backcover")

assert len(pages) == TOTAL, len(pages)

CSS = (ROOT / "impresos" / "brochure.css").read_text(encoding="utf-8")
doc = f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><title>ESLA · Presentación institucional</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow:wght@300;400;500;600&family=Cinzel:wght@500;700&family=Manrope:wght@400;500;600;700&display=swap">
<style>{CSS}</style></head><body>
<svg width="0" height="0" style="position:absolute"><symbol id="esla-mark" viewBox="0 0 100 100"><rect x="2" y="2" width="96" height="96" rx="14" fill="#C07D46"/><rect x="8" y="8" width="84" height="84" rx="10" fill="none" stroke="#FFFFFF" stroke-width="2.4"/><path d="M27 50 H73 V38 Q73 28 63 28 H37 Q27 28 27 38 V62 Q27 72 37 72 H70" fill="none" stroke="#FFFFFF" stroke-width="12" stroke-linejoin="round"/></symbol></svg>
{"".join(pages)}</body></html>'''
OUT.write_text(doc, encoding="utf-8")
print("ok", OUT, "páginas", len(pages), "áreas", len(tiles), "créditos", len(credits))
