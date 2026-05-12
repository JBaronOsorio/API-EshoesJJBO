"""
Aplicación principal de FastAPI.

Este módulo define la instancia de FastAPI, configura el middleware de CORS,
registra el evento de inicio que inicializa la base de datos y declara todos
los endpoints de la API REST. Actúa como punto de entrada de la capa de
infraestructura hacia el exterior.
"""

from typing import List

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from src.application.chat_service import ChatService
from src.application.dtos import (
    ChatHistoryDTO,
    ChatMessageRequestDTO,
    ChatMessageResponseDTO,
    ProductDTO,
)
from src.application.product_service import ProductService
from src.domain.exceptions import ChatServiceError, ProductNotFoundError
from src.infrastructure.db.database import get_db, init_db
from src.infrastructure.llm_providers.gemini_service import GeminiService
from src.infrastructure.repositories.chat_repository import SQLChatRepository
from src.infrastructure.repositories.product_repository import SQLProductRepository

app = FastAPI(
    title="ShoesAI E-commerce API",
    description=(
        "API REST de e-commerce de zapatos con chat conversacional "
        "potenciado por Google Gemini. Construida con Clean Architecture."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event() -> None:
    """
    Evento que se ejecuta al iniciar la aplicación.

    Inicializa la base de datos creando las tablas necesarias y cargando
    los datos iniciales si la base de datos está vacía. Este evento garantiza
    que la aplicación esté lista para recibir requests desde el primer momento.
    """
    init_db()


@app.get("/", tags=["General"])
def root() -> dict:
    """
    Endpoint raíz con información básica de la API.

    Returns:
        dict: Nombre, versión y lista de endpoints principales disponibles.
    """
    return {
        "name": "ShoesAI E-commerce API",
        "version": "1.0.0",
        "description": "E-commerce de zapatos con chat inteligente",
        "endpoints": {
            "products": "/products",
            "chat": "/chat",
            "docs": "/docs",
            "health": "/health",
        },
    }


@app.get("/health", tags=["General"])
def health_check() -> dict:
    """
    Endpoint de verificación del estado de la aplicación.

    Útil para monitoreo y para verificar que el contenedor Docker
    está corriendo correctamente.

    Returns:
        dict: Estado de la aplicación y timestamp actual.
    """
    from datetime import datetime, timezone

    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/products", response_model=List[ProductDTO], tags=["Productos"])
def get_products(db: Session = Depends(get_db)) -> List[ProductDTO]:
    """
    Retorna la lista completa de productos registrados en el sistema.

    Incluye productos con y sin stock. Para filtrar solo los disponibles,
    usar el parámetro available=true (ver endpoint /products con query params).

    Args:
        db (Session): Sesión de base de datos inyectada por FastAPI.

    Returns:
        List[ProductDTO]: Lista de todos los productos con su información completa.

    Example:
        GET /products
        Response: [{"id": 1, "name": "Air Zoom Pegasus 40", "price": 130.0, ...}]
    """
    product_repo = SQLProductRepository(db)
    service = ProductService(product_repo)
    return service.get_all_products()


@app.get("/products/{product_id}", response_model=ProductDTO, tags=["Productos"])
def get_product_by_id(product_id: int, db: Session = Depends(get_db)) -> ProductDTO:
    """
    Retorna los detalles de un producto específico por su ID.

    Args:
        product_id (int): Identificador único del producto a buscar.
        db (Session): Sesión de base de datos inyectada por FastAPI.

    Returns:
        ProductDTO: Datos completos del producto encontrado.

    Raises:
        HTTPException 404: Si no existe ningún producto con ese ID.

    Example:
        GET /products/1
        Response: {"id": 1, "name": "Air Zoom Pegasus 40", "price": 130.0, ...}
    """
    product_repo = SQLProductRepository(db)
    service = ProductService(product_repo)

    try:
        return service.get_product_by_id(product_id)
    except ProductNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)


@app.post("/chat", response_model=ChatMessageResponseDTO, tags=["Chat"])
async def chat(
    request: ChatMessageRequestDTO,
    db: Session = Depends(get_db),
) -> ChatMessageResponseDTO:
    """
    Procesa un mensaje del usuario y retorna la respuesta del asistente de IA.

    Orquesta el flujo completo: recupera productos, construye el contexto
    conversacional con el historial reciente, genera la respuesta con Gemini
    y persiste el intercambio en la base de datos.

    Args:
        request (ChatMessageRequestDTO): Mensaje del usuario con session_id.
        db (Session): Sesión de base de datos inyectada por FastAPI.

    Returns:
        ChatMessageResponseDTO: Respuesta del asistente con el mensaje original
            y el timestamp del intercambio.

    Raises:
        HTTPException 500: Si ocurre un error al procesar el mensaje o
            comunicarse con la API de Gemini.

    Example:
        POST /chat
        Body: {"session_id": "user_001", "message": "Busco zapatos Nike para correr"}
        Response: {"session_id": "user_001", "user_message": "...", "assistant_message": "..."}
    """
    product_repo = SQLProductRepository(db)
    chat_repo = SQLChatRepository(db)
    ai_service = GeminiService()
    service = ChatService(product_repo, chat_repo, ai_service)

    try:
        return await service.process_message(request)
    except ChatServiceError as e:
        raise HTTPException(status_code=500, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error inesperado al procesar el mensaje: {str(e)}",
        )


@app.get(
    "/chat/history/{session_id}",
    response_model=List[ChatHistoryDTO],
    tags=["Chat"],
)
def get_chat_history(
    session_id: str,
    limit: int = 10,
    db: Session = Depends(get_db),
) -> List[ChatHistoryDTO]:
    """
    Retorna el historial de mensajes de una sesión conversacional.

    Args:
        session_id (str): Identificador único de la sesión a consultar.
        limit (int): Número máximo de mensajes a retornar. Por defecto 10.
        db (Session): Sesión de base de datos inyectada por FastAPI.

    Returns:
        List[ChatHistoryDTO]: Lista de mensajes en orden cronológico.

    Example:
        GET /chat/history/user_001?limit=5
        Response: [{"id": 1, "role": "user", "message": "...", "timestamp": "..."}]
    """
    product_repo = SQLProductRepository(db)
    chat_repo = SQLChatRepository(db)
    ai_service = GeminiService()
    service = ChatService(product_repo, chat_repo, ai_service)
    return service.get_session_history(session_id, limit)


@app.delete("/chat/history/{session_id}", tags=["Chat"])
def delete_chat_history(
    session_id: str,
    db: Session = Depends(get_db),
) -> dict:
    """
    Elimina todo el historial de mensajes de una sesión conversacional.

    Útil para reiniciar una conversación o para cumplir solicitudes
    de borrado de datos por parte del usuario.

    Args:
        session_id (str): Identificador de la sesión a limpiar.
        db (Session): Sesión de base de datos inyectada por FastAPI.

    Returns:
        dict: Confirmación con el número de mensajes eliminados.

    Example:
        DELETE /chat/history/user_001
        Response: {"session_id": "user_001", "deleted_messages": 4}
    """
    product_repo = SQLProductRepository(db)
    chat_repo = SQLChatRepository(db)
    ai_service = GeminiService()
    service = ChatService(product_repo, chat_repo, ai_service)
    deleted = service.clear_session_history(session_id)
    return {"session_id": session_id, "deleted_messages": deleted}

    