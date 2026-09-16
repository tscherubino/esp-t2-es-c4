"""Armazenamento local seguro de imagens originais."""

from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import settings


MAX_IMAGE_SIZE = 5 * 1024 * 1024
ALLOWED_CONTENT_TYPES = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}


async def save_image(upload: UploadFile) -> tuple[str, str, str]:
    """Valida e salva uma imagem, retornando nome interno, tipo e caminho relativo."""

    if upload.content_type not in ALLOWED_CONTENT_TYPES:
        raise ValueError("Envie uma imagem JPEG, PNG ou WebP.")

    content = await upload.read(MAX_IMAGE_SIZE + 1)
    return save_image_bytes(content, upload.content_type)


def save_image_bytes(content: bytes, content_type: str | None) -> tuple[str, str, str]:
    """Salva bytes de imagem já lidos, usando o mesmo limite e whitelist."""

    if content_type not in ALLOWED_CONTENT_TYPES:
        raise ValueError("Envie uma imagem JPEG, PNG ou WebP.")
    if len(content) > MAX_IMAGE_SIZE:
        raise ValueError("A imagem deve ter no máximo 5 MB.")

    stored_filename = f"{uuid4()}{ALLOWED_CONTENT_TYPES[content_type]}"
    target = settings.uploads_dir / stored_filename
    target.write_bytes(content)
    return stored_filename, content_type, f"uploads/{stored_filename}"


def delete_image(stored_filename: str) -> None:
    """Remove apenas um arquivo previamente armazenado no diretório de uploads."""

    target = (settings.uploads_dir / Path(stored_filename).name).resolve()
    uploads_root = settings.uploads_dir.resolve()
    if target.parent == uploads_root and target.exists():
        target.unlink()
