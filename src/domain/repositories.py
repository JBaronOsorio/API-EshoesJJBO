"""
Interfaces de repositorios del dominio.

Este módulo define los contratos que deben cumplir las implementaciones
concretas de acceso a datos. Al depender de estas abstracciones en lugar
de implementaciones concretas, la capa de aplicación permanece desacoplada
de la tecnología de persistencia utilizada.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.entities import ChatMessage, Product


class IProductRepository(ABC):
    """
    Contrato para el repositorio de productos.

    Define las operaciones disponibles para acceder y manipular productos
    sin especificar el mecanismo de almacenamiento subyacente. Cualquier
    implementación concreta (SQLite, PostgreSQL, en memoria) debe respetar
    esta interfaz.
    """

    @abstractmethod
    def get_all(self) -> List[Product]:
        """
        Recupera todos los productos registrados en el sistema.

        Returns:
            List[Product]: Lista de productos. Puede estar vacía si no
                hay productos registrados.
        """
        pass

    @abstractmethod
    def get_by_id(self, product_id: int) -> Optional[Product]:
        """
        Busca un producto por su identificador único.

        Args:
            product_id (int): ID del producto a buscar.

        Returns:
            Optional[Product]: El producto encontrado, o None si no existe.
        """
        pass

    @abstractmethod
    def get_by_brand(self, brand: str) -> List[Product]:
        """
        Recupera todos los productos de una marca específica.

        Args:
            brand (str): Nombre de la marca a filtrar (ej: 'Nike', 'Adidas').

        Returns:
            List[Product]: Lista de productos de esa marca. Puede estar vacía.
        """
        pass

    @abstractmethod
    def get_by_category(self, category: str) -> List[Product]:
        """
        Recupera todos los productos de una categoría específica.

        Args:
            category (str): Nombre de la categoría (ej: 'Running', 'Casual').

        Returns:
            List[Product]: Lista de productos de esa categoría. Puede estar vacía.
        """
        pass

    @abstractmethod
    def save(self, product: Product) -> Product:
        """
        Persiste un producto nuevo o actualiza uno existente.

        Si el producto tiene ID, se actualiza el registro existente.
        Si no tiene ID (None), se crea un nuevo registro y se le asigna un ID.

        Args:
            product (Product): Producto a guardar o actualizar.

        Returns:
            Product: El producto después de ser persistido, con su ID asignado
                en caso de ser nuevo.
        """
        pass

    @abstractmethod
    def delete(self, product_id: int) -> bool:
        """
        Elimina un producto del sistema por su ID.

        Args:
            product_id (int): ID del producto a eliminar.

        Returns:
            bool: True si el producto fue eliminado exitosamente,
                False si no se encontró ningún producto con ese ID.
        """
        pass


class IChatRepository(ABC):
    """
    Contrato para el repositorio de mensajes de chat.

    Define las operaciones necesarias para persistir y recuperar el historial
    de conversaciones. La implementación concreta decide el mecanismo de
    almacenamiento, pero debe respetar el orden cronológico de los mensajes.
    """

    @abstractmethod
    def save_message(self, message: ChatMessage) -> ChatMessage:
        """
        Persiste un mensaje de chat en el historial.

        Args:
            message (ChatMessage): Mensaje a guardar. Puede ser del usuario
                o del asistente.

        Returns:
            ChatMessage: El mensaje guardado con su ID asignado por la base
                de datos.
        """
        pass

    @abstractmethod
    def get_session_history(
        self, session_id: str, limit: Optional[int] = None
    ) -> List[ChatMessage]:
        """
        Recupera el historial de mensajes de una sesión.

        Args:
            session_id (str): Identificador de la sesión conversacional.
            limit (Optional[int]): Si se especifica, retorna solo los últimos
                N mensajes. Si es None, retorna el historial completo.

        Returns:
            List[ChatMessage]: Mensajes en orden cronológico (más antiguo primero).
        """
        pass

    @abstractmethod
    def delete_session_history(self, session_id: str) -> int:
        """
        Elimina todos los mensajes de una sesión conversacional.

        Args:
            session_id (str): Identificador de la sesión a limpiar.

        Returns:
            int: Número de mensajes eliminados.
        """
        pass

    @abstractmethod
    def get_recent_messages(self, session_id: str, count: int) -> List[ChatMessage]:
        """
        Recupera los últimos N mensajes de una sesión.

        Se usa para construir el contexto conversacional antes de enviar
        el prompt a Gemini. Los mensajes se retornan en orden cronológico
        para que el modelo los interprete correctamente.

        Args:
            session_id (str): Identificador de la sesión.
            count (int): Número de mensajes recientes a recuperar.

        Returns:
            List[ChatMessage]: Los últimos N mensajes en orden cronológico
                (más antiguo primero).
        """
        pass