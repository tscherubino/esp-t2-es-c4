"""Testes unitários dos services sem depender da interface HTML."""

import asyncio
from uuid import uuid4

import pytest
from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import ShoppingList, ShoppingListItem
from app.processors.providers import MockOCRProvider
from app.repositories.recipe_repository import get_demo_user, get_recipe
from app.schemas.imports import IngredientSuggestion, ImportReviewInput, PreparationStepSuggestion, StructuredRecipe
from app.services.import_service import RecipeImportService, build_ocr_provider, build_recipe_parser
from app.services.recipe_service import RecipeInput, clean_values, create_recipe, delete_recipe, update_recipe
from app.services.shopping_service import (
    ShoppingItemInput,
    add_item,
    consolidate_ingredients,
    delete_shopping_list,
    toggle_item,
    update_item,
)
from app.services.storage import delete_image, save_image_bytes
from app.models import Ingredient


def _recipe_input(suffix: str = "") -> RecipeInput:
    """Cria dados mínimos e determinísticos para os testes do service de receitas."""
    return RecipeInput(
        title=f"Receita unitária {suffix or uuid4().hex}",
        servings=2,
        prep_time_minutes=10,
        original_text="Texto original",
        origin_story="Origem de teste",
        ingredient_descriptions=["Farinha", "Ovos", ""],
        ingredient_quantities=["1", "2"],
        ingredient_units=["xícara", "unidades"],
        step_instructions=["Misture", "Asse", ""],
        tags=["Teste", "teste"],
    )


def test_recipe_service_normalizes_values_and_replaces_children() -> None:
    """Verifica limpeza, criação, atualização e substituição dos filhos da receita."""
    assert clean_values(["  farinha ", "", " ovos"]) == ["farinha", "ovos"]

    with SessionLocal() as db:
        user = get_demo_user(db)
        recipe = create_recipe(db, user, _recipe_input("criação"))
        recipe_id = recipe.public_id
        assert [item.description for item in recipe.ingredients] == ["Farinha", "Ovos"]
        assert [step.instruction for step in recipe.preparation_steps] == ["Misture", "Asse"]
        assert [link.tag.name for link in recipe.recipe_tags] == ["teste"]

        update_recipe(
            db,
            recipe,
            RecipeInput(
                title="Receita atualizada",
                servings=None,
                prep_time_minutes=None,
                original_text=None,
                origin_story=None,
                ingredient_descriptions=["Arroz"],
                ingredient_quantities=[],
                ingredient_units=[],
                step_instructions=["Cozinhe"],
                tags=[],
            ),
        )
        refreshed = get_recipe(db, recipe_id, user)
        assert refreshed is not None
        assert refreshed.title == "Receita atualizada"
        assert [item.description for item in refreshed.ingredients] == ["Arroz"]
        assert [step.instruction for step in refreshed.preparation_steps] == ["Cozinhe"]
        delete_recipe(db, refreshed)
        assert get_recipe(db, recipe_id, user) is None


def test_shopping_service_manages_item_lifecycle() -> None:
    """Verifica criação, edição, marcação e exclusão de item e lista."""
    with SessionLocal() as db:
        user = get_demo_user(db)
        shopping_list = ShoppingList(user_id=user.id, name="Lista unitária")
        db.add(shopping_list)
        db.commit()
        db.refresh(shopping_list)

        item = add_item(db, shopping_list, ShoppingItemInput("  Café ", "1", "pacote", "forte"))
        assert item.description == "Café"
        assert item.notes == "forte"
        update_item(db, item, ShoppingItemInput("Café moído", None, None, None))
        assert item.description == "Café moído"
        assert item.quantity is None
        toggle_item(db, item)
        assert item.is_checked is True

        delete_shopping_list(db, shopping_list)
        assert db.scalar(select(ShoppingList).where(ShoppingList.id == shopping_list.id)) is None
        assert db.scalar(select(ShoppingListItem).where(ShoppingListItem.id == item.id)) is None


def test_shopping_service_handles_empty_and_decimal_edge_cases() -> None:
    """Verifica lista vazia e soma de quantidades decimais com vírgula."""
    with pytest.raises(ValueError, match="Selecione pelo menos uma receita"):
        from app.services.shopping_service import create_list_from_recipes

        with SessionLocal() as db:
            create_list_from_recipes(db, get_demo_user(db), [])

    items, warnings = consolidate_ingredients(
        [
            Ingredient(description="Leite", quantity="1,5", unit="litro"),
            Ingredient(description=" leite ", quantity="0,5", unit="litro"),
        ]
    )
    assert len(items) == 1
    assert items[0].quantity == "2"
    assert warnings == []


def test_storage_service_saves_and_deletes_valid_image() -> None:
    """Verifica ciclo unitário do armazenamento local de uma imagem PNG válida."""
    content = b"\x89PNG\r\n\x1a\n" + b"0" * 32
    stored_filename, content_type, relative_path = save_image_bytes(content, "image/png")
    try:
        assert stored_filename.endswith(".png")
        assert content_type == "image/png"
        assert relative_path.endswith(stored_filename)
    finally:
        delete_image(stored_filename)


def test_import_service_uses_injected_local_providers() -> None:
    """Verifica análise e finalização usando providers injetados, sem serviços externos."""
    structured = StructuredRecipe(
        title="Receita injetada",
        servings="2",
        prep_time_minutes=15,
        ingredients=[IngredientSuggestion(name="Arroz", confidence_score=0.9)],
        preparation_steps=[PreparationStepSuggestion(step_number=1, description="Cozinhe", confidence_score=0.9)],
        suggested_tags=[],
        warnings=[],
    )

    class FakeOCR:
        """Provider de teste que devolve texto controlado."""

        def extract_text(self, image: bytes, manual_transcription=None) -> str:
            """Retorna o texto controlado do cenário unitário."""
            return "Texto da imagem"

    class FakeParser:
        """Parser de teste que devolve uma estrutura controlada."""

        def parse(self, text: str) -> StructuredRecipe:
            """Retorna a estrutura preparada para o teste."""
            return structured

    with SessionLocal() as db:
        user = get_demo_user(db)
        service = RecipeImportService(FakeOCR(), FakeParser())
        job, result, source_text = asyncio.run(service.analyze(db, user, " Texto original ", None))
        assert result.title == "Receita injetada"
        assert source_text == "Texto original"
        assert job.status == "completed"

        recipe = service.finalize(
            db,
            job,
            user,
            ImportReviewInput(
                title="Receita revisada",
                ingredient_names=["Arroz"],
                preparation_steps=["Cozinhe"],
            ),
        )
        assert recipe.title == "Receita revisada"
        assert job.recipe_id == recipe.id
        delete_recipe(db, recipe)


def test_import_provider_factories_return_local_defaults() -> None:
    """Verifica que as fábricas usam implementações locais por padrão."""
    assert isinstance(build_ocr_provider(), MockOCRProvider)
    assert build_recipe_parser().__class__.__name__ in {"RuleBasedRecipeParser", "MockLLMRecipeParser"}
