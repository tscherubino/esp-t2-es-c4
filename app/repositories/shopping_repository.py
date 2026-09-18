"""Consultas de listas de compras do usuário demo."""

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import ShoppingList, ShoppingListItem, User


def list_shopping_lists(db: Session, user: User) -> list[ShoppingList]:
    """Lista compras do usuário, incluindo os itens e ordenando pelas mais recentes."""
    statement = (
        select(ShoppingList)
        .where(ShoppingList.user_id == user.id)
        .options(selectinload(ShoppingList.items))
        .order_by(ShoppingList.updated_at.desc())
    )
    return list(db.scalars(statement).unique().all())


def get_shopping_list(db: Session, public_id: str, user: User) -> ShoppingList | None:
    """Busca uma lista pelo identificador público com verificação de propriedade."""
    statement = (
        select(ShoppingList)
        .where(ShoppingList.public_id == public_id, ShoppingList.user_id == user.id)
        .options(selectinload(ShoppingList.items))
    )
    return db.scalars(statement).unique().first()


def get_shopping_item(
    db: Session, public_id: str, shopping_list: ShoppingList
) -> ShoppingListItem | None:
    """Busca um item somente entre os itens da lista já autorizada."""
    return next(
        (item for item in shopping_list.items if item.public_id == public_id), None
    )
