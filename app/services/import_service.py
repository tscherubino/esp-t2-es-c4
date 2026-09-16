"""Infraestrutura inicial para importação, sem IA/OCR real."""

from typing import Optional

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models import ImportJob, Recipe, RecipeImage, User
from app.services.storage import save_image


async def create_pending_import(
    db: Session,
    user: User,
    original_text: Optional[str],
    image: Optional[UploadFile],
) -> Recipe:
    """Preserva as fontes e cria uma receita aguardando processamento futuro."""

    clean_text = original_text.strip() if original_text and original_text.strip() else None
    filename = image.filename if image and image.filename else None
    title = (clean_text.splitlines()[0].strip() if clean_text else None) or filename or "Receita importada"
    recipe = Recipe(user_id=user.id, title=title[:200], original_text=clean_text)
    db.add(recipe)
    db.flush()

    if image is not None and image.filename:
        stored_filename, content_type, relative_path = await save_image(image)
        recipe.images.append(
            RecipeImage(
                original_filename=image.filename,
                stored_filename=stored_filename,
                content_type=content_type,
                relative_path=relative_path,
            )
        )

    source_type = "text" if clean_text else "image"
    if clean_text and image is not None and image.filename:
        source_type = "text_and_image"
    db.add(
        ImportJob(
            user_id=user.id,
            recipe=recipe,
            source_type=source_type,
            status="pending",
            original_text=clean_text,
        )
    )
    db.commit()
    return recipe
