"""
Entidades del dominio de la aplicación.

Este módulo define los objetos de negocio principales del sistema.
Las entidades encapsulan tanto los datos como las reglas de negocio
que los gobiernan, sin depender de ningún framework o base de datos.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from src.domain.exceptions import InvalidProductDataError


@dataclass
class Product:
    """
    Entidad que representa un producto (zapato) en el e-commerce.

    Encapsula los datos del producto y las reglas de negocio asociadas,
    como la validación de precios, el control de stock y la verificación
    de disponibilidad para la venta.

    Attributes:
        id (Optional[int]): Identificador único. None si aún no fue persistido.
        name (str): Nombre del producto.
        brand (str): Marca del producto (Nike, Adidas, Puma, etc.).
        category (str): Categoría (Running, Casual, Formal, etc.).
        size (str): Talla del zapato.
        color (str): Color del producto.
        price (float): Precio en dólares. Debe ser mayor a 0.
        stock (int): Unidades disponibles en inventario. No puede ser negativo.
        description (str): Descripción detallada del producto.
    """

    id: Optional[int]
    name: str
    brand: str
    category: str
    size: str
    color: str
    price: float
    stock: int
    description: str

    def __post_init__(self) -> None:
        """
        Ejecuta las validaciones de negocio al momento de crear el producto.

        Se invoca automáticamente por el dataclass después de __init__.
        Garantiza que ningún producto inválido pueda existir en el dominio.

        Raises:
            InvalidProductDataError: Si el nombre está vacío, el precio es
                menor o igual a 0, o el stock es negativo.
        """
        if not self.name or not self.name.strip():
            raise InvalidProductDataError("El nombre del producto no puede estar vacío")

        if self.price <= 0:
            raise InvalidProductDataError(
                f"El precio debe ser mayor a 0, se recibió: {self.price}"
            )

        if self.stock < 0:
            raise InvalidProductDataError(
                f"El stock no puede ser negativo, se recibió: {self.stock}"
            )

    def is_available(self) -> bool:
        """
        Verifica si el producto tiene unidades disponibles para la venta.

        Returns:
            bool: True si hay al menos una unidad en stock, False si está agotado.

        Example:
            >>> product = Product(id=1, name="Nike Air", brand="Nike",
            ...     category="Running", size="42", color="Negro",
            ...     price=120.0, stock=5, description="Zapato de running")
            >>> product.is_available()
            True
        """
        return self.stock > 0

    def reduce_stock(self, quantity: int) -> None:
        """
        Reduce el stock del producto en la cantidad especificada.

        Se usa cuando se confirma una venta. Valida que haya suficiente
        stock disponible antes de realizar la reducción.

        Args:
            quantity (int): Número de unidades a descontar. Debe ser positivo.

        Raises:
            ValueError: Si quantity es menor o igual a 0, o si el stock
                disponible es insuficiente para cubrir la cantidad solicitada.

        Example:
            >>> product.reduce_stock(3)
            >>> print(product.stock)
            2
        """
        if quantity <= 0:
            raise ValueError(
                f"La cantidad a reducir debe ser positiva, se recibió: {quantity}"
            )

        if quantity > self.stock:
            raise ValueError(
                f"Stock insuficiente. Disponible: {self.stock}, solicitado: {quantity}"
            )

        self.stock -= quantity

    def increase_stock(self, quantity: int) -> None:
        """
        Aumenta el stock del producto en la cantidad especificada.

        Se usa cuando se recibe un nuevo lote de mercancía o se revierte
        una venta cancelada.

        Args:
            quantity (int): Número de unidades a agregar. Debe ser positivo.

        Raises:
            ValueError: Si quantity es menor o igual a 0.

        Example:
            >>> product.increase_stock(10)
            >>> print(product.stock)
            15
        """
        if quantity <= 0:
            raise ValueError(
                f"La cantidad a agregar debe ser positiva, se recibió: {quantity}"
            )

        self.stock += quantity


@dataclass
class ChatMessage:
    """
    Entidad que representa un mensaje dentro de una conversación de chat.

    Cada instancia corresponde a un turno de la conversación, ya sea
    del usuario o del asistente de IA. Se persiste en la base de datos
    para mantener el historial conversacional entre sesiones.

    Attributes:
        id (Optional[int]): Identificador único. None si aún no fue persistido.
        session_id (str): Identificador de la sesión conversacional del usuario.
        role (str): Rol del emisor. Solo acepta 'user' o 'assistant'.
        message (str): Contenido del mensaje.
        timestamp (datetime): Momento en que se creó el mensaje.
    """

    id: Optional[int]
    session_id: str
    role: str
    message: str
    timestamp: datetime

    def __post_init__(self) -> None:
        """
        Ejecuta las validaciones de negocio al crear el mensaje.

        Raises:
            ValueError: Si el rol no es válido, el mensaje está vacío,
                o el session_id está vacío.
        """
        valid_roles = {"user", "assistant"}
        if self.role not in valid_roles:
            raise ValueError(
                f"El rol debe ser 'user' o 'assistant', se recibió: '{self.role}'"
            )

        if not self.message or not self.message.strip():
            raise ValueError("El mensaje no puede estar vacío")

        if not self.session_id or not self.session_id.strip():
            raise ValueError("El session_id no puede estar vacío")

    def is_from_user(self) -> bool:
        """
        Indica si el mensaje fue enviado por el usuario.

        Returns:
            bool: True si el rol es 'user'.
        """
        return self.role == "user"

    def is_from_assistant(self) -> bool:
        """
        Indica si el mensaje fue generado por el asistente de IA.

        Returns:
            bool: True si el rol es 'assistant'.
        """
        return self.role == "assistant"


@dataclass
class ChatContext:
    """
    Value object que encapsula el contexto de una conversación.

    Mantiene los mensajes recientes de una sesión para proveer memoria
    conversacional al modelo de IA. Limita la cantidad de mensajes incluidos
    en el contexto para controlar el tamaño del prompt enviado a Gemini.

    Attributes:
        messages (list[ChatMessage]): Lista completa de mensajes de la sesión.
        max_messages (int): Número máximo de mensajes a incluir en el contexto.
            Por defecto 6, equivalente a 3 turnos de conversación.
    """

    messages: list[ChatMessage]
    max_messages: int = field(default=6)

    def get_recent_messages(self) -> list[ChatMessage]:
        """
        Retorna los últimos N mensajes según el límite configurado.

        Usar solo los mensajes más recientes evita que el prompt crezca
        indefinidamente y mantiene la relevancia del contexto.

        Returns:
            list[ChatMessage]: Los últimos max_messages mensajes en orden
                cronológico (más antiguo primero).

        Example:
            >>> context = ChatContext(messages=mensajes, max_messages=4)
            >>> recientes = context.get_recent_messages()
            >>> len(recientes) <= 4
            True
        """
        return self.messages[-self.max_messages :]

    def format_for_prompt(self) -> str:
        """
        Formatea el historial de mensajes recientes como texto para el prompt de IA.

        Genera un string con el historial de la conversación en un formato
        legible que el modelo de lenguaje puede interpretar correctamente
        para mantener coherencia en sus respuestas.

        Returns:
            str: Historial formateado. Cadena vacía si no hay mensajes previos.

        Example:
            >>> context.format_for_prompt()
            'Usuario: Busco zapatos para correr\\nAsistente: Tengo varias opciones...'
        """
        if not self.messages:
            return ""

        lines = []
        role_labels = {"user": "Usuario", "assistant": "Asistente"}

        for msg in self.get_recent_messages():
            label = role_labels.get(msg.role, msg.role.capitalize())
            lines.append(f"{label}: {msg.message}")

        return "\n".join(lines)