"""Engine e fábrica de sessões SQLAlchemy."""

from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.db.base import Base


connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def initialize_database() -> None:
    """Cria as tabelas declaradas no SQLite local, caso ainda não existam."""

    settings.uploads_dir.parent.joinpath("data").mkdir(parents=True, exist_ok=True)
    # Importa os modelos antes do create_all para registrar todas as tabelas.
    import app.models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _ensure_recipe_columns()


def _ensure_recipe_columns() -> None:
    """Adiciona colunas novas simples ao banco local sem exigir Alembic."""

    inspector = inspect(engine)
    if "recipes" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("recipes")}
    additions = {
        "servings": "INTEGER",
        "prep_time_minutes": "INTEGER",
    }
    with engine.begin() as connection:
        for name, sql_type in additions.items():
            if name not in columns:
                connection.execute(text(f"ALTER TABLE recipes ADD COLUMN {name} {sql_type}"))


def get_db() -> Generator[Session, None, None]:
    """Fornece uma sessão por requisição para os próximos casos de uso."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
