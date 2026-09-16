"""Configuração da aplicação com defaults locais."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Configurações carregadas do ambiente ou de um arquivo .env local."""

    app_name: str = "Livro Vivo de Receitas"
    database_url: str = f"sqlite:///{(PROJECT_ROOT / 'data' / 'app.db').as_posix()}"
    uploads_dir: Path = PROJECT_ROOT / "uploads"
    import_ocr_provider: str = "mock"
    import_parser: str = "rule_based"

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
