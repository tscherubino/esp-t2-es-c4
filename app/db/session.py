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
    _ensure_import_columns()
    _ensure_shopping_columns()


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


def _ensure_import_columns() -> None:
    """Atualiza o banco local para os metadados de revisão de importações."""
    inspector = inspect(engine)
    if "import_jobs" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("import_jobs")}
    additions = {
        "extracted_text": "TEXT",
        "image_original_filename": "VARCHAR(255)",
        "image_stored_filename": "VARCHAR(255)",
        "image_content_type": "VARCHAR(100)",
        "image_relative_path": "VARCHAR(500)",
        "structured_payload": "TEXT",
    }
    with engine.begin() as connection:
        for name, sql_type in additions.items():
            if name not in columns:
                connection.execute(text(f"ALTER TABLE import_jobs ADD COLUMN {name} {sql_type}"))


def _ensure_shopping_columns() -> None:
    """Atualiza bancos locais existentes com observações dos itens."""
    inspector = inspect(engine)
    if "shopping_list_items" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("shopping_list_items")}
    if "notes" not in columns:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE shopping_list_items ADD COLUMN notes VARCHAR(255)"))


def get_db() -> Generator[Session, None, None]:
    """Fornece uma sessão por requisição para os próximos casos de uso."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
