"""Ponto de entrada da aplicação FastAPI."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

from app.core.config import settings
from app.db.session import initialize_database


APP_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=APP_DIR / "templates")

settings.uploads_dir.mkdir(parents=True, exist_ok=True)
(settings.uploads_dir.parent / "data").mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Inicializa a estrutura do banco antes de atender requisições."""

    initialize_database()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)


@app.get("/", include_in_schema=False)
def index(request: Request):
    """Renderiza a página inicial mínima do MVP."""

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"app_name": settings.app_name},
    )


@app.get("/health")
def health() -> dict[str, str]:
    """Indica que a aplicação está disponível."""

    return {"status": "ok"}
