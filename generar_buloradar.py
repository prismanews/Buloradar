import feedparser
import re
import html
import random
from datetime import datetime
from collections import Counter
import numpy as np
import hashlib
import json
import os
import time
import logging
from difflib import SequenceMatcher

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# ---------- CONFIG ----------

logging.basicConfig(level=logging.INFO)

UMBRAL_CLUSTER = 0.63
UMBRAL_DUPLICADO = 0.87
MAX_NOTICIAS_FEED = 8
CACHE_FILE = "embeddings_cache.json"

modelo = SentenceTransformer("all-MiniLM-L6-v2")


# ---------- FEEDS (REUTILIZADOS PRISMA) ----------

feeds = {
    "El País": "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada",
    "El Mundo": "https://e00-elmundo.uecdn.es/elmundo/rss/portada.xml",
    "ABC": "https://www.abc.es/rss/feeds/abcPortada.xml",
    "La Vanguardia": "https://www.lavanguardia.com/rss/home.xml",
    "20 Minutos": "https://www.20minutos.es/rss/",
    "eldiario.es": "https://www.eldiario.es/rss/",
    "BBC Mundo": "https://feeds.bbci.co.uk/mundo/rss.xml",
    "Reuters": "https://www.reutersagency.com/feed/?best-topics=general-news"
}


# ---------- DETECTOR BULOS ----------

PALABRAS_BULO = [
    "escándalo", "ocultan", "nadie habla",
    "no quieren que sepas", "impactante",
    "viral", "última hora", "increíble",
    "bomba", "secreto", "censura",
    "alarmante", "te sorprenderá"
]


def score_bulo(titulo, embedding=None, embeddings_global=None):
    score = 0
    texto = titulo.lower()

    for palabra in PALABRAS_BULO:
        if palabra in texto:
            score += 15

    if titulo.isupper():
        score += 20

    if "!!" in titulo or "??" in titulo:
        score += 10

    if embedding is not None and embeddings_global is not None:
        centroide = np.mean(embeddings_global, axis=0)
        sim = cosine_similarity([embedding], [centroide])[0][0]
        if sim < 0.25:
            score += 10

    return min(score, 100)


# ---------- UTILIDADES ----------

def limpiar_html(texto):
    texto = html.unescape(texto)
    texto = re.sub(r'<.*?>', '', texto)
    return texto.strip()


def get_cache_key(texto):
    return hashlib.md5(texto.encode()).hexdigest()


def cargar_cache():
    if os.path.exists(CACHE_FILE):
        return json.load(open(CACHE_FILE))
    return {}


def guardar_cache(cache):
    json.dump(cache, open(CACHE_FILE, "w"))


# ---------- RECOGER NOTICIAS ----------

noticias = []

for medio, url in feeds.items():
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries[:MAX_NOTICIAS_FEED]:
            if "title" in entry and "link" in entry:
                noticias.append({
                    "medio": medio,
                    "titulo": limpiar_html(entry.title),
                    "link": entry.link.strip()
                })
    except Exception as e:
        print("Error feed:", medio, e)


# ---------- EMBEDDINGS ----------

cache = cargar_cache()

embeddings = []
titulos = [n["titulo"] for n in noticias]

for titulo in titulos:
    key = get_cache_key(titulo)
    if key in cache:
        embeddings.append(np.array(cache[key]))
    else:
        emb = modelo.encode(titulo)
        cache[key] = emb.tolist()
        embeddings.append(emb)

guardar_cache(cache)
embeddings = np.array(embeddings)


# ---------- DEDUPLICADO ----------

filtradas = []
emb_filtrados = []

for i, emb in enumerate(embeddings):
    if not emb_filtrados:
        filtradas.append(noticias[i])
        emb_filtrados.append(emb)
        continue

    sim = cosine_similarity([emb], emb_filtrados)[0]
    if max(sim) < UMBRAL_DUPLICADO:
        filtradas.append(noticias[i])
        emb_filtrados.append(emb)

noticias = filtradas
embeddings = np.array(emb_filtrados)


# ---------- SCORE BULOS ----------

for i, n in enumerate(noticias):
    n["bulo_score"] = score_bulo(n["titulo"], embeddings[i], embeddings)


# ---------- ORDENAR ----------

noticias.sort(key=lambda x: x["bulo_score"], reverse=True)


# ---------- HTML ----------

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
<p>Radar automático de posibles titulares engañosos.</p>
<p>Actualizado: {fecha}</p>
"""


for n in noticias[:40]:

    alerta = ""
    if n["bulo_score"] > 60:
        alerta = '<p class="alerta">⚠️ Posible desinformación</p>'

    html += f"""
    <div class="card">
        <h2>
        <a href="{n['link']}" target="_blank">
        {n['titulo']}
        </a>
        </h2>
        <p>{n['medio']}</p>
        {alerta}
        <p class="score">Score IA: {n['bulo_score']}%</p>
    </div>
    """


html += "</body></html>"

open("index.html", "w", encoding="utf-8").write(html)

print("✅ BULORADAR generado")
