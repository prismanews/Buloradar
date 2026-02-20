from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
from datetime import datetime, timedelta
import asyncio
from scraper.twitter_scraper import TwitterScraper
from scraper.tiktok_scraper import TikTokScraper
from scraper.medios_scraper import MediosScraper
from ai.detector import BuloDetector
from database.models import Bulo, Fuente, Usuario
from database.db_config import Database
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="BuloRadar API", version="2.0.0")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar componentes
db = Database()
twitter_scraper = TwitterScraper()
tiktok_scraper = TikTokScraper()
medios_scraper = MediosScraper()
detector = BuloDetector()

# Modelos Pydantic
class BuloCreate(BaseModel):
    titulo: str
    descripcion: str
    plataforma: str
    url: str
    categoria: str
    nivel_peligro: str

class BuloResponse(BaseModel):
    id: str
    titulo: str
    descripcion: str
    verdad: Optional[str]
    plataforma: str
    categoria: str
    nivel_peligro: str
    fecha: datetime
    fuentes: List[dict]
    viralidad: int

class ReporteUsuario(BaseModel):
    url: str
    plataforma: str
    descripcion: str
    email: Optional[str]

# Endpoints API

@app.get("/")
async def root():
    return {"message": "BuloRadar API v2.0", "status": "operativo"}

@app.get("/api/bulos/recientes", response_model=List[BuloResponse])
async def get_bulos_recientes(limit: int = 20):
    """Obtener los bulos más recientes"""
    bulos = await db.get_recientes(limit)
    return bulos

@app.get("/api/bulos/buscar")
async def buscar_bulos(
    query: str = "",
    categoria: str = "",
    plataforma: str = "",
    fecha_desde: str = "",
    fecha_hasta: str = "",
    nivel_peligro: str = ""
):
    """Búsqueda avanzada de bulos"""
    filtros = {
        "query": query,
        "categoria": categoria,
        "plataforma": plataforma,
        "nivel_peligro": nivel_peligro
    }
    if fecha_desde and fecha_hasta:
        filtros["fecha_desde"] = datetime.fromisoformat(fecha_desde)
        filtros["fecha_hasta"] = datetime.fromisoformat(fecha_hasta)
    
    resultados = await db.buscar_bulos(filtros)
    return resultados

@app.get("/api/bulos/{bulo_id}", response_model=BuloResponse)
async def get_bulo(bulo_id: str):
    """Obtener detalle de un bulo específico"""
    bulo = await db.get_bulo(bulo_id)
    if not bulo:
        raise HTTPException(status_code=404, detail="Bulo no encontrado")
    return bulo

@app.post("/api/bulos/reportar")
async def reportar_bulo(reporte: ReporteUsuario, background_tasks: BackgroundTasks):
    """Reportar un nuevo posible bulo (desde el frontend o extensión)"""
    # Guardar reporte
    reporte_id = await db.guardar_reporte(reporte.dict())
    
    # Análisis en segundo plano
    background_tasks.add_task(analizar_reporte, reporte_id, reporte.dict())
    
    return {"message": "Reporte recibido", "id": reporte_id}

@app.post("/api/bulos/verificar")
async def verificar_bulo(url: str):
    """Verificar un contenido específico (usado por la extensión)"""
    # Analizar URL
    resultado = await detector.analizar_url(url)
    
    # Buscar en base de datos
    existente = await db.buscar_por_url(url)
    
    if existente:
        resultado["ya_verificado"] = True
        resultado["bulo_id"] = existente["id"]
    
    return resultado

@app.get("/api/estadisticas")
async def get_estadisticas():
    """Obtener estadísticas generales"""
    total = await db.count_bulos()
    por_categoria = await db.count_por_categoria()
    por_plataforma = await db.count_por_plataforma()
    tendencias = await db.get_tendencias_ultima_semana()
    
    return {
        "total_bulos": total,
        "por_categoria": por_categoria,
        "por_plataforma": por_plataforma,
        "tendencias": tendencias
    }

@app.post("/api/scraper/ejecutar")
async def ejecutar_scraping(background_tasks: BackgroundTasks):
    """Ejecutar scraping manual (solo admin)"""
    background_tasks.add_task(ejecutar_scraping_completo)
    return {"message": "Scraping iniciado"}

# Funciones en segundo plano
async def analizar_reporte(reporte_id: str, reporte_data: dict):
    """Analizar un reporte con IA"""
    # Analizar contenido
    analisis = await detector.analizar_texto(reporte_data["descripcion"])
    
    if analisis["probabilidad_bulo"] > 0.7:
        # Buscar más información
        fuentes = await buscar_fuentes_verificacion(reporte_data)
        
        # Crear entrada en base de datos
        nuevo_bulo = {
            "titulo": generar_titulo(analisis),
            "descripcion": reporte_data["descripcion"],
            "plataforma": reporte_data["plataforma"],
            "url": reporte_data["url"],
            "categoria": analisis["categoria"],
            "nivel_peligro": calcular_peligro(analisis),
            "fuentes": fuentes,
            "verificado": False,
            "reporte_origen": reporte_id
        }
        
        await db.crear_bulo(nuevo_bulo)

async def ejecutar_scraping_completo():
    """Ejecutar todos los scrapers"""
    # Twitter
    tweets = await twitter_scraper.scan_tendencias()
    for tweet in tweets:
        await procesar_contenido(tweet, "twitter")
    
    # TikTok
    videos = await tiktok_scraper.scan_tendencias()
    for video in videos:
        await procesar_contenido(video, "tiktok")
    
    # Medios
    noticias = await medios_scraper.scan_portadas()
    for noticia in noticias:
        await procesar_contenido(noticia, "medio")

async def procesar_contenido(contenido: dict, plataforma: str):
    """Procesar un contenido y verificar si es bulo"""
    # Analizar con IA
    analisis = await detector.analizar_contenido(contenido)
    
    if analisis["es_bulo"]:
        # Guardar en base de datos
        bulo = {
            "titulo": contenido.get("titulo") or contenido.get("texto")[:100],
            "descripcion": contenido.get("texto", ""),
            "plataforma": plataforma,
            "url": contenido.get("url"),
            "categoria": analisis["categoria"],
            "nivel_peligro": analisis["peligro"],
            "viralidad": contenido.get("likes", 0) + contenido.get("retweets", 0),
            "fecha_deteccion": datetime.now()
        }
        
        await db.crear_bulo(bulo)
        
        # Notificar si es muy viral
        if bulo["viralidad"] > 10000:
            await notificar_alerta(bulo)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
