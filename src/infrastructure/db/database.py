"""
Configuración de la base de datos con SQLAlchemy.

Este módulo inicializa el motor de conexión, la fábrica de sesiones
y la clase base para los modelos ORM. También expone la función
get_db() que FastAPI usa como dependencia inyectada en cada endpoint,
garantizando que cada request tenga su propia sesión y que esta se
cierre correctamente al finalizar.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from src.config import settings


class Base(DeclarativeBase):
    """
    Clase base para todos los modelos ORM de la aplicación.

    Todos los modelos deben heredar de esta clase para que SQLAlchemy
    los registre y pueda crear sus tablas correspondientes.
    """
    pass


engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
    echo=settings.is_development(),
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db():
    """
    Generador que provee una sesión de base de datos por request.

    Se usa como dependencia inyectada en los endpoints de FastAPI mediante
    Depends(get_db). Garantiza que la sesión se cierre siempre al finalizar
    el request, incluso si ocurre una excepción durante el procesamiento.

    Yields:
        Session: Sesión activa de SQLAlchemy lista para realizar consultas.

    Example:
        @app.get("/products")
        def get_products(db: Session = Depends(get_db)):
            ...
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Inicializa la base de datos creando todas las tablas definidas en los modelos.

    Importa los modelos ORM para que SQLAlchemy los registre en el metadata
    de Base antes de ejecutar create_all(). Luego carga los datos iniciales
    si la base de datos está vacía.

    Este función debe llamarse una única vez al iniciar la aplicación,
    típicamente en el evento startup de FastAPI.

    Returns:
        None
    """
    from src.infrastructure.db import models  # noqa: F401
    from src.infrastructure.db.init_data import load_initial_data

    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()
    try:
        load_initial_data(db)
    finally:
        db.close()