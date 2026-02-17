import feedparser
import re
import html
import numpy as np
from datetime import datetime
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# ---------- CONFIG ----------
modelo = SentenceTransformer("all-MiniLM-L6-v2")

UMBRAL_FACTCHECK = 0.78
UMBRAL_SIMILITUD_NOTICIAS = 0.55

PESO_FACTCHECK = 60
PESO_SENSACIONALISMO = 20
PESO_AISLAMIENTO = 15
PESO_FORMATO = 5


# ---------- FEEDS NOTICIAS ----------
feeds_noticias = {
    "El País": "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada",
    "El Mundo": "https://e00-elmundo.uecdn.es/elmundo/rss/portada.xml",
    "ABC": "https://www.abc.es/rss/feeds/abcPortada.xml",
    "La Vanguardia": "https://www.lavanguardia.com/rss/home.xml",
    "El Confidencial": "https://blogs.elconfidencial.com/rss/",
    "Público": "https://www.publico.es/rss/",
    "HuffPost": "https://www.huffingtonpost.es/feed/",
    "El Español": "https://www.elespanol.com/rss/",
    "Xataka": "http://feeds.weblogssl.com/xataka2",
    "Scientific American": "https://www.scientificamerican.com/section/news/rss/"
}


# ---------- FACT-CHECKERS ----------
feeds_verificadores = {
    "Maldita": "https://maldita.es/rss/fact-checking",
    "Newtral": "https://www.newtral.es/feed/",
    "EFE Verifica": "https://efeverifica.com/feed/",
    "AFP": "https://factual.afp.com/feed/all"
}


# ---------- LIMPIEZA ----------
def limpiar(texto):
    texto = html.unescape(texto)
    texto = re.sub(r'<.*?>', '', texto)
    return texto.strip()


# ---------- DESMENTIDOS ----------
desmentidos = []

for medio, url in feeds_verificadores.items():
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries[:25]:
            desmentidos.append(limpiar(entry.title))
    except:
        continue

emb_desmentidos = modelo.encode(desmentidos) if desmentidos else []


# ---------- NOTICIAS ----------
noticias = []

for medio, url in feeds_noticias.items():
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries[:10]:
            noticias.append({
                "medio": medio,
                "titulo": limpiar(entry.title),
                "link": entry.link
            })
    except:
        continue

titulos = [n["titulo"] for n in noticias]
emb_noticias = modelo.encode(titulos)


# ---------- FUNCIÓN SCORE ----------
def calcular_score(noticia, emb_noticia, emb_noticias, emb_desmentidos):

    score = 0
    razon = "Cobertura informativa normal"

    # 1️⃣ FACT-CHECK
    if len(emb_desmentidos) > 0:
        sims = cosine_similarity([emb_noticia], emb_desmentidos)[0]
        if max(sims) > UMBRAL_FACTCHECK:
            score += PESO_FACTCHECK
            razon = "Relacionado con verificaciones"

    # 2️⃣ SENSACIONALISMO
    palabras = [
        "escándalo","bomba","impactante","ocultan",
        "alarmante","brutal","pánico","exclusiva",
        "no creerás","histórico"
    ]

    if any(p in noticia["titulo"].lower() for p in palabras):
        score += PESO_SENSACIONALISMO
        razon = "Lenguaje sensacionalista"

    # 3️⃣ AISLAMIENTO MEDIÁTICO
    sims = cosine_similarity([emb_noticia], emb_noticias)[0]
    similares = sum(s > UMBRAL_SIMILITUD_NOTICIAS for s in sims)

    if similares <= 2:
        score += PESO_AISLAMIENTO
        razon = "Poca cobertura mediática"

    # 4️⃣ FORMATO EXAGERADO
    if noticia["titulo"].isupper():
        score += PESO_FORMATO
        razon = "Titular exagerado"

    return min(score, 100), razon


# ---------- CALCULAR SCORES ----------
for i, noticia in enumerate(noticias):
    score, razon = calcular_score(
        noticia,
        emb_noticias[i],
        emb_noticias,
        emb_desmentidos
    )

    noticia["bulo_score"] = score
    noticia["razon"] = razon


# ---------- ORDENAR ----------
noticias.sort(key=lambda x: x["bulo_score"], reverse=True)


# ---------- GENERAR HTML ----------
fecha = datetime.now().strftime("%d/%m/%Y %H:%M")

html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>BuloRadar</title>
<link rel="stylesheet" href="buloradar.css">
<meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>

<h1>🚨 BuloRadar</h1>
<p>Radar automático de posibles titulares dudosos.</p>
<p>Actualizado: {fecha}</p>
"""


for n in noticias[:40]:
    html += f"""
    <div class="card">
        <h2>
        <a href="{n['link']}" target="_blank">
        {n['titulo']}
        </a>
        </h2>
        <p>{n['medio']}</p>
        <p><strong>Score:</strong> {n['bulo_score']}%</p>
        <p>{n['razon']}</p>
    </div>
    """

html += """
<p style="margin-top:40px;font-size:0.9em;opacity:0.6;">
Este sistema detecta señales lingüísticas y coincidencias con verificaciones públicas.
No determina veracidad factual.
</p>
"""

html += "</body></html>"

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("✅ BuloRadar actualizado correctamente")
