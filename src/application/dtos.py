"""
Data Transfer Objects (DTOs) de la capa de aplicación.

Este módulo define los objetos usados para transferir datos entre la capa
de infraestructura (API) y la capa de aplicación (servicios). Pydantic
se encarga de la validación automática de tipos y los validadores
personalizados aplican reglas de negocio básicas en el punto de entrada.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator


class ProductDTO(BaseModel):
    """
    DTO para representar un producto en las respuestas de la API.

    Se usa tanto para serializar respuestas (GET /products) como para
    recibir datos al crear o actualizar productos. Pydantic valida
    automáticamente los tipos de cada campo.

    Attributes:
        id (Optional[int]): Identificador del producto. None si es nuevo.
        name (str): Nombre del producto.
        brand (str): Marca del producto.
        category (str): Categoría del producto.
        size (str): Talla del zapato.
        color (str): Color del producto.
        price (float): Precio en dólares. Debe ser mayor a 0.
        stock (int): Unidades en inventario. No puede ser negativo.
        description (str): Descripción detallada del producto.
    """

    id: Optional[int] = None
    name: str
    brand: str
    category: str
    size: str
    color: str
    price: float
    stock: int
    description: str

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, value: float) -> float:
        """
        Valida que el precio sea estrictamente mayor a cero.

        Args:
            value (float): Precio recibido en el request.

        Returns:
            float: El mismo precio si es válido.

        Raises:
            ValueError: Si el precio es menor o igual a 0.
        """
        if value <= 0:
            raise ValueError("El precio debe ser mayor a 0")
        return value

    @field_validator("stock")
    @classmethod
    def stock_must_be_non_negative(cls, value: int) -> int:
        """
        Valida que el stock no sea un valor negativo.

        Args:
            value (int): Stock recibido en el request.

        Returns:
            int: El mismo stock si es válido.

        Raises:
            ValueError: Si el stock es negativo.
        """
        if value < 0:
            raise ValueError("El stock no puede ser negativo")
        return value

    model_config = {"from_attributes": True}


class ChatMessageRequestDTO(BaseModel):
    """
    DTO para recibir mensajes del usuario en el endpoint POST /chat.

    Representa la petición de un cliente que quiere interactuar con el
    asistente de IA. El session_id permite mantener conversaciones
    separadas para distintos usuarios.

    Attributes:
        session_id (str): Identificador único de la sesión del usuario.
        message (str): Contenido del mensaje enviado por el usuario.
    """

    session_id: str
    message: str

    @field_validator("message")
    @classmethod
    def message_not_empty(cls, value: str) -> str:
        """
        Valida que el mensaje no sea una cadena vacía o solo espacios.

        Args:
            value (str): Mensaje recibido del usuario.

        Returns:
            str: El mensaje con espacios extremos eliminados.

        Raises:
            ValueError: Si el mensaje está vacío o contiene solo espacios.
        """
        if not value or not value.strip():
            raise ValueError("El mensaje no puede estar vacío")
        return value.strip()

    @field_validator("session_id")
    @classmethod
    def session_id_not_empty(cls, value: str) -> str:
        """
        Valida que el session_id no sea una cadena vacía o solo espacios.

        Args:
            value (str): Session ID recibido del cliente.

        Returns:
            str: El session_id con espacios extremos eliminados.

        Raises:
            ValueError: Si el session_id está vacío.
        """
        if not value or not value.strip():
            raise ValueError("El session_id no puede estar vacío")
        return value.strip()


class ChatMessageResponseDTO(BaseModel):
    """
    DTO para estructurar la respuesta del endpoint POST /chat.

    Contiene tanto el mensaje original del usuario como la respuesta
    generada por el asistente de IA, junto con metadatos de la sesión.

    Attributes:
        session_id (str): Identificador de la sesión conversacional.
        user_message (str): Mensaje original enviado por el usuario.
        assistant_message (str): Respuesta generada por el asistente de IA.
        timestamp (datetime): Momento en que se procesó el mensaje.
    """

    session_id: str
    user_message: str
    assistant_message: str
    timestamp: datetime


class ChatHistoryDTO(BaseModel):
    """
    DTO para representar un mensaje individual en el historial de chat.

    Se usa en el endpoint GET /chat/history/{session_id} para listar
    todos los mensajes de una sesión en orden cronológico.

    Attributes:
        id (int): Identificador único del mensaje.
        role (str): Rol del emisor ('user' o 'assistant').
        message (str): Contenido del mensaje.
        timestamp (datetime): Momento en que se registró el mensaje.
    """

    id: int
    role: str
    message: str
    timestamp: datetime

    model_config = {"from_attributes": True}