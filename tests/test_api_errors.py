"""Testes de contrato HTTP, erros e payloads inválidos dos endpoints principais."""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_recipe_endpoints_return_404_for_unknown_resources() -> None:
    """Garante 404 para detalhes, edição, exclusão, imagem e API de receita inexistente."""
    assert client.get("/recipes/unknown-recipe").status_code == 404
    assert client.get("/recipes/unknown-recipe/edit").status_code == 404
    assert client.post("/recipes/unknown-recipe/delete", follow_redirects=False).status_code == 404
    assert client.get("/recipes/unknown-recipe/images/unknown-image").status_code == 404
    assert client.get("/api/recipes/unknown-recipe").status_code == 404


def test_import_and_shopping_endpoints_return_404_for_unknown_resources() -> None:
    """Garante 404 para jobs e listas de compras inexistentes."""
    assert client.get("/recipes/import/unknown-job/review").status_code == 404
    assert client.post("/recipes/import/unknown-job/review", data={"title": "Teste"}).status_code == 404
    assert client.get("/shopping-list/unknown-list/text").status_code == 404
    assert client.post("/shopping-list/unknown-list/delete", follow_redirects=False).status_code == 404
    assert client.post("/shopping-list/unknown-list/items", data={"description": "Café"}).status_code == 404
    assert client.post(
        "/shopping-list/unknown-list/items/unknown-item/toggle", follow_redirects=False
    ).status_code == 404


def test_recipe_endpoints_reject_invalid_payloads() -> None:
    """Garante 422 para campos ausentes, vazios ou com tipo inválido."""
    assert client.post("/recipes", data={}).status_code == 422
    assert client.post("/recipes", data={"title": "", "servings": "2"}).status_code == 422
    assert client.post("/recipes", data={"title": "Teste", "servings": "não-numérico"}).status_code == 422


def test_import_and_shopping_endpoints_handle_invalid_payloads() -> None:
    """Garante respostas controladas para fontes ausentes e geração sem receitas."""
    import_response = client.post("/api/recipes/import/analyze", data={})
    assert import_response.status_code == 400
    assert "detail" in import_response.json()

    page_response = client.post("/shopping-list/generate", data={})
    assert page_response.status_code == 200
    assert "Selecione" in page_response.text

    unknown_recipe_response = client.post(
        "/shopping-list/generate", data={"recipe_ids": ["unknown-recipe"]}
    )
    assert unknown_recipe_response.status_code == 200
    assert "não foi encontrada" in unknown_recipe_response.text or "nÃ£o foi encontrada" in unknown_recipe_response.text


def test_api_recipe_endpoint_returns_stable_minimal_payload() -> None:
    """Verifica que a API retorna os campos principais para uma receita válida."""
    created = client.post(
        "/recipes",
        data={"title": "Receita API edge", "step_instructions": ["Teste"]},
        follow_redirects=False,
    )
    assert created.status_code == 303
    public_id = created.headers["location"].rsplit("/", 1)[-1]

    response = client.get(f"/api/recipes/{public_id}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["public_id"] == public_id
    assert payload["title"] == "Receita API edge"
    assert payload["ingredients"] == []
    assert payload["preparation_steps"] == ["Teste"]
    assert client.post(f"/recipes/{public_id}/delete", follow_redirects=False).status_code == 303
