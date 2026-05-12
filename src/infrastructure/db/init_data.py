"""
Datos iniciales para la base de datos.

Este módulo carga un conjunto de productos de ejemplo al iniciar
la aplicación por primera vez. Si ya existen productos en la base
de datos, la función no hace nada para evitar duplicados.
"""

from sqlalchemy.orm import Session

from src.infrastructure.db.models import ProductModel


def load_initial_data(db: Session) -> None:
    """
    Carga productos de ejemplo si la base de datos está vacía.

    Verifica si ya existen registros en la tabla de productos antes
    de insertar. Esto permite que la función se llame en cada arranque
    de la aplicación sin riesgo de duplicar datos.

    Args:
        db (Session): Sesión activa de SQLAlchemy para realizar las
            operaciones de inserción.

    Returns:
        None
    """
    existing_count = db.query(ProductModel).count()

    if existing_count > 0:
        return

    initial_products = [
        ProductModel(
            name="Air Zoom Pegasus 40",
            brand="Nike",
            category="Running",
            size="42",
            color="Negro/Blanco",
            price=130.0,
            stock=8,
            description="Zapatilla de running con amortiguación Zoom Air. "
            "Ideal para rodajes largos gracias a su suela de espuma React.",
        ),
        ProductModel(
            name="Ultraboost 23",
            brand="Adidas",
            category="Running",
            size="41",
            color="Blanco",
            price=160.0,
            stock=5,
            description="Zapatilla premium con tecnología Boost para máxima "
            "devolución de energía. Upper en Primeknit adaptable al pie.",
        ),
        ProductModel(
            name="Suede Classic XXI",
            brand="Puma",
            category="Casual",
            size="40",
            color="Azul Marino",
            price=75.0,
            stock=12,
            description="Icónico modelo casual con parte superior en gamuza "
            "y suela de goma vulcanizada. Clásico atemporal.",
        ),
        ProductModel(
            name="Chuck Taylor All Star",
            brand="Converse",
            category="Casual",
            size="43",
            color="Rojo",
            price=65.0,
            stock=15,
            description="El clásico de los clásicos. Lona duradera, puntera "
            "de goma y estilo icónico que nunca pasa de moda.",
        ),
        ProductModel(
            name="Gel-Kayano 30",
            brand="Asics",
            category="Running",
            size="42",
            color="Gris/Azul",
            price=145.0,
            stock=6,
            description="Zapatilla de running con soporte de pronación y "
            "tecnología GEL para amortiguación superior en largas distancias.",
        ),
        ProductModel(
            name="Old Skool",
            brand="Vans",
            category="Casual",
            size="41",
            color="Negro/Blanco",
            price=70.0,
            stock=20,
            description="Diseño clásico con la icónica franja lateral. "
            "Construcción en lona y ante con suela de goma waffle.",
        ),
        ProductModel(
            name="574 Core",
            brand="New Balance",
            category="Casual",
            size="44",
            color="Gris",
            price=85.0,
            stock=9,
            description="Zapatilla lifestyle con tecnología ENCAP en la "
            "entresuela para soporte y durabilidad. Comodidad todo el día.",
        ),
        ProductModel(
            name="Mercurial Vapor 15",
            brand="Nike",
            category="Fútbol",
            size="40",
            color="Naranja/Negro",
            price=110.0,
            stock=4,
            description="Bota de fútbol de velocidad con placa de carbono "
            "y upper Nike Gripknit para control del balón en superficies duras.",
        ),
        ProductModel(
            name="Stan Smith",
            brand="Adidas",
            category="Formal",
            size="43",
            color="Blanco/Verde",
            price=90.0,
            stock=11,
            description="El referente del estilo minimalista. Piel sintética "
            "premium y diseño limpio que funciona tanto en contextos formales como casuales.",
        ),
        ProductModel(
            name="Cloudstratus 3",
            brand="On Running",
            category="Running",
            size="42",
            color="Negro",
            price=175.0,
            stock=3,
            description="Zapatilla de doble capa de CloudTec para máxima "
            "amortiguación. Diseñada para corredores que buscan estabilidad "
            "en rodajes exigentes.",
        ),
    ]

    db.add_all(initial_products)
    db.commit()