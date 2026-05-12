"""
Excepciones del dominio de la aplicación.

Este módulo define los errores de negocio específicos del sistema.
A diferencia de las excepciones técnicas, estas representan situaciones
inválidas según las reglas del negocio, no fallas del sistema.
"""


class ProductNotFoundError(Exception):
    """
    Se lanza cuando se intenta acceder a un producto que no existe.

    Esta excepción se usa en la capa de aplicación cuando un repositorio
    no encuentra el producto solicitado por ID u otro criterio.

    Attributes:
        product_id (int | None): El ID del producto que no fue encontrado.
        message (str): Mensaje descriptivo del error.
    """

    def __init__(self, product_id: int | None = None) -> None:
        """
        Inicializa la excepción con un mensaje descriptivo.

        Args:
            product_id (int | None): ID del producto no encontrado.
                Si se omite, se usa un mensaje genérico.
        """
        if product_id is not None:
            self.message = f"Producto con ID {product_id} no encontrado"
        else:
            self.message = "Producto no encontrado"

        self.product_id = product_id
        super().__init__(self.message)


class InvalidProductDataError(Exception):
    """
    Se lanza cuando los datos proporcionados para un producto son inválidos.

    Cubre casos como precio negativo, stock inválido o nombre vacío.
    Se lanza principalmente desde el método __post_init__ de la entidad Product.

    Attributes:
        message (str): Descripción del dato inválido.
    """

    def __init__(self, message: str = "Datos de producto inválidos") -> None:
        """
        Inicializa la excepción con un mensaje descriptivo del error.

        Args:
            message (str): Descripción del problema encontrado en los datos.
        """
        self.message = message
        super().__init__(self.message)


class ChatServiceError(Exception):
    """
    Se lanza cuando ocurre un error durante el procesamiento de un mensaje de chat.

    Puede originarse por fallos en la comunicación con la API de Gemini,
    errores al guardar mensajes en la base de datos, o cualquier otro
    problema en el flujo del chat.

    Attributes:
        message (str): Descripción del error ocurrido.
    """

    def __init__(self, message: str = "Error en el servicio de chat") -> None:
        """
        Inicializa la excepción con un mensaje descriptivo del error.

        Args:
            message (str): Descripción del problema ocurrido en el servicio de chat.
        """
        self.message = message
        super().__init__(self.message)