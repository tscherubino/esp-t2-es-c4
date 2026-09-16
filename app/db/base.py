"""Base declarativa do SQLAlchemy.

Os modelos de domínio serão adicionados em uma etapa posterior.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Classe base para os modelos ORM do projeto."""
