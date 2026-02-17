import feedparser
import re
import html
import numpy as np
import hashlib
import json
import os
import requests
import urllib.parse
from datetime import datetime
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# ---------- CONFIGURACIÓN ----------
# Consigue tu API Key en: https://console.cloud.google.com/
GOOGLE_FACTCHECK_API_KEY = "TU_API_KEY_AQUÍ" 

UMBRAL_SENSACIONALISTA = 60
UMBRAL_DUPLICADO = 0.87
MAX_NOTICIAS_FEED = 10
CACHE_FILE = "embeddings_cache.json"

modelo = SentenceTransformer("all-MiniLM-L6-v2")

# ---------- DICCIONARIOS DE SEÑALES ----------
DICCIONARIO_ALERTA = {
    "SENSACIONALISMO": ["impactante", "escándalo", "brutal", "bomba", "no creerás", "viral", "secreto", "censura", "increíble"],
    "AMBIGUEDAD": ["podría", "según algunos", "dicen que", "se cree que", "rumores", "supuesto", "misterioso"],
    "URGENCIA": ["última hora", "urgente", "atención", "difunde", "compartid", "alerta"]
}

# ---------- FEEDS ----------
feeds = {
    "El País": "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada",
    "El Mundo": "https://e00-elmundo.uecdn.es/elmundo/rss/portada.xml",
    "ABC": "https://www.abc.es/rss/feeds/abcPortada.xml",
    "La Vanguardia": "https://www.lavanguardia.com/rss/home.xml",
    "20 Minutos": "https://www.20minutos.es/rss/",
    "eldiario.es": "https://www.eldiario.es/rss/",
    "BBC Mundo": "https://feeds.bbci.co.uk/mundo/rss.xml"
}

# ---------- FUNCIONES NÚCLEO ----------

def verificar_fact_check(query):
    if not GOOGLE_FACTCHECK_API_KEY or GOOGLE_FACTCHECK_API_KEY == "TU_API_KEY_AQUÍ":
        return None
    endpoint = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
    params = {"query": query, "languageCode": "es", "key": GOOGLE_FACTCHECK_API_KEY}
    try:
        response = requests.get(endpoint, params=params, timeout=5)
        data = response.json()
        if "claims" in data:
            claim = data["claims"][0]
            veredicto = claim["claimReview"][0]["textualRating"]
            fuente = claim["claimReview"][0]["publisher"]["name"]
            return f"Confirmado como '{veredicto}' por {fuente}"
    except: return None
    return None

def calcular_puntuacion(titulo, embedding, embeddings_global):
    score = 0
    texto = titulo.lower()
    razones = []
    for cat, palabras in DICCIONARIO_ALERTA.items():
        if any(p in texto for p in palabras):
            score += 25
            razones.append(cat.capitalize())
    if titulo.isupper():
        score += 30
        razones.append("Mayúsculas")
    if "!!" in titulo or "??" in titulo:
        score += 15
        razones.append("Exclamaciones")
    centroide = np.mean(embeddings_global, axis=0)
    sim = cosine_similarity([embedding], [centroide])[0][0]
    if sim < 0.22:
        score += 20
        razones.append("Contenido Atípico")
    return min(score, 100), ", ".join(razones)

def limpiar_html(texto):
    return html.unescape(re.sub(r'<.*?>', '', texto)).strip()

# ---------- PROCESAMIENTO ----------

# 1. Recoger noticias
noticias_raw = []
for medio, url in feeds.items():
    try:
        f = feedparser.parse(url)
        for entry in f.entries[:MAX_NOTICIAS_FEED]:
            noticias_raw.append({"medio": medio, "titulo": limpiar_html(entry.title), "link": entry.link.strip()})
    except: continue

# 2. Generar Embeddings y Deduplicar
titulos = [n["titulo"] for n in noticias_raw]
embs = modelo.encode(titulos)
filtradas, embs_f = [], []

for i, emb in enumerate(embs):
    if not embs_f or max(cosine_similarity([emb], embs_f)[0]) < UMBRAL_DUPLICADO:
        filtradas.append(noticias_raw[i])
        embs_f.append(emb)

# 3. Score y Fact-Check
for i, n in enumerate(filtradas):
    s_base, raz = calcular_puntuacion(n["titulo"], embs_f[i], embs_f)
    n["bulo_score"] = s_base
    n["razones"] = raz
    n["detalle_oficial"] = verificar_fact_check(n["titulo"]) if s_base > 40 else None
    if n["detalle_oficial"]: n["bulo_score"] = 100

filtradas.sort(key=lambda x: x["bulo_score"], reverse=True)

# ---------- GENERAR HTML ----------

fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
html_output = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BuloRadar - Análisis de Sensacionalismo</title>
    <link rel="stylesheet" href="buloradar.css">
</head>
<body>
    <header class="main-header">
        <h1>🚨 BuloRadar</h1>
        <div class="disclaimer">
            <strong>Nota:</strong> Este radar analiza patrones lingüísticos y sensacionalismo. NO es una verificación de hechos automática, excepto en casos señalados por agencias oficiales.
        </div>
        <p>Actualizado: {fecha}</p>
    </header>
    <main class="grid">
"""

for n in filtradas[:40]:
    c_alerta = "high-risk" if n['bulo_score'] >= 70 else "warning" if n['bulo_score'] >= 40 else ""
    t_twitter = urllib.parse.quote(f"🚨 Análisis de BuloRadar:\n\n📰 {n['titulo']}\n📊 Score: {n['bulo_score']}%\n🔗 {n['link']}\n\n#BuloRadar @PrismaNews")
    
    html_output += f"""
    <div class="card {c_alerta}">
        <span class="medio">{n['medio']}</span>
        <h2><a href="{n['link']}" target="_blank">{n['titulo']}</a></h2>
        <span class="tag">{n['razones'] if n['razones'] else 'Estilo Neutro'}</span>
        <div class="score-container">
            <div class="score-bar"><div class="progress" style="width: {n['bulo_score']}%"></div></div>
            <div class="score-text"><span>Indice Sensacionalismo</span><span>{n['bulo_score']}%</span></div>
        </div>
        {"<div class='fact-check-alert'>⚠️ " + n['detalle_oficial'] + "</div>" if n['detalle_oficial'] else ""}
        <div class="card-footer">
            <a href="https://twitter.com/intent/tweet?text={t_twitter}" target="_blank" class="btn-share">
                <svg viewBox="0 0 24 24" width="14" height="14"><path fill="currentColor" d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"></path></svg>
                Compartir
            </a>
        </div>
    </div>
    """

html_output += "</main></body></html>"
with open("index.html", "w", encoding="utf-8") as f: f.write(html_output)
print("✅ BuloRadar generado con éxito.")
