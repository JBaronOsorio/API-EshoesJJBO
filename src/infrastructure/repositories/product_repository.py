"""
Implementación concreta del repositorio de productos con SQLAlchemy.

Este módulo implementa la interfaz IProductRepository definida en el dominio,
usando SQLAlchemy como ORM para interactuar con la base de datos SQLite.
Contiene los métodos de conversión entre modelos ORM y entidades del dominio,
manteniendo la separación entre capas.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from src.domain.entities import Product
from src.domain.repositories import IProductRepository
from src.infrastructure.db.models import ProductModel


class SQLProductRepository(IProductRepository):
    """
    Repositorio de productos que usa SQLAlchemy para persistir en SQLite.

    Implementa todos los métodos definidos en IProductRepository. Cada método
    trabaja exclusivamente con modelos ORM internamente y retorna entidades
    del dominio hacia afuera, garantizando que las capas superiores nunca
    dependan de SQLAlchemy directamente.

    Attributes:
        db (Session): Sesión activa de SQLAlchemy inyectada por FastAPI.
    """

    def __init__(self, db: Session) -> None:
        """
        Inicializa el repositorio con una sesión de base de datos.

        Args:
            db (Session): Sesión de SQLAlchemy activa para este request.
        """
        self.db = db

    def get_all(self) -> List[Product]:
        """
        Recupera todos los productos de la base de datos.

        Returns:
            List[Product]: Lista de entidades Product. Vacía si no hay registros.
        """
        models = self.db.query(ProductModel).all()
        return [self._model_to_entity(m) for m in models]

    def get_by_id(self, product_id: int) -> Optional[Product]:
        """
        Busca un producto por su ID en la base de datos.

        Args:
            product_id (int): ID del producto a buscar.

        Returns:
            Optional[Product]: Entidad Product si existe, None si no se encuentra.
        """
        model = (
            self.db.query(ProductModel)
            .filter(ProductModel.id == product_id)
            .first()
        )

        if model is None:
            return None

        return self._model_to_entity(model)

    def get_by_brand(self, brand: str) -> List[Product]:
        """
        Recupera todos los productos de una marca específica.

        La comparación es insensible a mayúsculas para mayor flexibilidad.

        Args:
            brand (str): Nombre de la marca a filtrar.

        Returns:
            List[Product]: Lista de productos de esa marca.
        """
        models = (
            self.db.query(ProductModel)
            .filter(ProductModel.brand.ilike(f"%{brand}%"))
            .all()
        )
        return [self._model_to_entity(m) for m in models]

    def get_by_category(self, category: str) -> List[Product]:
        """
        Recupera todos los productos de una categoría específica.

        La comparación es insensible a mayúsculas para mayor flexibilidad.

        Args:
            category (str): Nombre de la categoría a filtrar.

        Returns:
            List[Product]: Lista de productos de esa categoría.
        """
        models = (
            self.db.query(ProductModel)
            .filter(ProductModel.category.ilike(f"%{category}%"))
            .all()
        )
        return [self._model_to_entity(m) for m in models]

    def save(self, product: Product) -> Product:
        """
        Persiste un producto nuevo o actualiza uno existente.

        Si el producto tiene ID, busca el registro existente y actualiza
        sus campos. Si no tiene ID, crea un nuevo registro. En ambos casos
        retorna la entidad con el ID definitivo asignado por la base de datos.

        Args:
            product (Product): Entidad a guardar o actualizar.

        Returns:
            Product: Entidad actualizada con ID asignado.
        """
        if product.id is not None:
            model = (
                self.db.query(ProductModel)
                .filter(ProductModel.id == product.id)
                .first()
            )
            if model:
                model.name = product.name
                model.brand = product.brand
                model.category = product.category
                model.size = product.size
                model.color = product.color
                model.price = product.price
                model.stock = product.stock
                model.description = product.description
            else:
                model = self._entity_to_model(product)
                self.db.add(model)
        else:
            model = self._entity_to_model(product)
            self.db.add(model)

        self.db.commit()
        self.db.refresh(model)
        return self._model_to_entity(model)

    def delete(self, product_id: int) -> bool:
        """
        Elimina un producto de la base de datos por su ID.

        Args:
            product_id (int): ID del producto a eliminar.

        Returns:
            bool: True si se eliminó un registro, False si no existía.
        """
        model = (
            self.db.query(ProductModel)
            .filter(ProductModel.id == product_id)
            .first()
        )

        if model is None:
            return False

        self.db.delete(model)
        self.db.commit()
        return True

    def _model_to_entity(self, model: ProductModel) -> Product:
        """
        Convierte un modelo ORM ProductModel a una entidad de dominio Product.

        Args:
            model (ProductModel): Modelo ORM recuperado de la base de datos.

        Returns:
            Product: Entidad del dominio con los datos del modelo.
        """
        return Product(
            id=model.id,
            name=model.name,
            brand=model.brand,
            category=model.category,
            size=model.size,
            color=model.color,
            price=model.price,
            stock=model.stock,
            description=model.description or "",
        )

    def _entity_to_model(self, product: Product) -> ProductModel:
        """
        Convierte una entidad de dominio Product a un modelo ORM ProductModel.

        Args:
            product (Product): Entidad del dominio a convertir.

        Returns:
            ProductModel: Modelo ORM listo para ser persistido.
        """
        return ProductModel(
            id=product.id,
            name=product.name,
            brand=product.brand,
            category=product.category,
            size=product.size,
            color=product.color,
            price=product.price,
            stock=product.stock,
            description=product.description,
        )