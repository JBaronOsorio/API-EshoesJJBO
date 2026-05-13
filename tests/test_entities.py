"""
Tests unitarios para las entidades del dominio.

Verifica que las reglas de negocio definidas en las entidades funcionen
correctamente: validaciones en la creación, métodos de consulta y
operaciones que modifican el estado.
"""

import pytest

from src.domain.entities import ChatContext, ChatMessage, Product
from src.domain.exceptions import InvalidProductDataError


class TestProduct:
    """Tests para la entidad Product."""

    def test_crear_producto_valido(self, valid_product: Product) -> None:
        """Un producto con datos correctos debe crearse sin errores."""
        assert valid_product.name == "Air Zoom Pegasus 40"
        assert valid_product.price == 130.0
        assert valid_product.stock == 8

    def test_precio_cero_lanza_excepcion(self) -> None:
        """Un producto con precio igual a 0 debe lanzar InvalidProductDataError."""
        with pytest.raises(InvalidProductDataError):
            Product(
                id=None,
                name="Zapato Test",
                brand="Test",
                category="Casual",
                size="40",
                color="Negro",
                price=0.0,
                stock=5,
                description="Test",
            )

    def test_precio_negativo_lanza_excepcion(self) -> None:
        """Un producto con precio negativo debe lanzar InvalidProductDataError."""
        with pytest.raises(InvalidProductDataError):
            Product(
                id=None,
                name="Zapato Test",
                brand="Test",
                category="Casual",
                size="40",
                color="Negro",
                price=-10.0,
                stock=5,
                description="Test",
            )

    def test_stock_negativo_lanza_excepcion(self) -> None:
        """Un producto con stock negativo debe lanzar InvalidProductDataError."""
        with pytest.raises(InvalidProductDataError):
            Product(
                id=None,
                name="Zapato Test",
                brand="Test",
                category="Casual",
                size="40",
                color="Negro",
                price=100.0,
                stock=-1,
                description="Test",
            )

    def test_nombre_vacio_lanza_excepcion(self) -> None:
        """Un producto con nombre vacío debe lanzar InvalidProductDataError."""
        with pytest.raises(InvalidProductDataError):
            Product(
                id=None,
                name="   ",
                brand="Test",
                category="Casual",
                size="40",
                color="Negro",
                price=100.0,
                stock=5,
                description="Test",
            )

    def test_is_available_con_stock(self, valid_product: Product) -> None:
        """Un producto con stock mayor a 0 debe estar disponible."""
        assert valid_product.is_available() is True

    def test_is_available_sin_stock(self, zero_stock_product: Product) -> None:
        """Un producto con stock 0 no debe estar disponible."""
        assert zero_stock_product.is_available() is False

    def test_reduce_stock_exitoso(self, valid_product: Product) -> None:
        """Reducir el stock con cantidad válida debe actualizar el stock correctamente."""
        stock_inicial = valid_product.stock
        valid_product.reduce_stock(3)
        assert valid_product.stock == stock_inicial - 3

    def test_reduce_stock_insuficiente_lanza_excepcion(self, valid_product: Product) -> None:
        """Reducir más stock del disponible debe lanzar ValueError."""
        with pytest.raises(ValueError):
            valid_product.reduce_stock(100)

    def test_reduce_stock_cantidad_negativa_lanza_excepcion(self, valid_product: Product) -> None:
        """Reducir el stock con cantidad negativa o cero debe lanzar ValueError."""
        with pytest.raises(ValueError):
            valid_product.reduce_stock(0)

    def test_increase_stock_exitoso(self, valid_product: Product) -> None:
        """Aumentar el stock con cantidad válida debe sumar correctamente."""
        stock_inicial = valid_product.stock
        valid_product.increase_stock(5)
        assert valid_product.stock == stock_inicial + 5

    def test_increase_stock_cantidad_negativa_lanza_excepcion(self, valid_product: Product) -> None:
        """Aumentar el stock con cantidad negativa o cero debe lanzar ValueError."""
        with pytest.raises(ValueError):
            valid_product.increase_stock(-1)

    def test_reduce_stock_deja_en_cero(self, valid_product: Product) -> None:
        """Reducir el stock exactamente al total disponible debe dejar el stock en 0."""
        valid_product.reduce_stock(valid_product.stock)
        assert valid_product.stock == 0
        assert valid_product.is_available() is False


