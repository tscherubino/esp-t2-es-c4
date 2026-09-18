"""Rotas web da lista de compras simples."""

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import PlainTextResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.repositories.recipe_repository import get_demo_user, list_recipes
from app.repositories.shopping_repository import get_shopping_item, get_shopping_list, list_shopping_lists
from app.services.shopping_service import (
    ShoppingItemInput,
    add_item,
    create_list_from_recipes,
    delete_shopping_list,
    remove_item,
    shopping_list_text,
    toggle_item,
    update_item,
)


router = APIRouter(tags=["shopping-list"])
templates = Jinja2Templates(directory=Path(__file__).resolve().parent.parent / "templates")


def page_context(request: Request, **values: object) -> dict[str, object]:
    """Monta o contexto comum dos templates de lista de compras."""
    return {"request": request, "app_name": settings.app_name, **values}


def render_page(request: Request, db: Session, user, selected_list=None, error: str | None = None, warnings: list[str] | None = None):
    """Renderiza a tela com listas, receitas e mensagens do fluxo atual."""
    lists = list_shopping_lists(db, user)
    recipes = list_recipes(db, user)
    if selected_list is None and lists:
        selected_list = lists[0]
    return templates.TemplateResponse(
        request=request,
        name="shopping_list.html",
        context=page_context(request, recipes=recipes, shopping_lists=lists, selected_list=selected_list, error=error, warnings=warnings or []),
    )


@router.get("/shopping-list")
def shopping_list(request: Request, list_id: str | None = None, db: Session = Depends(get_db)):
    """Exibe a lista de compras e seleciona uma lista pelo identificador opcional."""
    user = get_demo_user(db)
    selected = get_shopping_list(db, list_id, user) if list_id else None
    return render_page(request, db, user, selected_list=selected)


@router.post("/shopping-list/generate")
def generate_shopping_list(request: Request, recipe_ids: Annotated[list[str], Form()] = [], name: Annotated[str, Form()] = "Lista de compras", db: Session = Depends(get_db)):
    """Gera uma lista a partir das receitas selecionadas."""
    user = get_demo_user(db)
    try:
        shopping_list, warnings = create_list_from_recipes(db, user, recipe_ids, name)
    except ValueError as error:
        return render_page(request, db, user, error=str(error))
    return render_page(request, db, user, selected_list=shopping_list, warnings=warnings)


@router.post("/shopping-list/{list_public_id}/delete")
def delete_shopping_list_route(list_public_id: str, db: Session = Depends(get_db)):
    """Exclui uma lista pertencente ao usuário e seus itens em cascata."""
    user = get_demo_user(db)
    shopping_list = get_shopping_list(db, list_public_id, user)
    if shopping_list is None:
        raise HTTPException(status_code=404, detail="Lista de compras não encontrada.")
    delete_shopping_list(db, shopping_list)
    return RedirectResponse("/shopping-list", status_code=303)


@router.post("/shopping-list/{list_public_id}/items")
def create_shopping_item(list_public_id: str, request: Request, description: Annotated[str, Form()], quantity: Annotated[str | None, Form()] = None, unit: Annotated[str | None, Form()] = None, notes: Annotated[str | None, Form()] = None, db: Session = Depends(get_db)):
    """Adiciona um item manual à lista autorizada."""
    user = get_demo_user(db)
    shopping_list = get_shopping_list(db, list_public_id, user)
    if shopping_list is None:
        raise HTTPException(status_code=404, detail="Lista de compras não encontrada.")
    try:
        add_item(db, shopping_list, ShoppingItemInput(description, quantity, unit, notes))
    except ValueError as error:
        return render_page(request, db, user, selected_list=shopping_list, error=str(error))
    return RedirectResponse(f"/shopping-list?list_id={list_public_id}", status_code=303)


@router.post("/shopping-list/{list_public_id}/items/{item_public_id}/edit")
def edit_shopping_item(list_public_id: str, item_public_id: str, request: Request, description: Annotated[str, Form()], quantity: Annotated[str | None, Form()] = None, unit: Annotated[str | None, Form()] = None, notes: Annotated[str | None, Form()] = None, db: Session = Depends(get_db)):
    """Edita um item pertencente à lista autorizada."""
    user = get_demo_user(db)
    shopping_list = get_shopping_list(db, list_public_id, user)
    if shopping_list is None:
        raise HTTPException(status_code=404, detail="Lista de compras não encontrada.")
    item = get_shopping_item(db, item_public_id, shopping_list)
    if item is None:
        raise HTTPException(status_code=404, detail="Item não encontrado.")
    try:
        update_item(db, item, ShoppingItemInput(description, quantity, unit, notes))
    except ValueError as error:
        return render_page(request, db, user, selected_list=shopping_list, error=str(error))
    return RedirectResponse(f"/shopping-list?list_id={list_public_id}", status_code=303)


@router.post("/shopping-list/{list_public_id}/items/{item_public_id}/toggle")
def toggle_shopping_item(list_public_id: str, item_public_id: str, db: Session = Depends(get_db)):
    """Alterna o estado de compra de um item autorizado."""
    user = get_demo_user(db)
    shopping_list = get_shopping_list(db, list_public_id, user)
    if shopping_list is None:
        raise HTTPException(status_code=404, detail="Lista de compras não encontrada.")
    item = get_shopping_item(db, item_public_id, shopping_list)
    if item is None:
        raise HTTPException(status_code=404, detail="Item não encontrado.")
    toggle_item(db, item)
    return RedirectResponse(f"/shopping-list?list_id={list_public_id}", status_code=303)


@router.post("/shopping-list/{list_public_id}/items/{item_public_id}/delete")
def delete_shopping_item(list_public_id: str, item_public_id: str, db: Session = Depends(get_db)):
    """Remove um item pertencente à lista autorizada."""
    user = get_demo_user(db)
    shopping_list = get_shopping_list(db, list_public_id, user)
    if shopping_list is None:
        raise HTTPException(status_code=404, detail="Lista de compras não encontrada.")
    item = get_shopping_item(db, item_public_id, shopping_list)
    if item is None:
        raise HTTPException(status_code=404, detail="Item não encontrado.")
    remove_item(db, item)
    return RedirectResponse(f"/shopping-list?list_id={list_public_id}", status_code=303)


@router.get("/shopping-list/{list_public_id}/text", response_class=PlainTextResponse)
def shopping_list_as_text(list_public_id: str, db: Session = Depends(get_db)):
    """Retorna uma lista autorizada em formato textual simples."""
    shopping_list = get_shopping_list(db, list_public_id, get_demo_user(db))
    if shopping_list is None:
        raise HTTPException(status_code=404, detail="Lista de compras não encontrada.")
    return shopping_list_text(shopping_list)
