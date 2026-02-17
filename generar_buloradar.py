import feedparser
import re
import html
import numpy as np
import urllib.parse
from datetime import datetime
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# ---------- CONFIGURACIÓN AVANZADA ----------
UMBRAL_SENSACIONALISTA = 65
UMBRAL_DUPLICADO = 0.88
# Hemos ampliado la lista de medios para tener una base de comparación más sólida
feeds = {
    "El País": "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada",
    "El Mundo": "https://e00-elmundo.uecdn.es/elmundo/rss/portada.xml",
    "ABC": "https://www.abc.es/rss/feeds/abcPortada.xml",
    "La Vanguardia": "https://www.lavanguardia.com/rss/home.xml",
    "20 Minutos": "https://www.20minutos.es/rss/",
    "eldiario.es": "https://www.eldiario.es/rss/",
    "BBC Mundo": "https://feeds.bbci.co.uk/mundo/rss.xml",
    "EFE Noticias": "https://www.efe.com/efe/espana/1/rss"
}

modelo = SentenceTransformer("all-MiniLM-L6-v2")

# Diccionario expandido de señales de desinformación
DICCIONARIO_IA = {
    "SENSACIONALISMO": ["impactante", "escándalo", "brutal", "bomba", "no creerás", "viral", "secreto", "censura", "estalla", "misterioso"],
    "AMBIGUEDAD": ["podría", "según algunos", "dicen que", "se cree que", "rumores", "supuesto", "posiblemente"],
    "URGENCIA_FALSA": ["última hora", "urgente", "difunde", "atención", "máxima difusión", "compartid"]
}

def limpiar_texto(t):
    return html.unescape(re.sub(r'<.*?>', '', t)).strip()

def analizar_noticia(titulo, embedding, embeddings_global):
    score = 0
    razones = []
    texto_lower = titulo.lower()

    # 1. Análisis Lingüístico (Diccionario IA)
    for cat, palabras in DICCIONARIO_ALERTA.items():
        if any(f" {p} " in f" {texto_lower} " for p in palabras):
            score += 25
            razones.append(cat.capitalize())

    # 2. Análisis de Estilo (Gritos y Puntuación)
    if titulo.isupper():
        score += 30
        razones.append("Mayúsculas")
    if "!!" in titulo or "??" in titulo:
        score += 15
        razones.append("Excesiva Puntuación")

    # 3. Inteligencia Semántica (Detección de Anomalías)
    # Comparamos la noticia con el promedio de todas las noticias del día
    # Si es un tema que nadie más toca o tiene un enfoque único, es sospechoso
    centroide = np.mean(embeddings_global, axis=0)
    similitud = cosine_similarity([embedding], [centroide])[0][0]
    
    if similitud < 0.18: # Noticia muy aislada semánticamente
        score += 20
        razones.append("Contenido Atípico")

    return min(score, 100), ", ".join(razones)

# --- PROCESO PRINCIPAL ---
noticias_raw = []
for medio, url in feeds.items():
    try:
        f = feedparser.parse(url)
        for e in f.entries[:10]:
            noticias_raw.append({"medio": medio, "titulo": limpiar_texto(e.title), "link": e.link})
    except: continue

# Generar Embeddings y Deduplicar
titulos = [n["titulo"] for n in noticias_raw]
embeddings = modelo.encode(titulos)
filtradas, embs_f = [], []

for i, emb in enumerate(embeddings):
    if not embs_f or max(cosine_similarity([emb], embs_f)[0]) < UMBRAL_DUPLICADO:
        filtradas.append(noticias_raw[i])
        embs_f.append(emb)

# Aplicar Inteligencia de Detección
for i, n in enumerate(filtradas):
    score, razones = analizar_noticia(n["titulo"], embs_f[i], embs_f)
    n["bulo_score"] = score
    n["razones"] = razones

filtradas.sort(key=lambda x: x["bulo_score"], reverse=True)

# --- GENERACIÓN DE HTML ---
fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
html_final = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BuloRadar - Análisis de IA</title>
    <link rel="stylesheet" href="buloradar.css">
</head>
<body>
    <header class="main-header">
        <h1>🚨 BuloRadar</h1>
        <div class="disclaimer">
            <strong>Analizador de Estilo:</strong> Esta herramienta detecta patrones de sensacionalismo y anomalías semánticas típicas de la desinformación. No es una verificación factual manual.
        </div>
        <p>Última actualización: {fecha}</p>
    </header>
    <main class="grid">
"""

for n in filtradas[:40]:
    t_twitter = urllib.parse.quote(f"🚨 Análisis #BuloRadar:\n\n📰 {n['titulo']}\n📊 Score IA: {n['bulo_score']}%\n\nVer más: https://prismanews.github.io/Buloradar/")
    clase = "high-risk" if n['bulo_score'] >= 65 else "warning" if n['bulo_score'] >= 35 else ""
    
    html_final += f"""
    <div class="card {clase}">
        <span class="medio">{n['medio']}</span>
        <h2><a href="{n['link']}" target="_blank">{n['titulo']}</a></h2>
        <span class="tag">{n['razones'] if n['razones'] else 'Neutro'}</span>
        <div class="score-container">
            <div class="score-bar"><div class="progress" style="width: {n['bulo_score']}%"></div></div>
            <p class="score-text">Índice de Sospecha: {n['bulo_score']}%</p>
        </div>
        <div class="card-footer">
            <a href="https://twitter.com/intent/tweet?text={t_twitter}" target="_blank" class="btn-share">
                <svg viewBox="0 0 24 24" width="14" height="14" fill="white"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"></path></svg>
                Compartir
            </a>
        </div>
    </div>
    """

html_final += "</main></body></html>"
with open("index.html", "w", encoding="utf-8") as f: f.write(html_final)
