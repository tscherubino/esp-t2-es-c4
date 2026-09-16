"""Página de apresentação do futuro fluxo de lista de compras."""

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from app.core.config import settings


router = APIRouter(tags=["shopping-list"])
templates = Jinja2Templates(directory=Path(__file__).resolve().parent.parent / "templates")


@router.get("/shopping-list")
def shopping_list(request: Request):
    """Apresenta o estado vazio até a funcionalidade de compras ser implementada."""

    return templates.TemplateResponse(
        request=request,
        name="shopping_list.html",
        context={"app_name": settings.app_name},
    )
