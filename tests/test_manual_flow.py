import io
import re

from fastapi.testclient import TestClient

from app.main import app


PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"0" * 32


def test_manual_recipe_flow_end_to_end() -> None:
    with TestClient(app) as client:
        assert client.get("/recipes").status_code == 200

        create_data = {
            "title": "Bolo de teste ponta a ponta",
            "servings": "8",
            "prep_time_minutes": "45",
            "origin_story": "Receita de família",
            "original_text": "Bolo original preservado",
            "ingredient_descriptions": ["farinha", "ovos", "", "", ""],
            "ingredient_quantities": ["2", "3", "", "", ""],
            "ingredient_units": ["xícaras", "unidades", "", "", ""],
            "step_instructions": ["Misture tudo", "Asse por 45 minutos", "", "", ""],
            "tags": ["família", "sobremesa"],
        }
        created = client.post(
            "/recipes",
            data=create_data,
            files={"image": ("bolo.png", io.BytesIO(PNG_BYTES), "image/png")},
            follow_redirects=False,
        )
        assert created.status_code == 303
        public_id = created.headers["location"].rsplit("/", 1)[-1]

        recipe_list = client.get("/recipes")
        assert recipe_list.status_code == 200
        assert f"/recipes/{public_id}/images/" in recipe_list.text

        detail = client.get(f"/recipes/{public_id}")
        assert detail.status_code == 200
        assert "Bolo de teste ponta a ponta" in detail.text
        assert "Receita de família" in detail.text
        assert "farinha" in detail.text
        assert "Misture tudo" in detail.text
        assert "sobremesa" in detail.text
        image_match = re.search(r"/recipes/[^\"]+/images/([^\"]+)", detail.text)
        assert image_match is not None
        assert client.get(f"/recipes/{public_id}/images/{image_match.group(1)}").status_code == 200
        assert client.get(f"/api/recipes/{public_id}").status_code == 200

        edited = client.post(
            f"/recipes/{public_id}/edit",
            data={
                **create_data,
                "title": "Bolo de teste editado",
                "servings": "10",
                "tags": ["família"],
            },
            follow_redirects=False,
        )
        assert edited.status_code == 303
        assert "Bolo de teste editado" in client.get(f"/recipes/{public_id}").text

        deleted = client.post(f"/recipes/{public_id}/delete", follow_redirects=False)
        assert deleted.status_code == 303
        assert client.get(f"/recipes/{public_id}").status_code == 404

        imported = client.post(
            "/recipes/import",
            data={"original_text": "Receita importada pendente"},
            follow_redirects=False,
        )
        assert imported.status_code == 303
        review_url = imported.headers["location"]
        assert review_url.startswith("/recipes/import/")
        review = client.get(review_url)
        assert review.status_code == 200
        assert "Revisar importação" in review.text
        job_id = review_url.split("/")[3]
        finalized = client.post(
            f"/recipes/import/{job_id}/review",
            data={
                "title": "Receita importada revisada",
                "servings": "4",
                "prep_time_minutes": "30",
                "origin_story": "Importada e revisada",
                "ingredient_names": ["arroz"],
                "ingredient_quantities": ["1"],
                "ingredient_units": ["xícara"],
                "preparation_steps": ["Cozinhe"],
                "tags": ["importada"],
            },
            follow_redirects=False,
        )
        assert finalized.status_code == 303
        imported_id = finalized.headers["location"].rsplit("/", 1)[-1]
        assert "Receita importada revisada" in client.get(f"/recipes/{imported_id}").text
        assert client.post(f"/recipes/{imported_id}/delete", follow_redirects=False).status_code == 303
