from fastapi.testclient import TestClient

from app.main import app
from app.models import Ingredient
from app.services.shopping_service import consolidate_ingredients


def test_consolidates_same_ingredient_and_unit() -> None:
    items, warnings = consolidate_ingredients(
        [
            Ingredient(description="Farinha", quantity="1", unit="xícara"),
            Ingredient(description=" farinha ", quantity="2", unit="xícara"),
            Ingredient(description="Farinha", quantity="1", unit="grama"),
        ]
    )

    assert [(item.description, item.quantity, item.unit) for item in items] == [
        ("Farinha", "3", "xícara"),
        ("Farinha", "1", "grama"),
    ]
    assert warnings == []


def test_keeps_non_numeric_quantities_separate_with_warning() -> None:
    items, warnings = consolidate_ingredients(
        [
            Ingredient(description="Sal", quantity="a gosto", unit=None),
            Ingredient(description="sal", quantity="1 pitada", unit=None),
        ]
    )

    assert len(items) == 2
    assert "quantidades iguais não foram somadas" in warnings[0]


def test_shopping_list_flow_generates_and_manages_items() -> None:
    with TestClient(app) as client:
        created = client.post(
            "/recipes",
            data={
                "title": "Receita para lista de compras",
                "ingredient_descriptions": ["arroz", "arroz", "sal"],
                "ingredient_quantities": ["1", "2", "a gosto"],
                "ingredient_units": ["xícara", "xícara", ""],
                "step_instructions": ["Cozinhe"],
            },
            follow_redirects=False,
        )
        recipe_id = created.headers["location"].rsplit("/", 1)[-1]

        generated = client.post(
            "/shopping-list/generate",
            data={"recipe_ids": [recipe_id], "name": "Mercado da semana"},
        )
        assert generated.status_code == 200
        assert "Mercado da semana" in generated.text
        assert "Excluir" in generated.text
        assert "3 xícara de arroz" in generated.text

        from sqlalchemy import select

        from app.db.session import SessionLocal
        from app.models import ShoppingList

        with SessionLocal() as db:
            shopping_list = db.scalar(
                select(ShoppingList).where(ShoppingList.name == "Mercado da semana")
            )
            assert shopping_list is not None
            list_id = shopping_list.public_id
            item_id = shopping_list.items[0].public_id

        added = client.post(
            f"/shopping-list/{list_id}/items",
            data={
                "description": "café",
                "quantity": "1",
                "unit": "pacote",
                "notes": "sem açúcar",
            },
            follow_redirects=False,
        )
        assert added.status_code == 303

        edited = client.post(
            f"/shopping-list/{list_id}/items/{item_id}/edit",
            data={"description": "arroz integral", "quantity": "3", "unit": "xícara"},
            follow_redirects=False,
        )
        assert edited.status_code == 303
        assert (
            client.post(
                f"/shopping-list/{list_id}/items/{item_id}/toggle",
                follow_redirects=False,
            ).status_code
            == 303
        )
        assert client.get(f"/shopping-list/{list_id}/text").status_code == 200
        assert (
            client.post(
                f"/shopping-list/{list_id}/items/{item_id}/delete",
                follow_redirects=False,
            ).status_code
            == 303
        )

        deleted = client.post(
            f"/shopping-list/{list_id}/delete", follow_redirects=False
        )
        assert deleted.status_code == 303
        assert client.get(f"/shopping-list?list_id={list_id}").status_code == 200

        with SessionLocal() as db:
            assert (
                db.scalar(select(ShoppingList).where(ShoppingList.public_id == list_id))
                is None
            )
