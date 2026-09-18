"""Casos de uso do fluxo manual de receitas."""

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Ingredient, PreparationStep, Recipe, RecipeTag, Tag, User
from app.repositories.recipe_repository import get_recipe, list_recipes
from app.services.storage import delete_image


@dataclass
class RecipeInput:
    """Representa os dados normalizados de uma receita manual.

    Attributes:
        title: Título da receita.
        servings: Quantidade de porções, quando informada.
        prep_time_minutes: Tempo de preparo em minutos, quando informado.
        original_text: Texto original preservado, quando existente.
        origin_story: História ou origem da receita, quando informada.
        ingredient_descriptions: Descrições dos ingredientes.
        ingredient_quantities: Quantidades correspondentes aos ingredientes.
        ingredient_units: Unidades correspondentes aos ingredientes.
        step_instructions: Instruções ordenadas do modo de preparo.
        tags: Tags informadas para a receita.

    """

    title: str
    servings: int | None
    prep_time_minutes: int | None
    original_text: str | None
    origin_story: str | None
    ingredient_descriptions: list[str]
    ingredient_quantities: list[str]
    ingredient_units: list[str]
    step_instructions: list[str]
    tags: list[str]


def clean_values(values: list[str]) -> list[str]:
    """Remove espaços e entradas vazias dos valores recebidos.

    Args:
        values: Valores textuais potencialmente vazios ou com espaços extras.

    Returns:
        Valores não vazios, com espaços externos removidos.

    """
    return [value.strip() for value in values if value.strip()]


def _replace_children(db: Session, recipe: Recipe, data: RecipeInput) -> None:
    """Substitui ingredientes, etapas e tags editáveis da receita.

    Args:
        db: Sessão ativa do banco de dados.
        recipe: Receita cujos componentes serão substituídos.
        data: Dados normalizados dos componentes editáveis.

    Notes:
        A posição dos ingredientes e das etapas é recriada na ordem recebida.
        Tags são normalizadas sem diferenciar maiúsculas de minúsculas.

    """
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
                quantity=quantities[position].strip()
                if position < len(quantities)
                else None,
                unit=units[position].strip() if position < len(units) else None,
                position=position,
            )
        )

    for position, instruction in enumerate(clean_values(data.step_instructions)):
        recipe.preparation_steps.append(
            PreparationStep(position=position, instruction=instruction)
        )

    tag_names = dict.fromkeys(name.casefold() for name in clean_values(data.tags))
    for normalized_name in tag_names:
        tag = db.scalar(
            select(Tag).where(
                Tag.user_id == recipe.user_id, Tag.name == normalized_name
            )
        )
        if tag is None:
            tag = Tag(user_id=recipe.user_id, name=normalized_name)
            db.add(tag)
            db.flush()
        recipe_tag = RecipeTag(tag=tag)
        recipe.recipe_tags.append(recipe_tag)
        db.add(recipe_tag)


def create_recipe(
    db: Session, user: User, data: RecipeInput, *, commit: bool = True
) -> Recipe:
    """Cria uma receita e seus componentes editáveis.

    Args:
        db: Sessão ativa do banco de dados.
        user: Usuário proprietário da receita.
        data: Dados normalizados da receita.
        commit: Quando verdadeiro, confirma a transação; caso contrário,
            apenas envia as alterações para a sessão.

    Returns:
        A entidade `Recipe` criada e vinculada à sessão.

    """
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


def update_recipe(
    db: Session, recipe: Recipe, data: RecipeInput, *, commit: bool = True
) -> Recipe:
    """Atualiza os dados principais e componentes editáveis da receita.

    Args:
        db: Sessão ativa do banco de dados.
        recipe: Receita existente que será atualizada.
        data: Novos dados normalizados da receita.
        commit: Quando verdadeiro, confirma a transação; caso contrário,
            apenas envia as alterações para a sessão.

    Returns:
        A entidade `Recipe` atualizada e vinculada à sessão.

    """
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
    """Exclui a receita e trata seus dados relacionados.

    Args:
        db: Sessão ativa do banco de dados.
        recipe: Receita que será excluída.

    Notes:
        Imagens e jobs de importação associados são removidos. Itens de listas
        de compras são preservados, mas deixam de apontar para a receita.

    """
    for image in recipe.images:
        delete_image(image.stored_filename)
    for import_job in list(recipe.import_jobs):
        db.delete(import_job)
    for shopping_item in list(recipe.shopping_list_items):
        shopping_item.recipe_id = None
    db.delete(recipe)
    db.commit()


__all__ = [
    "RecipeInput",
    "create_recipe",
    "delete_recipe",
    "get_recipe",
    "list_recipes",
    "update_recipe",
]
