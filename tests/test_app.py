from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_home_page_is_available() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "Livro Vivo de Receitas" in response.text
    assert 'href="/">Página inicial' in response.text
    assert 'href="/recipes">Minhas receitas' in response.text


def test_home_and_recipe_list_handle_empty_catalog(monkeypatch) -> None:
    monkeypatch.setattr("app.main.list_recipes", lambda db, user: [])
    monkeypatch.setattr("app.routers.recipes.list_recipes", lambda db, user: [])

    home = client.get("/")
    recipe_list = client.get("/recipes")

    assert home.status_code == 200
    assert 'id="empty-recipes-heading"' in home.text
    assert 'id="recipes-carousel"' not in home.text
    assert recipe_list.status_code == 200
    assert "Nenhuma receita cadastrada ainda." in recipe_list.text


def test_health_check_is_available() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_home_page_shows_registered_recipe_in_carousel() -> None:
    created = client.post(
        "/recipes",
        data={"title": "Receita no carrossel", "step_instructions": ["Misture"]},
        follow_redirects=False,
    )
    assert created.status_code == 303

    response = client.get("/")

    assert response.status_code == 200
    assert 'id="recipes-carousel"' in response.text
    assert "Receita no carrossel" in response.text


def test_home_and_recipe_list_handle_recipe_without_image() -> None:
    created = client.post(
        "/recipes",
        data={"title": "Receita sem imagem", "step_instructions": ["Misture"]},
        follow_redirects=False,
    )
    assert created.status_code == 303
    public_id = created.headers["location"].rsplit("/", 1)[-1]

    home = client.get("/")
    recipe_list = client.get("/recipes")

    assert home.status_code == 200
    assert "Receita sem imagem" in home.text
    assert recipe_list.status_code == 200
    assert "Sem imagem" in recipe_list.text
    assert f"/recipes/{public_id}/images/" not in recipe_list.text


def test_shopping_list_page_is_available() -> None:
    response = client.get("/shopping-list")

    assert response.status_code == 200
    assert "Lista de compras" in response.text
    assert "Gerar uma nova lista" in response.text
