import io

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.db.session import SessionLocal
from app.main import app
from app.models import ImportJob, Recipe, ShoppingList, ShoppingListItem
from app.repositories.recipe_repository import get_demo_user


PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"0" * 32


def test_invalid_manual_upload_does_not_persist_recipe() -> None:
    title = "Receita não deve nascer com upload inválido"
    with TestClient(app) as client:
        response = client.post(
            "/recipes",
            data={"title": title},
            files={"image": ("programa.exe", io.BytesIO(b"MZ-executavel"), "image/png")},
        )

    assert response.status_code == 400
    with SessionLocal() as db:
        assert db.scalar(select(Recipe).where(Recipe.title == title)) is None


def test_import_upload_limit_returns_friendly_error() -> None:
    oversized = PNG_BYTES + b"0" * (5 * 1024 * 1024)

    with TestClient(app) as client:
        response = client.post(
            "/recipes/import",
            files={"image": ("grande.png", io.BytesIO(oversized), "image/png")},
        )

    assert response.status_code == 400
    assert "5 MB" in response.text


def test_import_without_source_returns_friendly_error() -> None:
    with TestClient(app) as client:
        response = client.post("/recipes/import", data={})

    assert response.status_code == 400
    assert "Informe um texto ou selecione uma imagem" in response.text


def test_delete_recipe_removes_image_import_job_and_recipe_reference(tmp_path, monkeypatch) -> None:
    from app.core.config import settings

    monkeypatch.setattr(settings, "uploads_dir", tmp_path)
    with TestClient(app) as client:
        created = client.post(
            "/recipes",
            data={"title": "Receita para exclusão completa", "original_text": "fonte"},
            files={"image": ("origem.png", io.BytesIO(PNG_BYTES), "image/png")},
            follow_redirects=False,
        )
        public_id = created.headers["location"].rsplit("/", 1)[-1]

        with SessionLocal() as db:
            user = get_demo_user(db)
            recipe = db.scalar(select(Recipe).where(Recipe.public_id == public_id))
            assert recipe is not None
            image_path = tmp_path / recipe.images[0].stored_filename
            shopping_list = ShoppingList(user_id=user.id, name="Lista vinculada")
            shopping_list.items.append(
                ShoppingListItem(recipe_id=recipe.id, description="item vinculado")
            )
            db.add_all([
                shopping_list,
                ImportJob(
                    user_id=user.id,
                    recipe_id=recipe.id,
                    source_type="text",
                    status="completed",
                    original_text="fonte importada",
                ),
            ])
            db.commit()

        deleted = client.post(f"/recipes/{public_id}/delete", follow_redirects=False)
        assert deleted.status_code == 303
        assert not image_path.exists()

        with SessionLocal() as db:
            assert db.scalar(select(Recipe).where(Recipe.public_id == public_id)) is None
            assert db.scalar(select(ImportJob).where(ImportJob.recipe_id.is_not(None))) is None
            item = db.scalar(select(ShoppingListItem).where(ShoppingListItem.description == "item vinculado"))
            assert item is not None
            assert item.recipe_id is None
