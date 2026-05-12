"""
Modelos ORM de la capa de infraestructura.

Este módulo define la representación de las tablas de la base de datos
usando SQLAlchemy. Los modelos ORM son objetos técnicos de persistencia
y no deben confundirse con las entidades del dominio, aunque comparten
estructura similar.
"""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, Index, Integer, String, Text

from src.infrastructure.db.database import Base


class ProductModel(Base):
    """
    Modelo ORM que representa la tabla 'products' en la base de datos.

    Cada instancia corresponde a un registro de producto almacenado.
    Este modelo se convierte a entidades del dominio en el repositorio,
    nunca se expone directamente a las capas superiores.

    Attributes:
        id (int): Clave primaria autoincremental.
        name (str): Nombre del producto. Máximo 200 caracteres.
        brand (str): Marca del producto. Máximo 100 caracteres.
        category (str): Categoría del producto. Máximo 100 caracteres.
        size (str): Talla del zapato. Máximo 20 caracteres.
        color (str): Color del producto. Máximo 50 caracteres.
        price (float): Precio en dólares.
        stock (int): Unidades disponibles en inventario.
        description (str): Descripción detallada del producto.
    """

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    brand = Column(String(100), nullable=False)
    category = Column(String(100), nullable=False)
    size = Column(String(20), nullable=False)
    color = Column(String(50), nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    description = Column(Text, nullable=True)

    __table_args__ = (
        Index("ix_products_brand", "brand"),
        Index("ix_products_category", "category"),
    )

    def __repr__(self) -> str:
        """Representación legible del modelo para depuración."""
        return f"<ProductModel(id={self.id}, name='{self.name}', brand='{self.brand}')>"


class ChatMemoryModel(Base):
    """
    Modelo ORM que representa la tabla 'chat_memory' en la base de datos.

    Almacena cada mensaje de las conversaciones entre usuarios y el
    asistente de IA. El campo session_id permite agrupar mensajes por
    conversación y está indexado para acelerar las consultas de historial.

    Attributes:
        id (int): Clave primaria autoincremental.
        session_id (str): Identificador de la sesión conversacional.
        role (str): Rol del emisor ('user' o 'assistant').
        message (str): Contenido del mensaje.
        timestamp (datetime): Momento en que se registró el mensaje.
    """

    __tablename__ = "chat_memory"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(100), nullable=False, index=True)
    role = Column(String(20), nullable=False)
    message = Column(Text, nullable=False)
    timestamp = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        """Representación legible del modelo para depuración."""
        return (
            f"<ChatMemoryModel(id={self.id}, "
            f"session_id='{self.session_id}', role='{self.role}')>"
        )