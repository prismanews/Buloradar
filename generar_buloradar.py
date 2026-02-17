import feedparser
import re
import html
import numpy as np
import urllib.parse
from datetime import datetime
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# ---------- CONFIGURACIÓN ----------
UMBRAL_SENSACIONALISTA = 65
UMBRAL_DUPLICADO = 0.90
MAX_NOTICIAS_FEED = 12

modelo = SentenceTransformer("all-MiniLM-L6-v2")

DICCIONARIO_ALERTA = {
    "SENSACIONALISMO": ["impactante", "escándalo", "brutal", "bomba", "no creerás", "viral", "secreto", "censura", "increíble", "estalla"],
    "AMBIGUEDAD": ["podría", "según algunos", "dicen que", "se cree que", "rumores", "supuesto", "misterioso", "podrían"],
    "URGENCIA": ["última hora", "urgente", "atención", "difunde", "compartid", "alerta", "máxima difusión"]
}

# ---------- FUNCIONES ----------

def calcular_puntuacion(titulo, embedding, embeddings_global):
    score = 0
    texto = titulo.lower()
    razones = []
    
    # 1. Análisis de palabras clave
    for cat, palabras in DICCIONARIO_ALERTA.items():
        for p in palabras:
            if f" {p} " in f" {texto} ": # Búsqueda de palabra exacta
                score += 20
                if cat.capitalize() not in razones:
                    razones.append(cat.capitalize())
    
    # 2. Análisis visual
    if titulo.isupper():
        score += 30
        razones.append("Mayúsculas")
    if "!" in titulo or "?" in titulo:
        score += 15
        razones.append("Puntuación Excesiva")
        
    # 3. Rareza Semántica (Si es la única noticia que habla de algo de forma extraña)
    similitudes = cosine_similarity([embedding], embeddings_global)[0]
    sim_media = np.mean(similitudes)
    if sim_media < 0.15:
        score += 25
        razones.append("Aislado/Inusual")
        
    return min(score, 100), ", ".join(razones)

# ... (Aquí va tu lógica de recolección de feeds y procesamiento que ya tienes) ...
