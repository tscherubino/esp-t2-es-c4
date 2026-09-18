import asyncio
import io
import re

from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.processors import (
    ManualTranscriptionOCRProvider,
    MockLLMRecipeParser,
    MockOCRProvider,
    RuleBasedRecipeParser,
)
from app.repositories.recipe_repository import get_demo_user
from app.services.import_service import RecipeImportService

RECIPE_TEXT = """Bolo simples
Rende: 8 porções
Tempo: 40 minutos
Ingredientes:
2 xícaras de farinha
3 ovos
Modo de preparo:
Misture os ingredientes.
Asse até dourar."""

PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"0" * 32


def test_mock_ocr_returns_deterministic_text() -> None:
    text = MockOCRProvider().extract_text(b"not-an-image")

    assert "Ingredientes:" in text
    assert "Modo de preparo:" in text


def test_manual_transcription_provider_requires_transcription() -> None:
    provider = ManualTranscriptionOCRProvider()

    assert provider.extract_text(b"image", "  texto informado  ") == "texto informado"

    try:
        provider.extract_text(b"image")
    except ValueError as error:
        assert "transcrição manual" in str(error)
    else:
        raise AssertionError("A transcrição ausente deveria falhar")


def test_rule_based_parser_returns_valid_structured_recipe() -> None:
    result = RuleBasedRecipeParser().parse(RECIPE_TEXT)

    assert result.title == "Bolo simples"
    assert result.servings == "8"
    assert result.prep_time_minutes == 40
    assert [item.name for item in result.ingredients] == ["farinha", "ovos"]
    assert result.preparation_steps[0].step_number == 1
    assert all(0 <= item.confidence_score <= 1 for item in result.ingredients)


def test_mock_llm_parser_is_local_and_marks_warning() -> None:
    result = MockLLMRecipeParser().parse(RECIPE_TEXT)

    assert result.ingredients
    assert any("MockLLMRecipeParser" in warning for warning in result.warnings)


def test_import_service_analyzes_without_external_provider() -> None:
    db = SessionLocal()
    try:
        user = get_demo_user(db)
        job, structured, source_text = asyncio.run(
            RecipeImportService().analyze(db, user, RECIPE_TEXT, None)
        )

        assert job.status == "completed"
        assert source_text == RECIPE_TEXT
        assert structured.title == "Bolo simples"
        db.delete(job)
        db.commit()
    finally:
        db.close()


def test_image_import_with_manual_transcription_requires_review_before_save() -> None:
    with TestClient(app) as client:
        analyzed = client.post(
            "/recipes/import",
            data={"manual_transcription": RECIPE_TEXT},
            files={"image": ("receita.png", io.BytesIO(PNG_BYTES), "image/png")},
            follow_redirects=False,
        )
        assert analyzed.status_code == 303
        review_url = analyzed.headers["location"]
        assert "/review" in review_url
        review = client.get(review_url)
        assert review.status_code == 200
        assert "receita.png" in review.text
        assert "Bolo simples" in review.text

        job_id = review_url.split("/")[3]
        finalized = client.post(
            f"/recipes/import/{job_id}/review",
            data={
                "title": "Bolo de imagem revisado",
                "servings": "8",
                "prep_time_minutes": "40",
                "ingredient_names": ["farinha", "ovos"],
                "ingredient_quantities": ["2", "3"],
                "ingredient_units": ["xícaras", "unidades"],
                "preparation_steps": ["Misture", "Asse"],
                "tags": ["imagem"],
            },
            follow_redirects=False,
        )
        assert finalized.status_code == 303
        public_id = finalized.headers["location"].rsplit("/", 1)[-1]
        detail = client.get(f"/recipes/{public_id}")
        assert detail.status_code == 200
        assert "Bolo de imagem revisado" in detail.text
        image_match = re.search(r"/recipes/[^\"]+/images/([^\"]+)", detail.text)
        assert image_match is not None
        assert (
            client.get(
                f"/recipes/{public_id}/images/{image_match.group(1)}"
            ).status_code
            == 200
        )
        assert (
            client.post(
                f"/recipes/{public_id}/delete", follow_redirects=False
            ).status_code
            == 303
        )
