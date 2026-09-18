"""Caso de uso da importação assistida com providers exclusivamente locais."""

import json
import logging

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import ImportJob, RecipeImage, User
from app.models.entities import Recipe
from app.processors import (
    ManualTranscriptionOCRProvider,
    MockLLMRecipeParser,
    MockOCRProvider,
    RuleBasedRecipeParser,
)
from app.schemas.imports import ImportReviewInput, StructuredRecipe
from app.services.recipe_service import RecipeInput, create_recipe
from app.services.storage import MAX_IMAGE_SIZE, delete_image, save_image_bytes

logger = logging.getLogger(__name__)


def build_ocr_provider():
    """Seleciona o provider de OCR local conforme a configuração do ambiente."""
    if settings.import_ocr_provider == "manual":
        return ManualTranscriptionOCRProvider()
    return MockOCRProvider()


def build_recipe_parser():
    """Seleciona o parser local conforme a configuração do ambiente."""
    if settings.import_parser == "mock_llm":
        return MockLLMRecipeParser()
    return RuleBasedRecipeParser()


class RecipeImportService:
    """Analisa fontes, registra o job e finaliza somente após revisão."""

    def __init__(self, ocr_provider=None, recipe_parser=None):
        """Inicializa o serviço com providers informados ou com os padrões locais."""
        self.ocr_provider = ocr_provider or build_ocr_provider()
        self.recipe_parser = recipe_parser or build_recipe_parser()

    async def analyze(
        self,
        db: Session,
        user: User,
        original_text: str | None,
        image: UploadFile | None,
        manual_transcription: str | None = None,
    ) -> tuple[ImportJob, StructuredRecipe, str]:
        """Analisa texto ou imagem, persiste o job e retorna a sugestão para revisão."""
        source_text = (
            original_text.strip() if original_text and original_text.strip() else None
        )
        job = ImportJob(
            user_id=user.id,
            source_type="text",
            status="processing",
            original_text=source_text,
        )
        db.add(job)
        db.commit()
        db.refresh(job)

        try:
            if image is not None and image.filename:
                image_bytes = await image.read(MAX_IMAGE_SIZE + 1)
                stored_filename, content_type, relative_path = save_image_bytes(
                    image_bytes, image.content_type
                )
                job.source_type = "text_and_image" if source_text else "image"
                job.image_original_filename = image.filename
                job.image_stored_filename = stored_filename
                job.image_content_type = content_type
                job.image_relative_path = relative_path
                if not source_text:
                    source_text = self.ocr_provider.extract_text(
                        image_bytes, manual_transcription
                    )
            elif not source_text:
                raise ValueError("Informe um texto ou selecione uma imagem.")

            extracted_text = source_text or ""
            structured = self.recipe_parser.parse(extracted_text)
            job.extracted_text = extracted_text
            job.structured_payload = structured.model_dump_json()
            job.status = "completed"
            db.commit()
            return job, structured, extracted_text
        except Exception as error:
            if job.image_stored_filename:
                delete_image(job.image_stored_filename)
                job.image_stored_filename = None
                job.image_relative_path = None
            logger.warning(
                "Falha na importação local: status=failed source_type=%s error_type=%s",
                job.source_type,
                type(error).__name__,
            )
            job.status = "failed"
            job.error_message = str(error)
            db.commit()
            raise ValueError(
                f"Não foi possível analisar a importação: {error}"
            ) from error

    def get_job(self, db: Session, public_id: str, user: User) -> ImportJob | None:
        """Busca um job de importação pertencente ao usuário informado."""
        return db.scalar(
            select(ImportJob).where(
                ImportJob.public_id == public_id, ImportJob.user_id == user.id
            )
        )

    def finalize(
        self,
        db: Session,
        job: ImportJob,
        user: User,
        review: ImportReviewInput,
    ) -> Recipe:
        """Finaliza uma importação revisada e cria a receita definitiva."""
        if job.status != "completed" or not job.structured_payload:
            raise ValueError("Esta importação não está pronta para revisão.")

        original_text = job.original_text or job.extracted_text
        servings = review.servings
        if servings is None:
            structured = StructuredRecipe.model_validate(
                json.loads(job.structured_payload)
            )
            servings = (
                int(structured.servings)
                if structured.servings and structured.servings.isdigit()
                else None
            )
        recipe = create_recipe(
            db,
            user,
            RecipeInput(
                title=review.title,
                servings=servings,
                prep_time_minutes=review.prep_time_minutes,
                original_text=original_text,
                origin_story=review.origin_story,
                ingredient_descriptions=review.ingredient_names,
                ingredient_quantities=review.ingredient_quantities,
                ingredient_units=review.ingredient_units,
                step_instructions=review.preparation_steps,
                tags=review.tags,
            ),
        )
        if job.image_stored_filename:
            recipe.images.append(
                RecipeImage(
                    original_filename=job.image_original_filename
                    or job.image_stored_filename,
                    stored_filename=job.image_stored_filename,
                    content_type=job.image_content_type or "application/octet-stream",
                    relative_path=job.image_relative_path or "",
                )
            )
        job.recipe_id = recipe.id
        job.status = "completed"
        db.commit()
        return recipe


__all__ = ["RecipeImportService"]
