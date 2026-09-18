"""Rotas do Fluxo B — importação assistida e tela de revisão."""

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.repositories.recipe_repository import get_demo_user
from app.schemas.imports import (
    ImportAnalysisResponse,
    ImportReviewInput,
    StructuredRecipe,
)
from app.services.import_service import RecipeImportService

router = APIRouter(prefix="/recipes/import", tags=["imports"])
api_router = APIRouter(prefix="/api/recipes/import", tags=["imports-api"])
templates = Jinja2Templates(directory=Path(__file__).resolve().parent.parent / "templates")
DB_DEPENDENCY = Depends(get_db)


def context(request: Request, **values: object) -> dict[str, object]:
    """Monta o contexto comum dos templates de importação."""
    return {"request": request, "app_name": settings.app_name, **values}


@router.get("")
def import_form(request: Request):
    """Exibe o formulário inicial do fluxo de importação assistida."""
    return templates.TemplateResponse(
        request=request,
        name="recipes/import.html",
        context=context(request, error=None),
    )


async def analyze_import(
    request: Request,
    original_text: Annotated[str | None, Form()] = None,
    manual_transcription: Annotated[str | None, Form()] = None,
    image: UploadFile | None = None,
    db: Session = DB_DEPENDENCY,
):
    """Recebe uma fonte, cria o job local e redireciona para a revisão humana."""
    try:
        job, _, _ = await RecipeImportService().analyze(
            db, get_demo_user(db), original_text, image, manual_transcription
        )
    except ValueError as error:
        return templates.TemplateResponse(
            request=request,
            name="recipes/import.html",
            context=context(request, error=str(error)),
            status_code=400,
        )
    return RedirectResponse(f"/recipes/import/{job.public_id}/review", status_code=303)


router.add_api_route("", analyze_import, methods=["POST"])


@router.get("/{job_public_id}/review")
def review_import(job_public_id: str, request: Request, db: Session = DB_DEPENDENCY):
    """Exibe os dados estruturados de um job antes da persistência definitiva."""
    job = RecipeImportService().get_job(db, job_public_id, get_demo_user(db))
    if job is None:
        raise HTTPException(status_code=404, detail="Importação não encontrada.")
    if job.status == "failed":
        raise HTTPException(status_code=400, detail=job.error_message or "Importação falhou.")
    if not job.structured_payload:
        raise HTTPException(status_code=400, detail="Importação ainda não foi analisada.")
    structured = StructuredRecipe.model_validate_json(job.structured_payload)
    return templates.TemplateResponse(
        request=request,
        name="recipes/import_review.html",
        context=context(request, job=job, structured=structured, error=None),
    )


@router.post("/{job_public_id}/review")
def finalize_import(
    job_public_id: str,
    request: Request,
    title: Annotated[str, Form()],
    servings: Annotated[int | None, Form()] = None,
    prep_time_minutes: Annotated[int | None, Form()] = None,
    origin_story: Annotated[str | None, Form()] = None,
    ingredient_names: Annotated[list[str] | None, Form()] = None,
    ingredient_quantities: Annotated[list[str] | None, Form()] = None,
    ingredient_units: Annotated[list[str] | None, Form()] = None,
    preparation_steps: Annotated[list[str] | None, Form()] = None,
    tags: Annotated[list[str] | None, Form()] = None,
    db: Session = DB_DEPENDENCY,
):
    """Valida a revisão humana e transforma o job concluído em uma receita."""
    service = RecipeImportService()
    user = get_demo_user(db)
    job = service.get_job(db, job_public_id, user)
    if job is None:
        raise HTTPException(status_code=404, detail="Importação não encontrada.")
    try:
        review = ImportReviewInput(
            title=title,
            servings=servings,
            prep_time_minutes=prep_time_minutes,
            origin_story=origin_story,
            ingredient_names=ingredient_names or [],
            ingredient_quantities=ingredient_quantities or [],
            ingredient_units=ingredient_units or [],
            preparation_steps=preparation_steps or [],
            tags=tags or [],
        )
        recipe = service.finalize(db, job, user, review)
    except ValueError as error:
        db.rollback()
        structured = StructuredRecipe.model_validate_json(job.structured_payload or "{}")
        return templates.TemplateResponse(
            request=request,
            name="recipes/import_review.html",
            context=context(request, job=job, structured=structured, error=str(error)),
            status_code=400,
        )
    return RedirectResponse(f"/recipes/{recipe.public_id}", status_code=303)


@api_router.post("/analyze", response_model=ImportAnalysisResponse)
async def analyze_import_json(
    original_text: Annotated[str | None, Form()] = None,
    manual_transcription: Annotated[str | None, Form()] = None,
    image: UploadFile | None = None,
    db: Session = DB_DEPENDENCY,
) -> ImportAnalysisResponse:
    """Executa a análise local pela API e devolve o resultado estruturado."""
    try:
        job, structured, source_text = await RecipeImportService().analyze(
            db, get_demo_user(db), original_text, image, manual_transcription
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return ImportAnalysisResponse(
        import_job_public_id=job.public_id,
        source_text=source_text,
        structured_recipe=structured,
        status=job.status,
    )