class TestChatMessage:
    """Tests para la entidad ChatMessage."""

    def test_crear_mensaje_usuario_valido(self, user_message: ChatMessage) -> None:
        """Un mensaje de usuario con datos correctos debe crearse sin errores."""
        assert user_message.role == "user"
        assert user_message.session_id == "session_test_001"

    def test_crear_mensaje_asistente_valido(self, assistant_message: ChatMessage) -> None:
        """Un mensaje de asistente con datos correctos debe crearse sin errores."""
        assert assistant_message.role == "assistant"

    def test_rol_invalido_lanza_excepcion(self) -> None:
        """Un mensaje con rol distinto a 'user' o 'assistant' debe lanzar ValueError."""
        from datetime import datetime, timezone

        with pytest.raises(ValueError):
            ChatMessage(
                id=None,
                session_id="session_001",
                role="admin",
                message="Mensaje de prueba",
                timestamp=datetime.now(timezone.utc),
            )

    def test_mensaje_vacio_lanza_excepcion(self) -> None:
        """Un mensaje con contenido vacío debe lanzar ValueError."""
        from datetime import datetime, timezone

        with pytest.raises(ValueError):
            ChatMessage(
                id=None,
                session_id="session_001",
                role="user",
                message="   ",
                timestamp=datetime.now(timezone.utc),
            )

    def test_session_id_vacio_lanza_excepcion(self) -> None:
        """Un mensaje con session_id vacío debe lanzar ValueError."""
        from datetime import datetime, timezone

        with pytest.raises(ValueError):
            ChatMessage(
                id=None,
                session_id="",
                role="user",
                message="Hola",
                timestamp=datetime.now(timezone.utc),
            )

    def test_is_from_user(self, user_message: ChatMessage) -> None:
        """is_from_user debe retornar True para mensajes con role 'user'."""
        assert user_message.is_from_user() is True
        assert user_message.is_from_assistant() is False

    def test_is_from_assistant(self, assistant_message: ChatMessage) -> None:
        """is_from_assistant debe retornar True para mensajes con role 'assistant'."""
        assert assistant_message.is_from_assistant() is True
        assert assistant_message.is_from_user() is False


class TestChatContext:
    """Tests para el value object ChatContext."""

    def test_get_recent_messages_respeta_limite(self) -> None:
        """get_recent_messages debe retornar como máximo max_messages mensajes."""
        from datetime import datetime, timezone

        mensajes = [
            ChatMessage(
                id=i,
                session_id="session_001",
                role="user" if i % 2 == 0 else "assistant",
                message=f"Mensaje {i}",
                timestamp=datetime.now(timezone.utc),
            )
            for i in range(1, 10)
        ]

        context = ChatContext(messages=mensajes, max_messages=4)
        recientes = context.get_recent_messages()
        assert len(recientes) == 4

    def test_get_recent_messages_retorna_los_ultimos(self) -> None:
        """get_recent_messages debe retornar los mensajes más recientes."""
        from datetime import datetime, timezone

        mensajes = [
            ChatMessage(
                id=i,
                session_id="session_001",
                role="user",
                message=f"Mensaje {i}",
                timestamp=datetime.now(timezone.utc),
            )
            for i in range(1, 6)
        ]

        context = ChatContext(messages=mensajes, max_messages=2)
        recientes = context.get_recent_messages()
        assert recientes[0].message == "Mensaje 4"
        assert recientes[1].message == "Mensaje 5"

    def test_format_for_prompt_vacio(self) -> None:
        """format_for_prompt debe retornar cadena vacía si no hay mensajes."""
        context = ChatContext(messages=[])
        assert context.format_for_prompt() == ""

    def test_format_for_prompt_formato_correcto(self, chat_context: ChatContext) -> None:
        """format_for_prompt debe usar los labels 'Usuario' y 'Asistente'."""
        resultado = chat_context.format_for_prompt()
        assert "Usuario:" in resultado
        assert "Asistente:" in resultado

    def test_format_for_prompt_contiene_mensajes(self, chat_context: ChatContext) -> None:
        """format_for_prompt debe incluir el contenido de los mensajes."""
        resultado = chat_context.format_for_prompt()
        assert "Busco zapatos Nike para correr" in resultado
        assert "Air Zoom Pegasus 40" in resultado