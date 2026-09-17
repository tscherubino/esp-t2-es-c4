"""Consultas e operações de persistência de receitas."""

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Recipe, RecipeTag, User


def list_recipes(db: Session, user: User) -> list[Recipe]:
    statement = (
        select(Recipe)
        .where(Recipe.user_id == user.id)
        .options(
            selectinload(Recipe.images),
            selectinload(Recipe.ingredients),
            selectinload(Recipe.preparation_steps),
        )
        .order_by(Recipe.updated_at.desc())
    )
    return list(db.scalars(statement).unique().all())


def get_recipe(db: Session, public_id: str, user: User) -> Recipe | None:
    statement = (
        select(Recipe)
        .where(Recipe.public_id == public_id, Recipe.user_id == user.id)
        .options(
            selectinload(Recipe.images),
            selectinload(Recipe.ingredients),
            selectinload(Recipe.preparation_steps),
            selectinload(Recipe.recipe_tags).selectinload(RecipeTag.tag),
        )
    )
    return db.scalars(statement).unique().first()


def get_demo_user(db: Session) -> User:
    user = db.scalar(select(User).where(User.name == "Usuário demo"))
    if user is None:
        user = User(name="Usuário demo")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user
