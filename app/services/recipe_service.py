"""Casos de uso do fluxo manual de receitas."""

from dataclasses import dataclass
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Ingredient, PreparationStep, Recipe, RecipeImage, RecipeTag, Tag, User
from app.repositories.recipe_repository import get_recipe, list_recipes
from app.services.storage import delete_image


@dataclass
class RecipeInput:
    """Dados normalizados usados para criar ou atualizar uma receita manual."""
    title: str
    servings: Optional[int]
    prep_time_minutes: Optional[int]
    original_text: Optional[str]
    origin_story: Optional[str]
    ingredient_descriptions: list[str]
    ingredient_quantities: list[str]
    ingredient_units: list[str]
    step_instructions: list[str]
    tags: list[str]


def clean_values(values: list[str]) -> list[str]:
    """Remove espaços e entradas vazias de uma lista de valores do formulário."""
    return [value.strip() for value in values if value.strip()]


def _replace_children(db: Session, recipe: Recipe, data: RecipeInput) -> None:
    """Substitui ingredientes, etapas e tags preservando a posição dos itens."""
    recipe.ingredients.clear()
    recipe.preparation_steps.clear()
    old_recipe_tags = list(recipe.recipe_tags)
    recipe.recipe_tags.clear()
    for recipe_tag in old_recipe_tags:
        db.delete(recipe_tag)
    db.flush()

    descriptions = clean_values(data.ingredient_descriptions)
    quantities = data.ingredient_quantities
    units = data.ingredient_units
    for position, description in enumerate(descriptions):
        recipe.ingredients.append(
            Ingredient(
                description=description,
                quantity=quantities[position].strip() if position < len(quantities) else None,
                unit=units[position].strip() if position < len(units) else None,
                position=position,
            )
        )

    for position, instruction in enumerate(clean_values(data.step_instructions)):
        recipe.preparation_steps.append(PreparationStep(position=position, instruction=instruction))

    tag_names = dict.fromkeys(name.casefold() for name in clean_values(data.tags))
    for normalized_name in tag_names:
        tag = db.scalar(select(Tag).where(Tag.user_id == recipe.user_id, Tag.name == normalized_name))
        if tag is None:
            tag = Tag(user_id=recipe.user_id, name=normalized_name)
            db.add(tag)
            db.flush()
        recipe_tag = RecipeTag(tag=tag)
        recipe.recipe_tags.append(recipe_tag)
        db.add(recipe_tag)


def create_recipe(db: Session, user: User, data: RecipeInput, *, commit: bool = True) -> Recipe:
    """Cria uma receita e seus dados filhos, confirmando a transação quando solicitado."""
    recipe = Recipe(
        user_id=user.id,
        title=data.title.strip(),
        servings=data.servings,
        prep_time_minutes=data.prep_time_minutes,
        original_text=data.original_text.strip() if data.original_text else None,
        origin_story=data.origin_story.strip() if data.origin_story else None,
    )
    _replace_children(db, recipe, data)
    db.add(recipe)
    if commit:
        db.commit()
    else:
        db.flush()
    return recipe


def update_recipe(db: Session, recipe: Recipe, data: RecipeInput, *, commit: bool = True) -> Recipe:
    """Atualiza os dados principais e substitui os componentes editáveis da receita."""
    recipe.title = data.title.strip()
    recipe.servings = data.servings
    recipe.prep_time_minutes = data.prep_time_minutes
    recipe.original_text = data.original_text.strip() if data.original_text else None
    recipe.origin_story = data.origin_story.strip() if data.origin_story else None
    _replace_children(db, recipe, data)
    if commit:
        db.commit()
    else:
        db.flush()
    return recipe


def delete_recipe(db: Session, recipe: Recipe) -> None:
    """Exclui a receita, imagens, jobs associados e referências em listas de compras."""
    for image in recipe.images:
        delete_image(image.stored_filename)
    for import_job in list(recipe.import_jobs):
        db.delete(import_job)
    for shopping_item in list(recipe.shopping_list_items):
        shopping_item.recipe_id = None
    db.delete(recipe)
    db.commit()


__all__ = ["RecipeInput", "create_recipe", "delete_recipe", "get_recipe", "list_recipes", "update_recipe"]
