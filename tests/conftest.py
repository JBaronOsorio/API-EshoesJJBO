"""
Configuración y fixtures compartidas para los tests del proyecto.

Este módulo define los objetos de prueba reutilizables que se inyectan
automáticamente en los tests mediante el sistema de fixtures de pytest.
"""

from datetime import datetime, timezone

import pytest

from src.domain.entities import ChatContext, ChatMessage, Product


@pytest.fixture
def valid_product() -> Product:
    """
    Retorna un producto válido para usar en tests.

    Returns:
        Product: Instancia de producto con todos los campos válidos.
    """
    return Product(
        id=1,
        name="Air Zoom Pegasus 40",
        brand="Nike",
        category="Running",
        size="42",
        color="Negro/Blanco",
        price=130.0,
        stock=8,
        description="Zapatilla de running con amortiguación Zoom Air.",
    )


@pytest.fixture
def zero_stock_product() -> Product:
    """
    Retorna un producto sin stock disponible para tests de disponibilidad.

    Returns:
        Product: Instancia de producto con stock en cero.
    """
    return Product(
        id=2,
        name="Ultraboost 23",
        brand="Adidas",
        category="Running",
        size="41",
        color="Blanco",
        price=160.0,
        stock=0,
        description="Zapatilla premium con tecnología Boost.",
    )


@pytest.fixture
def user_message() -> ChatMessage:
    """
    Retorna un mensaje de usuario válido para usar en tests.

    Returns:
        ChatMessage: Mensaje con role 'user'.
    """
    return ChatMessage(
        id=1,
        session_id="session_test_001",
        role="user",
        message="Busco zapatos Nike para correr",
        timestamp=datetime.now(timezone.utc),
    )


@pytest.fixture
def assistant_message() -> ChatMessage:
    """
    Retorna un mensaje de asistente válido para usar en tests.

    Returns:
        ChatMessage: Mensaje con role 'assistant'.
    """
    return ChatMessage(
        id=2,
        session_id="session_test_001",
        role="assistant",
        message="Tenemos el Air Zoom Pegasus 40 disponible en talla 42.",
        timestamp=datetime.now(timezone.utc),
    )


@pytest.fixture
def chat_context(user_message: ChatMessage, assistant_message: ChatMessage) -> ChatContext:
    """
    Retorna un contexto conversacional con dos mensajes para tests.

    Args:
        user_message: Fixture del mensaje de usuario.
        assistant_message: Fixture del mensaje del asistente.

    Returns:
        ChatContext: Contexto con un intercambio completo de mensajes.
    """
    return ChatContext(messages=[user_message, assistant_message])