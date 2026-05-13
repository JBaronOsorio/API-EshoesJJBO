# ShoesAI — E-commerce con Chat Inteligente

API REST de e-commerce de zapatos con asistente conversacional potenciado por Google Gemini.
Construida aplicando Clean Architecture con tres capas bien definidas.

**Universidad EAFIT — Taller de Arquitectura de Software**

---

## Tabla de Contenidos

1. [Descripción](#descripción)
2. [Arquitectura](#arquitectura)
3. [Tecnologías](#tecnologías)
4. [Estructura del Proyecto](#estructura-del-proyecto)
5. [Instalación](#instalación)
6. [Configuración](#configuración)
7. [Uso](#uso)
8. [Endpoints](#endpoints)
9. [Docker](#docker)
10. [Tests](#tests)
11. [Autor](#autor)

---

## Descripción

ShoesAI es una API REST que combina funcionalidad de e-commerce tradicional con un chat
conversacional inteligente. Los usuarios pueden consultar el catálogo de zapatos mediante
endpoints REST convencionales o interactuar con un asistente de IA que conoce el inventario
y mantiene memoria de la conversación entre mensajes.

### Funcionalidades principales

- Consulta y filtrado de productos por marca y categoría
- Chat conversacional con Google Gemini que conoce el inventario en tiempo real
- Memoria conversacional por sesión (últimos 6 mensajes como contexto)
- Historial de conversaciones persistido en base de datos
- Documentación interactiva automática con Swagger UI

---

## Arquitectura

El proyecto implementa **Clean Architecture** con tres capas bien delimitadas:

┌─────────────────────────────────────────────────────┐
│                 INFRASTRUCTURE LAYER                │
│         FastAPI · SQLAlchemy · Gemini SDK           │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│                 APPLICATION LAYER                   │
│             Services · DTOs (Pydantic)              │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│                   DOMAIN LAYER                      │
│          Entities · Interfaces · Exceptions         │
└─────────────────────────────────────────────────────┘

**Regla de dependencias:** las capas externas dependen de las internas, nunca al revés.
El dominio no conoce SQLAlchemy ni Gemini. La capa de aplicación no conoce FastAPI.

---

## Tecnologías

| Tecnología | Versión | Propósito |
|---|---|---|
| Python | 3.11 | Lenguaje principal |
| FastAPI | 0.115.12 | Framework web y documentación automática |
| SQLAlchemy | 2.0.40 | ORM para base de datos |
| SQLite | — | Base de datos de persistencia |
| Pydantic | 2.11.4 | Validación de datos y DTOs |
| Google GenAI SDK | 1.10.0 | Integración con Gemini 2.5 Flash |
| Docker | — | Containerización |
| Pytest | 8.3.5 | Tests unitarios |

> **Nota técnica:** el taller original sugería el SDK `google-generativeai`, descontinuado
> en noviembre de 2025. Se usa `google-genai` que es el SDK oficial activo mantenido por Google.

---

## Estructura del Proyecto
```
e-commerce-chat-ai/
├── src/
│   ├── config.py                          # Configuración global (variables de entorno)
│   ├── domain/                            # Capa de dominio
│   │   ├── entities.py                    # Product, ChatMessage, ChatContext
│   │   ├── repositories.py                # IProductRepository, IChatRepository
│   │   └── exceptions.py                  # Excepciones de negocio
│   ├── application/                       # Capa de aplicación
│   │   ├── dtos.py                        # DTOs con validación Pydantic
│   │   ├── product_service.py             # Casos de uso de productos
│   │   └── chat_service.py                # Caso de uso de chat con IA
│   └── infrastructure/                    # Capa de infraestructura
│       ├── api/main.py                    # Endpoints FastAPI
│       ├── db/                            # Base de datos
│       │   ├── database.py                # Engine, sesiones, init_db
│       │   ├── models.py                  # Modelos ORM
│       │   └── init_data.py               # Datos iniciales (10 productos)
│       ├── repositories/                  # Implementaciones con SQLAlchemy
│       │   ├── product_repository.py
│       │   └── chat_repository.py
│       └── llm_providers/
│           └── gemini_service.py          # Integración con Google Gemini
├── tests/
│   ├── conftest.py                        # Fixtures compartidas
│   ├── test_entities.py                   # Tests de entidades del dominio
│   └── test_services.py                   # Tests de servicios con mocks
├── evidencias/                            # Screenshots requeridos
├── .env.example                           # Plantilla de variables de entorno
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── pyproject.toml
```
---

## Instalación

### Requisitos previos

- Python 3.11 o superior
- Docker y Docker Compose
- API Key de Google Gemini ([obtener aquí](https://aistudio.google.com/app/apikey))

### Pasos

**1. Clonar el repositorio**

```bash
git clone https://github.com/TU-USUARIO/e-commerce-chat-ai.git
cd e-commerce-chat-ai
```

**2. Crear entorno virtual e instalar dependencias**

```bash
python3 -m venv venv
source venv/bin/activate       # Mac/Linux
# venv\Scripts\activate        # Windows

pip install -r requirements.txt
```

**3. Configurar variables de entorno**

```bash
cp .env.example .env
# Editar .env y agregar tu GEMINI_API_KEY
```

---

## Configuración

El archivo `.env` requiere las siguientes variables:

```bash
GEMINI_API_KEY=tu_api_key_de_google_gemini
DATABASE_URL=sqlite:///./data/ecommerce_chat.db
ENVIRONMENT=development
```

---

## Uso

### Ejecutar en local

```bash
source venv/bin/activate
uvicorn src.infrastructure.api.main:app --reload --port 8000
```

- **API:** http://localhost:8000
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Ejecutar con Docker

```bash
docker-compose up --build
```

---

## Endpoints

### General

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/` | Información básica de la API |
| GET | `/health` | Health check |

### Productos

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/products` | Lista todos los productos |
| GET | `/products/{id}` | Obtiene un producto por ID |

### Chat

| Método | Endpoint | Descripción |
|---|---|---|
| POST | `/chat` | Envía un mensaje al asistente de IA |
| GET | `/chat/history/{session_id}` | Obtiene el historial de una sesión |
| DELETE | `/chat/history/{session_id}` | Elimina el historial de una sesión |

### Ejemplo de uso del chat

**Request:**
```json
POST /chat
{
  "session_id": "usuario_001",
  "message": "Busco zapatos Nike para correr en talla 42"
}
```

**Response:**
```json
{
  "session_id": "usuario_001",
  "user_message": "Busco zapatos Nike para correr en talla 42",
  "assistant_message": "Tenemos el Air Zoom Pegasus 40 de Nike disponible en talla 42 por $130. Contamos con 8 unidades en stock. Es ideal para running con amortiguación Zoom Air. ¿Te interesa?",
  "timestamp": "2026-05-13T07:22:20Z"
}
```

---

## Docker

```bash
# Construir y levantar
docker-compose up --build

# Correr en segundo plano
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener
docker-compose down
```

---

## Tests

```bash
# Correr todos los tests con reporte de coverage
pytest --cov=src --cov-report=term-missing -v
```

El proyecto incluye 39 tests unitarios con cobertura del 100% en la capa de dominio
y superior al 90% en la capa de aplicación.

---

## Autor

**Juan José Baron Osorio**


Ingeniería de Sistemas — Universidad EAFIT
