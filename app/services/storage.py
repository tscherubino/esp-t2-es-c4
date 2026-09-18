"""Armazenamento local seguro de imagens originais."""

from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import settings

MAX_IMAGE_SIZE = 5 * 1024 * 1024
ALLOWED_CONTENT_TYPES = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}


def _has_expected_signature(content: bytes, content_type: str) -> bool:
    """Confere a assinatura básica do conteúdo da imagem.

    Args:
        content: Bytes recebidos no upload.
        content_type: Tipo MIME informado para o arquivo.

    Returns:
        `True` quando a assinatura corresponde ao tipo MIME permitido.

    """
    signatures = {
        "image/jpeg": content.startswith(b"\xff\xd8\xff"),
        "image/png": len(content) >= 16 and content.startswith(b"\x89PNG\r\n\x1a\n"),
        "image/webp": len(content) >= 12 and content[:4] == b"RIFF" and content[8:12] == b"WEBP",
    }
    return signatures.get(content_type, False)


async def save_image(upload: UploadFile) -> tuple[str, str, str]:
    """Valida e salva uma imagem enviada pelo usuário.

    Args:
        upload: Arquivo recebido pelo endpoint de upload.

    Returns:
        Tupla com nome interno, tipo MIME e caminho relativo do arquivo.

    Raises:
        ValueError: Se o tipo, tamanho ou conteúdo do arquivo for inválido.

    """
    if upload.content_type not in ALLOWED_CONTENT_TYPES:
        raise ValueError("Envie uma imagem JPEG, PNG ou WebP.")

    content = await upload.read(MAX_IMAGE_SIZE + 1)
    return save_image_bytes(content, upload.content_type)


def save_image_bytes(content: bytes, content_type: str | None) -> tuple[str, str, str]:
    """Valida e salva bytes de imagem usando a whitelist local.

    Args:
        content: Conteúdo binário já lido do upload.
        content_type: Tipo MIME declarado para o conteúdo.

    Returns:
        Tupla com nome interno, tipo MIME e caminho relativo do arquivo.

    Raises:
        ValueError: Se o tipo, tamanho ou assinatura do conteúdo for inválido.

    """
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise ValueError("Envie uma imagem JPEG, PNG ou WebP.")
    if len(content) > MAX_IMAGE_SIZE:
        raise ValueError("A imagem deve ter no máximo 5 MB.")
    if not content or not _has_expected_signature(content, content_type):
        raise ValueError("O conteúdo enviado não corresponde a uma imagem válida.")

    settings.uploads_dir.mkdir(parents=True, exist_ok=True)
    stored_filename = f"{uuid4()}{ALLOWED_CONTENT_TYPES[content_type]}"
    target = settings.uploads_dir / stored_filename
    target.write_bytes(content)
    return stored_filename, content_type, f"uploads/{stored_filename}"


def delete_image(stored_filename: str) -> None:
    """Remove um arquivo armazenado sem sair do diretório de uploads.

    Args:
        stored_filename: Nome interno previamente gerado pelo serviço.

    """
    target = (settings.uploads_dir / Path(stored_filename).name).resolve()
    uploads_root = settings.uploads_dir.resolve()
    if target.parent == uploads_root and target.exists():
        target.unlink()
