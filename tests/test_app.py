from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_home_page_is_available() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "Livro Vivo de Receitas" in response.text


def test_health_check_is_available() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_shopping_list_page_is_available() -> None:
    response = client.get("/shopping-list")

    assert response.status_code == 200
    assert "Lista de compras" in response.text
    assert "Gerar uma nova lista" in response.text
