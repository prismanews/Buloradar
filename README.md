# BuloRadar - Fase 2 🚀

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)

## 📡 Sistema de Detección de Bulos en Tiempo Real

BuloRadar es una plataforma que monitoriza redes sociales y medios de comunicación para detectar, verificar y desmentir bulos en tiempo real.

### ✨ Características Fase 2

- ✅ **Web moderna** con diseño neo-brutalista
- ✅ **API REST** con FastAPI
- ✅ **Scrapers automáticos** para Twitter, TikTok, Telegram y medios
- ✅ **Detección con IA** usando GPT y modelos de ML
- ✅ **Base de datos MongoDB** escalable
- ✅ **Extensión para Chrome** que alerta en tiempo real
- ✅ **Sistema de reportes** colaborativo
- ✅ **Panel de administración**
- ✅ **Dockerización completa**

### 🚀 Inicio Rápido

#### Opción 1: Con Docker (recomendado)

```bash
# Clonar repositorio
git clone https://github.com/prismanews/Buroradar.git
cd Buroradar/fase2

# Copiar variables de entorno
cp .env.example .env
# Editar .env con tus claves API

# Levantar todos los servicios
docker-compose up -d

# Acceder a la web
http://localhost

# Acceder a la API
http://localhost:8000/docs
