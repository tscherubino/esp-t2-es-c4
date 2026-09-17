"""Ponto de entrada da aplicação FastAPI."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db, initialize_database
from app.repositories.recipe_repository import get_demo_user, list_recipes
from app.routers import imports, recipes, shopping


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
app.include_router(imports.router)
app.include_router(imports.api_router)
app.include_router(recipes.router)
app.include_router(recipes.api_router)
app.include_router(shopping.router)


@app.get("/", include_in_schema=False)
def index(request: Request, db: Session = Depends(get_db)):
    """Renderiza a página inicial mínima do MVP."""

    recipes = list_recipes(db, get_demo_user(db))

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"app_name": settings.app_name, "recipes": recipes},
    )


@app.get("/health")
def health() -> dict[str, str]:
    """Indica que a aplicação está disponível."""

    return {"status": "ok"}
