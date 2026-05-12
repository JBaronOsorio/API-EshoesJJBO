"""
Servicio de aplicación para la gestión de productos.

Este módulo implementa los casos de uso relacionados con productos.
Actúa como intermediario entre los endpoints de la API y el repositorio,
aplicando lógica de negocio de alto nivel y transformando entidades
del dominio en DTOs para su exposición.
"""

from typing import List, Optional

from src.application.dtos import ProductDTO
from src.domain.entities import Product
from src.domain.exceptions import InvalidProductDataError, ProductNotFoundError
from src.domain.repositories import IProductRepository


class ProductService:
    """
    Servicio que implementa los casos de uso de gestión de productos.

    Recibe el repositorio por inyección de dependencias, lo que permite
    desacoplar la lógica de negocio del mecanismo de persistencia.
    Los métodos de este servicio son los únicos puntos de entrada válidos
    para operaciones sobre productos en la aplicación.

    Attributes:
        product_repo (IProductRepository): Repositorio de productos inyectado.
    """

    def __init__(self, product_repo: IProductRepository) -> None:
        """
        Inicializa el servicio con el repositorio de productos.

        Args:
            product_repo (IProductRepository): Implementación concreta del
                repositorio a utilizar.
        """
        self.product_repo = product_repo

    def get_all_products(self) -> List[ProductDTO]:
        """
        Recupera todos los productos registrados en el sistema.

        Returns:
            List[ProductDTO]: Lista de productos serializados como DTOs.
                Puede estar vacía si no hay productos registrados.
        """
        products = self.product_repo.get_all()
        return [self._entity_to_dto(p) for p in products]

    def get_product_by_id(self, product_id: int) -> ProductDTO:
        """
        Busca un producto por su identificador único.

        Args:
            product_id (int): ID del producto a buscar.

        Returns:
            ProductDTO: Datos del producto encontrado.

        Raises:
            ProductNotFoundError: Si no existe ningún producto con ese ID.
        """
        product = self.product_repo.get_by_id(product_id)

        if product is None:
            raise ProductNotFoundError(product_id)

        return self._entity_to_dto(product)

    def get_available_products(self) -> List[ProductDTO]:
        """
        Recupera únicamente los productos con stock disponible.

        Filtra sobre todos los productos y retorna solo aquellos
        cuyo método is_available() retorna True.

        Returns:
            List[ProductDTO]: Lista de productos con al menos una unidad en stock.
        """
        products = self.product_repo.get_all()
        available = [p for p in products if p.is_available()]
        return [self._entity_to_dto(p) for p in available]

    def search_products(
        self,
        brand: Optional[str] = None,
        category: Optional[str] = None,
    ) -> List[ProductDTO]:
        """
        Busca productos aplicando filtros opcionales por marca y categoría.

        Si se pasan ambos filtros, se aplica primero el de marca y luego
        se filtra por categoría sobre los resultados. Si no se pasa ningún
        filtro, retorna todos los productos.

        Args:
            brand (Optional[str]): Marca por la que filtrar (ej: 'Nike').
            category (Optional[str]): Categoría por la que filtrar (ej: 'Running').

        Returns:
            List[ProductDTO]: Lista de productos que cumplen los filtros.
        """
        if brand and category:
            by_brand = self.product_repo.get_by_brand(brand)
            products = [p for p in by_brand if p.category.lower() == category.lower()]
        elif brand:
            products = self.product_repo.get_by_brand(brand)
        elif category:
            products = self.product_repo.get_by_category(category)
        else:
            products = self.product_repo.get_all()

        return [self._entity_to_dto(p) for p in products]

    def create_product(self, product_dto: ProductDTO) -> ProductDTO:
        """
        Crea un nuevo producto en el sistema.

        Convierte el DTO a una entidad del dominio (lo que activa las
        validaciones de negocio) y lo persiste mediante el repositorio.

        Args:
            product_dto (ProductDTO): Datos del producto a crear.

        Returns:
            ProductDTO: El producto creado con su ID asignado.

        Raises:
            InvalidProductDataError: Si los datos del DTO no pasan las
                validaciones de la entidad del dominio.
        """
        product = self._dto_to_entity(product_dto)
        saved = self.product_repo.save(product)
        return self._entity_to_dto(saved)

    def update_product(self, product_id: int, product_dto: ProductDTO) -> ProductDTO:
        """
        Actualiza los datos de un producto existente.

        Verifica que el producto exista antes de intentar actualizarlo.
        Reemplaza todos los campos del producto con los valores del DTO.

        Args:
            product_id (int): ID del producto a actualizar.
            product_dto (ProductDTO): Nuevos datos del producto.

        Returns:
            ProductDTO: El producto con los datos actualizados.

        Raises:
            ProductNotFoundError: Si no existe un producto con ese ID.
            InvalidProductDataError: Si los nuevos datos no son válidos.
        """
        existing = self.product_repo.get_by_id(product_id)

        if existing is None:
            raise ProductNotFoundError(product_id)

        updated_product = Product(
            id=product_id,
            name=product_dto.name,
            brand=product_dto.brand,
            category=product_dto.category,
            size=product_dto.size,
            color=product_dto.color,
            price=product_dto.price,
            stock=product_dto.stock,
            description=product_dto.description,
        )

        saved = self.product_repo.save(updated_product)
        return self._entity_to_dto(saved)

    def delete_product(self, product_id: int) -> bool:
        """
        Elimina un producto del sistema.

        Args:
            product_id (int): ID del producto a eliminar.

        Returns:
            bool: True si el producto fue eliminado exitosamente.

        Raises:
            ProductNotFoundError: Si no existe un producto con ese ID.
        """
        existing = self.product_repo.get_by_id(product_id)

        if existing is None:
            raise ProductNotFoundError(product_id)

        return self.product_repo.delete(product_id)

    def _entity_to_dto(self, product: Product) -> ProductDTO:
        """
        Convierte una entidad Product a su representación como ProductDTO.

        Args:
            product (Product): Entidad del dominio a convertir.

        Returns:
            ProductDTO: DTO con los datos del producto.
        """
        return ProductDTO(
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

    def _dto_to_entity(self, dto: ProductDTO) -> Product:
        """
        Convierte un ProductDTO a una entidad del dominio.

        La conversión activa automáticamente las validaciones definidas
        en el método __post_init__ de la entidad Product.

        Args:
            dto (ProductDTO): DTO a convertir.

        Returns:
            Product: Entidad del dominio lista para ser persistida.

        Raises:
            InvalidProductDataError: Si los datos no pasan las validaciones
                de la entidad.
        """
        return Product(
            id=dto.id,
            name=dto.name,
            brand=dto.brand,
            category=dto.category,
            size=dto.size,
            color=dto.color,
            price=dto.price,
            stock=dto.stock,
            description=dto.description,
        )