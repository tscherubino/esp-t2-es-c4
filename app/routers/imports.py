"""Rotas da infraestrutura inicial de importação."""

from pathlib import Path
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Form, Request, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.repositories.recipe_repository import get_demo_user
from app.services.import_service import create_pending_import


router = APIRouter(prefix="/recipes/import", tags=["imports"])
templates = Jinja2Templates(directory=Path(__file__).resolve().parent.parent / "templates")


@router.get("")
def import_form(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="recipes/import.html",
        context={"request": request, "app_name": settings.app_name, "error": None},
    )


@router.post("")
async def import_recipe(
    request: Request,
    original_text: Annotated[Optional[str], Form()] = None,
    image: UploadFile | None = None,
    db: Session = Depends(get_db),
):
    if not (original_text and original_text.strip()) and not (image and image.filename):
        return templates.TemplateResponse(
            request=request,
            name="recipes/import.html",
            context={
                "request": request,
                "app_name": settings.app_name,
                "error": "Informe um texto ou selecione uma imagem.",
            },
            status_code=400,
        )
    try:
        recipe = await create_pending_import(db, get_demo_user(db), original_text, image)
    except ValueError as error:
        db.rollback()
        return templates.TemplateResponse(
            request=request,
            name="recipes/import.html",
            context={"request": request, "app_name": settings.app_name, "error": str(error)},
            status_code=400,
        )
    return RedirectResponse(f"/recipes/{recipe.public_id}", status_code=303)
