"""Fixtures compartilhadas para manter a suíte isolada do ambiente local."""

import os
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

_temporary_root = TemporaryDirectory(prefix="livro-vivo-testes-")
_test_root = Path(_temporary_root.name)
os.environ["DATABASE_URL"] = f"sqlite:///{(_test_root / 'app.db').as_posix()}"
os.environ["UPLOADS_DIR"] = str(_test_root / "uploads")


@pytest.fixture(scope="session", autouse=True)
def isolated_local_environment():
    """Inicializa banco e uploads temporários para todos os testes."""

    from app.db.session import engine, initialize_database

    initialize_database()
    yield {"database": _test_root / "app.db", "uploads": _test_root / "uploads"}
    engine.dispose()
    _temporary_root.cleanup()


@pytest.fixture
def tmp_path(request: pytest.FixtureRequest):
    """Fornece diretório temporário isolado sem depender do plugin tmpdir."""
    with TemporaryDirectory(
        prefix=f"{request.node.name}-", dir=_test_root
    ) as directory:
        yield Path(directory)
