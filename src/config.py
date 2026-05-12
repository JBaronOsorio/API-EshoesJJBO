"""
Módulo de configuración global de la aplicación.

Lee las variables de entorno definidas en el archivo .env y las expone
como constantes tipadas para uso en toda la aplicación.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """
    Clase que centraliza la configuración de la aplicación.

    Lee las variables de entorno al momento de instanciarse y
    las expone como atributos tipados. Usar la instancia global
    `settings` en lugar de importar esta clase directamente.

    Attributes:
        gemini_api_key (str): Clave de autenticación para la API de Google Gemini.
        database_url (str): URL de conexión a la base de datos SQLite.
        environment (str): Entorno de ejecución ('development' o 'production').
    """

    def __init__(self) -> None:
        """Inicializa la configuración leyendo las variables de entorno."""
        self.gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
        self.database_url: str = os.getenv(
            "DATABASE_URL", "sqlite:///./data/ecommerce_chat.db"
        )
        self.environment: str = os.getenv("ENVIRONMENT", "development")

    def is_development(self) -> bool:
        """
        Indica si la aplicación está corriendo en modo desarrollo.

        Returns:
            bool: True si el entorno es 'development', False en caso contrario.
        """
        return self.environment == "development"


settings = Settings()