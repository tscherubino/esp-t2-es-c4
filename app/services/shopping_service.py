"""Casos de uso da lista de compras simples do MVP."""

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import re

from sqlalchemy.orm import Session

from app.models import Ingredient, Recipe, ShoppingList, ShoppingListItem, User
from app.repositories.recipe_repository import get_recipe


@dataclass
class ShoppingItemInput:
    description: str
    quantity: str | None = None
    unit: str | None = None
    notes: str | None = None


def _normalize(value: str | None) -> str:
    return re.sub(r"\s+", " ", (value or "").strip()).casefold()


def _parse_quantity(value: str | None) -> Decimal | None:
    if not value:
        return None
    normalized = value.strip().replace(",", ".")
    try:
        return Decimal(normalized)
    except InvalidOperation:
        return None


def _format_quantity(value: Decimal) -> str:
    formatted = format(value.normalize(), "f")
    return formatted.rstrip("0").rstrip(".") if "." in formatted else formatted


def _ingredient_to_item(ingredient: Ingredient) -> ShoppingItemInput:
    return ShoppingItemInput(
        description=ingredient.description,
        quantity=ingredient.quantity,
        unit=ingredient.unit,
        notes=ingredient.notes,
    )


def consolidate_ingredients(ingredients: list[Ingredient]) -> tuple[list[ShoppingItemInput], list[str]]:
    """Consolida nome/unidade iguais sem conversões ou inferências complexas."""

    result: list[ShoppingItemInput] = []
    positions: dict[tuple[str, str], int] = {}
    warnings: list[str] = []
    for ingredient in ingredients:
        item = _ingredient_to_item(ingredient)
        key = (_normalize(item.description), _normalize(item.unit))
        existing_position = positions.get(key)
        if existing_position is None:
            positions[key] = len(result)
            result.append(item)
            continue

        existing = result[existing_position]
        first_quantity = _parse_quantity(existing.quantity)
        next_quantity = _parse_quantity(item.quantity)
        if first_quantity is not None and next_quantity is not None:
            existing.quantity = _format_quantity(first_quantity + next_quantity)
            if item.notes:
                existing.notes = "; ".join(filter(None, [existing.notes, item.notes])) or None
        else:
            result.append(item)
            warnings.append(
                f"{item.description}: quantidades iguais não foram somadas porque não são numéricas."
            )

    return result, list(dict.fromkeys(warnings))


def create_list_from_recipes(
    db: Session, user: User, recipe_public_ids: list[str], name: str = "Lista de compras"
) -> tuple[ShoppingList, list[str]]:
    recipes: list[Recipe] = []
    for public_id in dict.fromkeys(recipe_public_ids):
        recipe = get_recipe(db, public_id, user)
        if recipe is None:
            raise ValueError("Uma das receitas selecionadas não foi encontrada.")
        recipes.append(recipe)
    if not recipes:
        raise ValueError("Selecione pelo menos uma receita para gerar a lista.")

    ingredients = [ingredient for recipe in recipes for ingredient in recipe.ingredients]
    items, warnings = consolidate_ingredients(ingredients)
    shopping_list = ShoppingList(user_id=user.id, name=name.strip() or "Lista de compras")
    for item in items:
        shopping_list.items.append(
            ShoppingListItem(
                description=item.description,
                quantity=item.quantity,
                unit=item.unit,
                notes=item.notes,
                recipe_id=recipes[0].id if len(recipes) == 1 else None,
            )
        )
    db.add(shopping_list)
    db.commit()
    db.refresh(shopping_list)
    return shopping_list, warnings


def add_item(db: Session, shopping_list: ShoppingList, data: ShoppingItemInput) -> ShoppingListItem:
    if not data.description.strip():
        raise ValueError("Informe o nome do item.")
    item = ShoppingListItem(
        shopping_list_id=shopping_list.id,
        description=data.description.strip(),
        quantity=data.quantity.strip() if data.quantity else None,
        unit=data.unit.strip() if data.unit else None,
        notes=data.notes.strip() if data.notes else None,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update_item(db: Session, item: ShoppingListItem, data: ShoppingItemInput) -> ShoppingListItem:
    if not data.description.strip():
        raise ValueError("Informe o nome do item.")
    item.description = data.description.strip()
    item.quantity = data.quantity.strip() if data.quantity else None
    item.unit = data.unit.strip() if data.unit else None
    item.notes = data.notes.strip() if data.notes else None
    db.commit()
    return item


def toggle_item(db: Session, item: ShoppingListItem) -> ShoppingListItem:
    item.is_checked = not item.is_checked
    db.commit()
    return item


def remove_item(db: Session, item: ShoppingListItem) -> None:
    db.delete(item)
    db.commit()


def delete_shopping_list(db: Session, shopping_list: ShoppingList) -> None:
    """Exclui uma lista e seus itens vinculados pela cascata do modelo."""
    db.delete(shopping_list)
    db.commit()


def shopping_list_text(shopping_list: ShoppingList) -> str:
    lines = [shopping_list.name]
    for item in shopping_list.items:
        prefix = "[x]" if item.is_checked else "[ ]"
        details = " ".join(filter(None, [item.quantity, item.unit]))
        line = " ".join(filter(None, [prefix, details, item.description]))
        if item.notes:
            line += f" ({item.notes})"
        lines.append(line)
    return "\n".join(lines)


__all__ = [
    "ShoppingItemInput",
    "add_item",
    "consolidate_ingredients",
    "create_list_from_recipes",
    "delete_shopping_list",
    "remove_item",
    "shopping_list_text",
    "toggle_item",
    "update_item",
]
