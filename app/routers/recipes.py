"""Rotas web e JSON para o fluxo manual de receitas."""

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.repositories.recipe_repository import get_demo_user, get_recipe, list_recipes
from app.schemas.domain import RecipeManualInput
from app.services.recipe_service import RecipeInput, create_recipe, delete_recipe, update_recipe
from app.services.storage import delete_image, save_image
from app.models import RecipeImage


router = APIRouter(prefix="/recipes", tags=["recipes"])
api_router = APIRouter(prefix="/api/recipes", tags=["recipes-api"])
templates = Jinja2Templates(directory=Path(__file__).resolve().parent.parent / "templates")


def to_recipe_input(data: RecipeManualInput) -> RecipeInput:
    """Converte o schema Pydantic do formulário no objeto do serviço de domínio."""
    return RecipeInput(**data.model_dump())


def recipe_context(request: Request, **values: object) -> dict[str, object]:
    """Monta o contexto comum dos templates de receitas."""
    return {"request": request, "app_name": settings.app_name, **values}


@router.get("")
def recipe_list(request: Request, db: Session = Depends(get_db)):
    """Renderiza a listagem de receitas do usuário local."""
    user = get_demo_user(db)
    return templates.TemplateResponse(
        request=request,
        name="recipes/list.html",
        context=recipe_context(request, recipes=list_recipes(db, user)),
    )


@router.get("/new")
def new_recipe(request: Request):
    """Renderiza o formulário vazio para cadastro manual."""
    return templates.TemplateResponse(
        request=request,
        name="recipes/form.html",
        context=recipe_context(request, recipe=None, error=None, mode="create"),
    )


@router.post("")
async def create_manual_recipe(
    request: Request,
    title: Annotated[str, Form()],
    servings: Annotated[int | None, Form()] = None,
    prep_time_minutes: Annotated[int | None, Form()] = None,
    origin_story: Annotated[str | None, Form()] = None,
    original_text: Annotated[str | None, Form()] = None,
    ingredient_descriptions: Annotated[list[str], Form()] = [],
    ingredient_quantities: Annotated[list[str], Form()] = [],
    ingredient_units: Annotated[list[str], Form()] = [],
    step_instructions: Annotated[list[str], Form()] = [],
    tags: Annotated[list[str], Form()] = [],
    image: UploadFile | None = None,
    db: Session = Depends(get_db),
):
    """Recebe e persiste uma receita manual, incluindo imagem opcional."""
    stored_image: tuple[str, str, str] | None = None
    try:
        data = RecipeManualInput(
            title=title,
            servings=servings,
            prep_time_minutes=prep_time_minutes,
            origin_story=origin_story,
            original_text=original_text,
            ingredient_descriptions=ingredient_descriptions,
            ingredient_quantities=ingredient_quantities,
            ingredient_units=ingredient_units,
            step_instructions=step_instructions,
            tags=tags,
        )
        if image is not None and image.filename:
            stored_image = await save_image(image)
        recipe = create_recipe(
            db,
            get_demo_user(db),
            to_recipe_input(data),
            commit=stored_image is None,
        )
        if stored_image is not None:
            stored_filename, content_type, relative_path = stored_image
            recipe.images.append(
                RecipeImage(
                    original_filename=image.filename,
                    stored_filename=stored_filename,
                    content_type=content_type,
                    relative_path=relative_path,
                )
            )
            db.commit()
        return RedirectResponse(f"/recipes/{recipe.public_id}", status_code=303)
    except (ValueError, Exception) as error:
        db.rollback()
        if stored_image is not None:
            delete_image(stored_image[0])
        if isinstance(error, ValueError):
            return templates.TemplateResponse(
                request=request,
                name="recipes/form.html",
                context=recipe_context(request, recipe=None, error=str(error), mode="create"),
                status_code=400,
            )
        raise


@router.get("/{public_id}")
def recipe_detail(public_id: str, request: Request, db: Session = Depends(get_db)):
    """Renderiza os detalhes de uma receita autorizada."""
    recipe = get_recipe(db, public_id, get_demo_user(db))
    if recipe is None:
        raise HTTPException(status_code=404, detail="Receita não encontrada.")
    return templates.TemplateResponse(
        request=request,
        name="recipes/detail.html",
        context=recipe_context(request, recipe=recipe),
    )


@router.get("/{public_id}/edit")
def edit_recipe(public_id: str, request: Request, db: Session = Depends(get_db)):
    """Renderiza o formulário preenchido para edição de uma receita."""
    recipe = get_recipe(db, public_id, get_demo_user(db))
    if recipe is None:
        raise HTTPException(status_code=404, detail="Receita não encontrada.")
    return templates.TemplateResponse(
        request=request,
        name="recipes/form.html",
        context=recipe_context(request, recipe=recipe, error=None, mode="edit"),
    )


