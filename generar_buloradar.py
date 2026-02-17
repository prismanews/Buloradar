import feedparser
import re
import html
import numpy as np
import urllib.parse
from datetime import datetime
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# ---------- CONFIGURACIÓN ----------
UMBRAL_BULO = 0.78 
modelo = SentenceTransformer("all-MiniLM-L6-v2")

# 1. EL GRAN RADAR DE NOTICIAS (Añadidos los Confidenciales)
feeds_noticias = {
    # Confidenciales y Digitales potentes
    "El Confidencial": "https://blogs.elconfidencial.com/rss/",
    "Vozpópuli": "https://www.vozpopuli.com/rss/",
    "Libertad Digital": "https://ld-rss.s3.amazonaws.com/libertaddigital/portada.xml",
    "Público": "https://www.publico.es/rss/",
    "HuffPost": "https://www.huffingtonpost.es/feed/",
    "El Español": "https://www.elespanol.com/rss/",
    "OKDiario": "https://okdiario.com/feed",
    "The Objective": "https://theobjective.com/feed/",
    
    # Tradicionales
    "El País": "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada",
    "El Mundo": "https://e00-elmundo.uecdn.es/elmundo/rss/portada.xml",
    "ABC": "https://www.abc.es/rss/feeds/abcPortada.xml",
    "La Vanguardia": "https://www.lavanguardia.com/rss/home.xml",
    
    # Ciencia y Tecnología (Donde hay muchos bulos de salud/tecnología)
    "Xataka": "http://feeds.weblogssl.com/xataka2",
    "Materia (El País)": "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/ciencia",
    "Scientific American": "https://www.scientificamerican.com/section/news/rss/"
}

# 2. VERIFICADORES (Nuestra "Piedra de Rosetta" para la verdad)
feeds_verificadores = {
    "Maldita.es": "https://maldita.es/rss/fact-checking",
    "Newtral": "https://www.newtral.es/feed/",
    "EFE Verifica": "https://efeverifica.com/feed/",
    "AFP Factual": "https://factual.afp.com/feed/all"
}

def limpiar(t): return html.unescape(re.sub(r'<.*?>', '', t)).strip()

# --- MOTOR DE ANÁLISIS ---
# Recogemos los desmentidos (La "Vacuna")
desmentidos_titulos = []
for v, url in feeds_verificadores.items():
    try:
        f = feedparser.parse(url)
        for e in f.entries[:25]: desmentidos_titulos.append(limpiar(e.title))
    except: continue

emb_desmentidos = modelo.encode(desmentidos_titulos) if desmentidos_titulos else []

# Recogemos las noticias (El "Virus")
noticias = []
for medio, url in feeds_noticias.items():
    try:
        f = feedparser.parse(url)
        for e in f.entries[:10]:
            noticias.append({"medio": medio, "titulo": limpiar(e.title), "link": e.link})
    except: continue

titulos_noticias = [n["titulo"] for n in noticias]
emb_noticias = modelo.encode(titulos_noticias)

for i, n in enumerate(noticias):
    score = 0
    razon = "Estilo Informativo"
    
    # Comprobación de coincidencia con un desmentido (Fact-Check)
    if len(emb_desmentidos) > 0:
        sims = cosine_similarity([emb_noticias[i]], emb_desmentidos)[0]
        max_sim = max(sims)
        if max_sim > UMBRAL_BULO:
            score = 100
            razon = "BULO CONFIRMADO"
    
    # Si no hay coincidencia directa, analizamos "banderas rojas" de estilo
    if score == 0:
        t_low = n["titulo"].lower()
        if any(p in t_low for p in ["bomba", "escándalo", "brutal", "ocultan", "exclusiva", "pánico"]):
            score = 45
            razon = "Estilo Sensacionalista"
        elif n["titulo"].isupper():
            score = 35
            razon = "Alerta: Titular en Mayúsculas"

    n["bulo_score"] = score
    n["razon"] = razon

# Ordenar por riesgo y limpiar duplicados (IA)
noticias.sort(key=lambda x: x["bulo_score"], reverse=True)

# --- GENERAR HTML ---
# (Aquí sigue tu bloque de generación de index.html con el diseño limpio)
