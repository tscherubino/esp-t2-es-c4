import pytest

from app.services.storage import MAX_IMAGE_SIZE, delete_image, save_image_bytes


PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"0" * 32


def test_storage_accepts_valid_png_and_uses_generated_name(tmp_path, monkeypatch) -> None:
    from app.core.config import settings

    monkeypatch.setattr(settings, "uploads_dir", tmp_path)

    stored_filename, content_type, relative_path = save_image_bytes(PNG_BYTES, "image/png")

    assert content_type == "image/png"
    assert stored_filename.endswith(".png")
    assert relative_path == f"uploads/{stored_filename}"
    assert (tmp_path / stored_filename).read_bytes() == PNG_BYTES


@pytest.mark.parametrize(
    ("content", "content_type", "message"),
    [
        (b"MZ-executavel", "image/png", "conteúdo"),
        (PNG_BYTES, "application/octet-stream", "JPEG"),
        (PNG_BYTES[:8], "image/png", "conteúdo"),
    ],
)
def test_storage_rejects_invalid_uploads(content: bytes, content_type: str, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        save_image_bytes(content, content_type)


def test_storage_rejects_files_over_five_mb() -> None:
    oversized = PNG_BYTES + b"0" * (MAX_IMAGE_SIZE - len(PNG_BYTES) + 1)

    with pytest.raises(ValueError, match="5 MB"):
        save_image_bytes(oversized, "image/png")


def test_delete_image_does_not_follow_path_components(tmp_path, monkeypatch) -> None:
    from app.core.config import settings

    monkeypatch.setattr(settings, "uploads_dir", tmp_path)
    outside = tmp_path.parent / "not-an-upload.txt"
    outside.write_text("não remover", encoding="utf-8")

    delete_image(f"..\\{outside.name}")

    assert outside.exists()
