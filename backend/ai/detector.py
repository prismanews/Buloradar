import openai
from transformers import pipeline
import asyncio
from typing import Dict, List
import re
import hashlib
import numpy as np
from datetime import datetime
import os

class BuloDetector:
    def __init__(self):
        # Inicializar modelos de IA
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = self.openai_api_key
        
        # Modelos de clasificación
        self.clasificador = pipeline(
            "text-classification",
            model="roberta-base-bne"
        )
        
        self.detector_noticias = pipeline(
            "text-classification",
            model="mrm8488/bert-tiny-finetuned-fake-news-detection"
        )
        
        # Palabras clave de desinformación
        self.patrones_bulo = [
            r"\b(cura|remedio) (milagroso|secreto)\b",
            r"\b(ellos|gobierno|élite) nos (oculta|esconde)\b",
            r"\b(verdad que no quieren que sepas)\b",
            r"\b(100% (efectivo|seguro))\b",
            r"\b(descubrimiento (revolucionario|increíble))\b"
        ]
        
        # Fuentes confiables
        self.fuentes_confiables = [
            "who.int", "who.es", "sanidad.gob.es",
            "maldita.es", "newtral.es", "rtve.es/verifica",
            "efe.com/comprueba", "reuters.com/fact-check"
        ]
    
    async def analizar_contenido(self, contenido: Dict) -> Dict:
        """Analizar un contenido completo"""
        texto = contenido.get("texto", "")
        url = contenido.get("url", "")
        imagenes = contenido.get("imagenes", [])
        
        # Análisis paralelo
        analisis_texto = await self.analizar_texto(texto)
        analisis_url = await self.analizar_url(url)
        analisis_imagenes = await self.analizar_imagenes(imagenes)
        
        # Combinar resultados
        resultado = {
            "es_bulo": False,
            "probabilidad_bulo": 0.0,
            "categoria": "desconocida",
            "peligro": "bajo",
            "evidencia": []
        }
        
        # Ponderar análisis
        if analisis_texto["probabilidad"] > 0.7:
            resultado["es_bulo"] = True
            resultado["probabilidad_bulo"] = analisis_texto["probabilidad"]
            resultado["evidencia"].append({
                "tipo": "texto",
                "detalle": analisis_texto["razon"]
            })
        
        if analisis_url["es_sospechosa"]:
            resultado["es_bulo"] = True
            resultado["evidencia"].append({
                "tipo": "url",
                "detalle": "Dominio sospechoso"
            })
        
        # Determinar categoría
        resultado["categoria"] = await self.clasificar_categoria(texto)
        
        # Calcular nivel de peligro
        resultado["peligro"] = await self.calcular_peligro(resultado)
        
        return resultado
    
    async def analizar_texto(self, texto: str) -> Dict:
        """Analizar texto con IA"""
        resultado = {
            "probabilidad": 0.0,
            "razon": "",
            "patrones_encontrados": []
        }
        
        try:
            # Usar GPT para análisis
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un experto en detectar desinformación y bulos. Analiza el texto y determina si es falso o engañoso."},
                    {"role": "user", "content": f"Analiza este texto y determina si es un bulo: {texto}"}
                ]
            )
            
            analisis = response.choices[0].message.content
            
            if "bulo" in analisis.lower() or "falso" in analisis.lower():
                resultado["probabilidad"] = 0.9
                resultado["razon"] = analisis
            
        except Exception as e:
            # Fallback a modelo local
            try:
                prediccion = self.detector_noticias(texto[:512])
                resultado["probabilidad"] = prediccion[0]["score"]
            except:
                pass
        
        # Buscar patrones típicos
        for patron in self.patrones_bulo:
            if re.search(patron, texto.lower()):
                resultado["patrones_encontrados"].append(patron)
                resultado["probabilidad"] = max(resultado["probabilidad"], 0.8)
        
        return resultado
    
    async def analizar_url(self, url: str) -> Dict:
        """Analizar URL sospechosa"""
        resultado = {
            "es_sospechosa": False,
            "razon": ""
        }
        
        # Patrones de URLs sospechosas
        patrones_sospechosos = [
            r"noticia\-[a-z0-9]{10}\.com",
            r"el\-[a-z]+\-diario\.es",
            r"periodico\-[a-z]+\.org",
            r"\.xyz$", r"\.top$", r"\.club$"
        ]
        
        for patron in patrones_sospechosos:
            if re.search(patron, url):
                resultado["es_sospechosa"] = True
                resultado["razon"] = "URL con patrón de sitio falso"
                break
        
        # Verificar contra fuentes confiables
        for fuente in self.fuentes_confiables:
            if fuente in url:
                resultado["es_sospechosa"] = False
                break
        
        return resultado
    
    async def analizar_imagenes(self, imagenes: List[str]) -> List[Dict]:
        """Analizar imágenes en busca de manipulación"""
        resultados = []
        
        for img_url in imagenes:
            # Aquí se integraría con APIs de análisis de imagen
            # como Google Vision, AWS Rekognition, etc.
            resultados.append({
                "url": img_url,
                "manipulada": False,
                "confianza": 0.0
            })
        
        return resultados
    
    async def clasificar_categoria(self, texto: str) -> str:
        """Clasificar el texto en categorías"""
        categorias = ["salud", "politica", "economia", "ciencia", "social"]
        
        try:
            # Usar clasificador
            resultado = self.clasificador(texto[:512])
            label = resultado[0]["label"]
            
            # Mapear a nuestras categorías
            if "salud" in label.lower():
                return "salud"
            elif "politic" in label.lower():
                return "politica"
            # ...
        except:
            pass
        
        return "otro"
    
    async def calcular_peligro(self, analisis: Dict) -> str:
        """Calcular nivel de peligro del bulo"""
        prob = analisis["probabilidad_bulo"]
        
        if prob > 0.9:
            return "alto"
        elif prob > 0.7:
            return "medio"
        else:
            return "bajo"
    
    async def buscar_fuentes_verificacion(self, texto: str) -> List[Dict]:
        """Buscar fuentes que verifiquen/desmientan"""
        fuentes = []
        
        # Buscar en bases de datos de verificadores
        verificadores = [
            {"nombre": "Maldita.es", "url": "https://maldita.es/buscador/?s="},
            {"nombre": "Newtral", "url": "https://www.newtral.es/?s="},
            {"nombre": "VerificaRTVE", "url": "https://www.rtve.es/noticias/verifica/?s="}
        ]
        
        # Crear query de búsqueda
        query = texto[:100].replace(" ", "+")
        
        for v in verificadores:
            fuentes.append({
                "nombre": v["nombre"],
                "url": v["url"] + query,
                "tipo": "verificador"
            })
        
        return fuentes
