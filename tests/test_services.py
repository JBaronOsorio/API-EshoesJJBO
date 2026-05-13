"""
Tests unitarios para los servicios de la capa de aplicación.

Usa mocks de los repositorios para aislar los servicios de cualquier
dependencia de base de datos o servicios externos, permitiendo testear
la lógica de orquestación de forma rápida y determinista.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.application.chat_service import ChatService
from src.application.dtos import ChatMessageRequestDTO
from src.application.product_service import ProductService
from src.domain.entities import ChatMessage, Product
from src.domain.exceptions import ChatServiceError, ProductNotFoundError


class TestProductService:
    """Tests para ProductService usando un mock de IProductRepository."""

    @pytest.fixture
    def mock_repo(self, valid_product: Product) -> MagicMock:
        """
        Retorna un mock del repositorio de productos con comportamiento predefinido.

        Args:
            valid_product: Fixture del producto válido.

        Returns:
            MagicMock: Mock que simula IProductRepository.
        """
        repo = MagicMock()
        repo.get_all.return_value = [valid_product]
        repo.get_by_id.return_value = valid_product
        repo.save.return_value = valid_product
        repo.delete.return_value = True
        repo.get_by_brand.return_value = [valid_product]
        repo.get_by_category.return_value = [valid_product]
        return repo

    @pytest.fixture
    def service(self, mock_repo: MagicMock) -> ProductService:
        """
        Retorna una instancia de ProductService con el repositorio mockeado.

        Args:
            mock_repo: Fixture del repositorio mock.

        Returns:
            ProductService: Instancia lista para testear.
        """
        return ProductService(mock_repo)

    def test_get_all_products_retorna_lista(self, service: ProductService) -> None:
        """get_all_products debe retornar una lista con los productos del repositorio."""
        result = service.get_all_products()
        assert len(result) == 1
        assert result[0].name == "Air Zoom Pegasus 40"

    def test_get_product_by_id_existente(self, service: ProductService) -> None:
        """get_product_by_id debe retornar el producto cuando existe."""
        result = service.get_product_by_id(1)
        assert result.id == 1
        assert result.brand == "Nike"

    def test_get_product_by_id_inexistente_lanza_excepcion(
        self, service: ProductService, mock_repo: MagicMock
    ) -> None:
        """get_product_by_id debe lanzar ProductNotFoundError si el producto no existe."""
        mock_repo.get_by_id.return_value = None

        with pytest.raises(ProductNotFoundError):
            service.get_product_by_id(999)

    def test_get_available_products_filtra_sin_stock(
        self, mock_repo: MagicMock, valid_product: Product, zero_stock_product: Product
    ) -> None:
        """get_available_products debe retornar solo productos con stock mayor a 0."""
        mock_repo.get_all.return_value = [valid_product, zero_stock_product]
        service = ProductService(mock_repo)

        result = service.get_available_products()
        assert len(result) == 1
        assert result[0].name == "Air Zoom Pegasus 40"

    def test_delete_product_existente(self, service: ProductService) -> None:
        """delete_product debe retornar True cuando el producto existe y se elimina."""
        result = service.delete_product(1)
        assert result is True

    def test_delete_product_inexistente_lanza_excepcion(
        self, service: ProductService, mock_repo: MagicMock
    ) -> None:
        """delete_product debe lanzar ProductNotFoundError si el producto no existe."""
        mock_repo.get_by_id.return_value = None

        with pytest.raises(ProductNotFoundError):
            service.delete_product(999)

    def test_search_products_por_marca(
        self, service: ProductService, mock_repo: MagicMock
    ) -> None:
        """search_products con brand debe llamar a get_by_brand del repositorio."""
        result = service.search_products(brand="Nike")
        mock_repo.get_by_brand.assert_called_once_with("Nike")
        assert len(result) == 1

    def test_search_products_sin_filtros_retorna_todos(
        self, service: ProductService, mock_repo: MagicMock
    ) -> None:
        """search_products sin filtros debe llamar a get_all del repositorio."""
        service.search_products()
        mock_repo.get_all.assert_called_once()


class TestChatService:
    """Tests para ChatService usando mocks de repositorios y servicio de IA."""

    @pytest.fixture
    def mock_product_repo(self, valid_product: Product) -> MagicMock:
        """
        Retorna un mock del repositorio de productos.

        Returns:
            MagicMock: Mock que simula IProductRepository.
        """
        repo = MagicMock()
        repo.get_all.return_value = [valid_product]
        return repo

    @pytest.fixture
    def mock_chat_repo(self) -> MagicMock:
        """
        Retorna un mock del repositorio de chat.

        Returns:
            MagicMock: Mock que simula IChatRepository.
        """
        repo = MagicMock()
        repo.get_recent_messages.return_value = []
        repo.save_message.side_effect = lambda msg: msg
        repo.get_session_history.return_value = []
        repo.delete_session_history.return_value = 3
        return repo

    @pytest.fixture
    def mock_ai_service(self) -> MagicMock:
        """
        Retorna un mock del servicio de IA con respuesta predefinida.

        Returns:
            MagicMock: Mock que simula GeminiService con generate_response async.
        """
        ai = MagicMock()
        ai.generate_response = AsyncMock(
            return_value="Tenemos el Air Zoom Pegasus 40 disponible en talla 42 por $130."
        )
        return ai

    @pytest.fixture
    def service(
        self,
        mock_product_repo: MagicMock,
        mock_chat_repo: MagicMock,
        mock_ai_service: MagicMock,
    ) -> ChatService:
        """
        Retorna una instancia de ChatService con todas las dependencias mockeadas.

        Returns:
            ChatService: Instancia lista para testear.
        """
        return ChatService(mock_product_repo, mock_chat_repo, mock_ai_service)

    @pytest.mark.asyncio
    async def test_process_message_retorna_respuesta(
        self, service: ChatService
    ) -> None:
        """process_message debe retornar un DTO con la respuesta del asistente."""
        request = ChatMessageRequestDTO(
            session_id="session_test_001",
            message="Busco zapatos Nike para correr",
        )

        result = await service.process_message(request)

        assert result.session_id == "session_test_001"
        assert result.user_message == "Busco zapatos Nike para correr"
        assert "Air Zoom Pegasus 40" in result.assistant_message

    @pytest.mark.asyncio
    async def test_process_message_guarda_dos_mensajes(
        self, service: ChatService, mock_chat_repo: MagicMock
    ) -> None:
        """process_message debe persistir el mensaje del usuario y la respuesta."""
        request = ChatMessageRequestDTO(
            session_id="session_test_001",
            message="Hola",
        )

        await service.process_message(request)

        assert mock_chat_repo.save_message.call_count == 2

    @pytest.mark.asyncio
    async def test_process_message_consulta_historial(
        self, service: ChatService, mock_chat_repo: MagicMock
    ) -> None:
        """process_message debe recuperar los mensajes recientes para el contexto."""
        request = ChatMessageRequestDTO(
            session_id="session_test_001",
            message="Hola",
        )

        await service.process_message(request)

        mock_chat_repo.get_recent_messages.assert_called_once_with(
            session_id="session_test_001",
            count=6,
        )

    @pytest.mark.asyncio
    async def test_process_message_fallo_ia_lanza_chat_service_error(
        self,
        mock_product_repo: MagicMock,
        mock_chat_repo: MagicMock,
    ) -> None:
        """process_message debe lanzar ChatServiceError si la IA falla."""
        ai_fallido = MagicMock()
        ai_fallido.generate_response = AsyncMock(
            side_effect=Exception("Timeout de conexión con Gemini")
        )

        service = ChatService(mock_product_repo, mock_chat_repo, ai_fallido)
        request = ChatMessageRequestDTO(
            session_id="session_test_001",
            message="Hola",
        )

        with pytest.raises(ChatServiceError):
            await service.process_message(request)

    def test_get_session_history_retorna_lista(self, service: ChatService) -> None:
        """get_session_history debe retornar la lista de DTOs del historial."""
        result = service.get_session_history("session_test_001", limit=10)
        assert isinstance(result, list)

    def test_clear_session_history_retorna_cantidad(self, service: ChatService) -> None:
        """clear_session_history debe retornar el número de mensajes eliminados."""
        result = service.clear_session_history("session_test_001")
        assert result == 3