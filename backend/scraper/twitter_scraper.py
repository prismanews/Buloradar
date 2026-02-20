import tweepy
import asyncio
from typing import List, Dict
import os
from datetime import datetime, timedelta
import re

class TwitterScraper:
    def __init__(self):
        # Configurar API de Twitter/X
        self.bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
        self.client = tweepy.Client(bearer_token=self.bearer_token)
        
        # Palabras clave a monitorizar
        self.keywords = [
            "bulo", "fake", "mentira", "noticia falsa", 
            "verdad", "realidad", "desmentido",
            "no te creas", "cuidado con", "alerta"
        ]
        
        # Cuentas de verificadores a seguir
        self.verificadores = [
            "maldita", "newtral", "verificartve",
            "efecomprueba", "reuters_fact"
        ]
    
    async def scan_tendencias(self) -> List[Dict]:
        """Escanear tendencias y bulos potenciales"""
        resultados = []
        
        try:
            # Buscar tweets recientes con keywords
            for keyword in self.keywords:
                tweets = await self.buscar_tweets(keyword, 100)
                resultados.extend(tweets)
            
            # Buscar menciones a verificadores
            for cuenta in self.verificadores:
                menciones = await self.buscar_menciones(cuenta, 50)
                resultados.extend(menciones)
            
            # Filtrar duplicados
            resultados = self.eliminar_duplicados(resultados)
            
            # Analizar viralidad
            for tweet in resultados:
                tweet["viralidad"] = self.calcular_viralidad(tweet)
            
        except Exception as e:
            print(f"Error en scraping Twitter: {e}")
        
        return resultados
    
    async def buscar_tweets(self, query: str, max_results: int) -> List[Dict]:
        """Buscar tweets por query"""
        tweets_data = []
        
        try:
            # Ejecutar búsqueda
            response = self.client.search_recent_tweets(
                query=query,
                max_results=max_results,
                tweet_fields=["created_at", "public_metrics", "entities"],
                expansions=["author_id"]
            )
            
            if response.data:
                for tweet in response.data:
                    tweet_data = {
                        "id": tweet.id,
                        "texto": tweet.text,
                        "fecha": tweet.created_at,
                        "likes": tweet.public_metrics["like_count"],
                        "retweets": tweet.public_metrics["retweet_count"],
                        "respuestas": tweet.public_metrics["reply_count"],
                        "url": f"https://twitter.com/i/web/status/{tweet.id}"
                    }
                    
                    # Extraer enlaces
                    if tweet.entities and "urls" in tweet.entities:
                        tweet_data["enlaces"] = [url["expanded_url"] for url in tweet.entities["urls"]]
                    
                    tweets_data.append(tweet_data)
        
        except Exception as e:
            print(f"Error buscando tweets: {e}")
        
        return tweets_data
    
    async def buscar_menciones(self, cuenta: str, max_results: int) -> List[Dict]:
        """Buscar menciones a verificadores"""
        return await self.buscar_tweets(f"@{cuenta}", max_results)
    
    def calcular_viralidad(self, tweet: Dict) -> int:
        """Calcular score de viralidad"""
        return tweet.get("likes", 0) * 2 + tweet.get("retweets", 0) * 3
    
    def eliminar_duplicados(self, tweets: List[Dict]) -> List[Dict]:
        """Eliminar tweets duplicados por ID"""
        vistos = set()
        unicos = []
        
        for tweet in tweets:
            if tweet["id"] not in vistos:
                vistos.add(tweet["id"])
                unicos.append(tweet)
        
        return unicos

    async def get_tendencias_virales(self) -> List[Dict]:
        """Obtener tendencias virales de la última hora"""
        # Buscar tweets de la última hora con alta interacción
        desde = datetime.now() - timedelta(hours=1)
        
        tweets = await self.buscar_tweets("min_faves:1000", 50)
        
        # Filtrar por fecha
        recientes = [t for t in tweets if t["fecha"] > desde]
        
        # Ordenar por viralidad
        return sorted(recientes, key=lambda x: x["viralidad"], reverse=True)