@router.post("/{public_id}/edit")
async def update_manual_recipe(
    public_id: str,
    request: Request,
    title: Annotated[str, Form()],
    servings: Annotated[int | None, Form()] = None,
    prep_time_minutes: Annotated[int | None, Form()] = None,
    origin_story: Annotated[str | None, Form()] = None,
    original_text: Annotated[str | None, Form()] = None,
    ingredient_descriptions: Annotated[list[str], Form()] = [],
    ingredient_quantities: Annotated[list[str], Form()] = [],
    ingredient_units: Annotated[list[str], Form()] = [],
    step_instructions: Annotated[list[str], Form()] = [],
    tags: Annotated[list[str], Form()] = [],
    image: UploadFile | None = None,
    db: Session = Depends(get_db),
):
    """Atualiza uma receita manual e substitui sua imagem quando enviada."""
    recipe = get_recipe(db, public_id, get_demo_user(db))
    if recipe is None:
        raise HTTPException(status_code=404, detail="Receita não encontrada.")
    data = RecipeManualInput(
        title=title,
        servings=servings,
        prep_time_minutes=prep_time_minutes,
        origin_story=origin_story,
        original_text=original_text,
        ingredient_descriptions=ingredient_descriptions,
        ingredient_quantities=ingredient_quantities,
        ingredient_units=ingredient_units,
        step_instructions=step_instructions,
        tags=tags,
    )
    stored_image: tuple[str, str, str] | None = None
    old_images = list(recipe.images) if image is not None and image.filename else []
    try:
        if image is not None and image.filename:
            stored_image = await save_image(image)
        update_recipe(db, recipe, to_recipe_input(data), commit=stored_image is None)
        if stored_image is not None:
            stored_filename, content_type, relative_path = stored_image
            for old_image in old_images:
                db.delete(old_image)
            recipe.images.append(
                RecipeImage(
                    original_filename=image.filename,
                    stored_filename=stored_filename,
                    content_type=content_type,
                    relative_path=relative_path,
                )
            )
            db.commit()
            for old_image in old_images:
                delete_image(old_image.stored_filename)
    except (ValueError, Exception) as error:
        db.rollback()
        if stored_image is not None:
            delete_image(stored_image[0])
        if isinstance(error, ValueError):
            return templates.TemplateResponse(
                request=request,
                name="recipes/form.html",
                context=recipe_context(request, recipe=recipe, error=str(error), mode="edit"),
                status_code=400,
            )
        raise
    return RedirectResponse(f"/recipes/{recipe.public_id}", status_code=303)


@router.post("/{public_id}/delete")
def remove_recipe(public_id: str, db: Session = Depends(get_db)):
    """Exclui uma receita autorizada e redireciona para a listagem."""
    recipe = get_recipe(db, public_id, get_demo_user(db))
    if recipe is None:
        raise HTTPException(status_code=404, detail="Receita não encontrada.")
    delete_recipe(db, recipe)
    return RedirectResponse("/recipes", status_code=303)


@router.get("/{public_id}/images/{image_public_id}")
def recipe_image(public_id: str, image_public_id: str, db: Session = Depends(get_db)):
    """Entrega uma imagem somente após validar receita, arquivo e diretório local."""
    recipe = get_recipe(db, public_id, get_demo_user(db))
    if recipe is None:
        raise HTTPException(status_code=404, detail="Receita não encontrada.")
    image = next((item for item in recipe.images if item.public_id == image_public_id), None)
    if image is None:
        raise HTTPException(status_code=404, detail="Imagem não encontrada.")
    target = (settings.uploads_dir / Path(image.stored_filename).name).resolve()
    if target.parent != settings.uploads_dir.resolve() or not target.is_file():
        raise HTTPException(status_code=404, detail="Arquivo da imagem não encontrado.")
    return FileResponse(target, media_type=image.content_type, filename=image.original_filename)


@api_router.get("")
def recipe_list_json(db: Session = Depends(get_db)) -> list[dict[str, object]]:
    """Retorna a listagem resumida de receitas em JSON."""
    user = get_demo_user(db)
    return [
        {"public_id": recipe.public_id, "title": recipe.title, "servings": recipe.servings}
        for recipe in list_recipes(db, user)
    ]


@api_router.get("/{public_id}")
def recipe_detail_json(public_id: str, db: Session = Depends(get_db)) -> dict[str, object]:
    """Retorna uma receita autorizada e seus componentes em JSON."""
    recipe = get_recipe(db, public_id, get_demo_user(db))
    if recipe is None:
        raise HTTPException(status_code=404, detail="Receita não encontrada.")
    return {
        "public_id": recipe.public_id,
        "title": recipe.title,
        "servings": recipe.servings,
        "prep_time_minutes": recipe.prep_time_minutes,
        "original_text": recipe.original_text,
        "origin_story": recipe.origin_story,
        "ingredients": [ingredient.description for ingredient in recipe.ingredients],
        "preparation_steps": [step.instruction for step in recipe.preparation_steps],
        "tags": [link.tag.name for link in recipe.recipe_tags],
    }
