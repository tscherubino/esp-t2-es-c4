"""Entidades SQLAlchemy do modelo inicial do MVP."""

from datetime import UTC, datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def new_public_id() -> str:
    """Gera o UUID textual exposto pela aplicação."""

    return str(uuid4())


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False
    )


class PublicIdMixin:
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    public_id: Mapped[str] = mapped_column(
        String(36), unique=True, index=True, default=new_public_id, nullable=False
    )


class User(PublicIdMixin, TimestampMixin, Base):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(120), nullable=False)

    recipes: Mapped[list["Recipe"]] = relationship(back_populates="user")
    tags: Mapped[list["Tag"]] = relationship(back_populates="user")
    shopping_lists: Mapped[list["ShoppingList"]] = relationship(back_populates="user")
    import_jobs: Mapped[list["ImportJob"]] = relationship(back_populates="user")


class Recipe(PublicIdMixin, TimestampMixin, Base):
    __tablename__ = "recipes"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    servings: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    prep_time_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    original_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    origin_story: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship(back_populates="recipes")
    images: Mapped[list["RecipeImage"]] = relationship(
        back_populates="recipe", cascade="all, delete-orphan"
    )
    ingredients: Mapped[list["Ingredient"]] = relationship(
        back_populates="recipe", cascade="all, delete-orphan", order_by="Ingredient.position"
    )
    preparation_steps: Mapped[list["PreparationStep"]] = relationship(
        back_populates="recipe", cascade="all, delete-orphan", order_by="PreparationStep.position"
    )
    recipe_tags: Mapped[list["RecipeTag"]] = relationship(
        back_populates="recipe", cascade="all, delete-orphan"
    )
    import_jobs: Mapped[list["ImportJob"]] = relationship(back_populates="recipe")
    shopping_list_items: Mapped[list["ShoppingListItem"]] = relationship(back_populates="recipe")


class RecipeImage(PublicIdMixin, TimestampMixin, Base):
    __tablename__ = "recipe_images"

    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"), nullable=False, index=True)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    relative_path: Mapped[str] = mapped_column(String(500), nullable=False)

    recipe: Mapped["Recipe"] = relationship(back_populates="images")


class Ingredient(PublicIdMixin, TimestampMixin, Base):
    __tablename__ = "ingredients"

    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"), nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    unit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    recipe: Mapped["Recipe"] = relationship(back_populates="ingredients")


class PreparationStep(PublicIdMixin, TimestampMixin, Base):
    __tablename__ = "preparation_steps"

    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"), nullable=False, index=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    instruction: Mapped[str] = mapped_column(Text, nullable=False)

    recipe: Mapped["Recipe"] = relationship(back_populates="preparation_steps")


class Tag(PublicIdMixin, TimestampMixin, Base):
    __tablename__ = "tags"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)

    user: Mapped["User"] = relationship(back_populates="tags")
    recipe_tags: Mapped[list["RecipeTag"]] = relationship(
        back_populates="tag", cascade="all, delete-orphan"
    )

    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_tag_user_name"),)


class RecipeTag(PublicIdMixin, TimestampMixin, Base):
    __tablename__ = "recipe_tags"

    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"), nullable=False, index=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id"), nullable=False, index=True)

    recipe: Mapped["Recipe"] = relationship(back_populates="recipe_tags")
    tag: Mapped["Tag"] = relationship(back_populates="recipe_tags")

    __table_args__ = (UniqueConstraint("recipe_id", "tag_id", name="uq_recipe_tag"),)


class ShoppingList(PublicIdMixin, TimestampMixin, Base):
    __tablename__ = "shopping_lists"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)

    user: Mapped["User"] = relationship(back_populates="shopping_lists")
    items: Mapped[list["ShoppingListItem"]] = relationship(
        back_populates="shopping_list", cascade="all, delete-orphan"
    )


class ShoppingListItem(PublicIdMixin, TimestampMixin, Base):
    __tablename__ = "shopping_list_items"

    shopping_list_id: Mapped[int] = mapped_column(
        ForeignKey("shopping_lists.id"), nullable=False, index=True
    )
    recipe_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("recipes.id"), nullable=True, index=True
    )
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    unit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_checked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    shopping_list: Mapped["ShoppingList"] = relationship(back_populates="items")
    recipe: Mapped[Optional["Recipe"]] = relationship(back_populates="shopping_list_items")


class ImportJob(PublicIdMixin, TimestampMixin, Base):
    __tablename__ = "import_jobs"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    recipe_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("recipes.id"), nullable=True, index=True
    )
    source_type: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending", index=True)
    original_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    extracted_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image_original_filename: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    image_stored_filename: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    image_content_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    image_relative_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    structured_payload: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship(back_populates="import_jobs")
    recipe: Mapped[Optional["Recipe"]] = relationship(back_populates="import_jobs")

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'processing', 'completed', 'failed')",
            name="ck_import_job_status",
        ),
    )
