import os
from typing import Generator

from dotenv import load_dotenv
from sqlmodel import Session, SQLModel, create_engine

""" configuración para la conexión a la base de datos """

# Cargar variables de entorno desde .env al iniciar el proceso
load_dotenv()

# Cadena de conexión: toma DATABASE_URL o usa el valor por defecto del enunciado
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:umu192@localhost:5432/rutinas",
)

# Motor de SQLModel/SQLAlchemy (echo=False para no llenar la consola de SQL)
engine = create_engine(DATABASE_URL, echo=False)


def init_db() -> None:
    """Crea las tablas si no existen (se ejecuta en startup)."""
    try:
        SQLModel.metadata.create_all(engine)
        print("✓ Base de datos inicializada correctamente")
    except Exception as e:
        print(f"⚠ Error al inicializar la base de datos: {e}")
        print("   Verifica que PostgreSQL esté corriendo y que la base de datos 'rutinas' exista")
        raise


def get_session() -> Generator[Session, None, None]:
    """Dependencia de FastAPI: entrega una sesión de BD y la cierra al finalizar."""
    with Session(engine) as session:
        yield session


