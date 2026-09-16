"""Schemas Pydantic v2 correspondentes às entidades do MVP."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class SchemaBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class TimestampSchema(SchemaBase):
    public_id: str
    created_at: datetime
    updated_at: datetime


class UserCreate(SchemaBase):
    name: str = Field(min_length=1, max_length=120)


class UserUpdate(SchemaBase):
    name: Optional[str] = Field(default=None, min_length=1, max_length=120)


class UserRead(TimestampSchema):
    name: str


class RecipeCreate(SchemaBase):
    title: str = Field(min_length=1, max_length=200)
    servings: Optional[int] = Field(default=None, ge=1)
    prep_time_minutes: Optional[int] = Field(default=None, ge=0)
    original_text: Optional[str] = None
    origin_story: Optional[str] = None
    user_public_id: str


class RecipeUpdate(SchemaBase):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    servings: Optional[int] = Field(default=None, ge=1)
    prep_time_minutes: Optional[int] = Field(default=None, ge=0)
    original_text: Optional[str] = None
    origin_story: Optional[str] = None


class RecipeManualInput(SchemaBase):
    """Entrada já validada para criação/edição pelo formulário manual."""

    title: str = Field(min_length=1, max_length=200)
    servings: Optional[int] = Field(default=None, ge=1)
    prep_time_minutes: Optional[int] = Field(default=None, ge=0)
    original_text: Optional[str] = None
    origin_story: Optional[str] = None
    ingredient_descriptions: list[str] = Field(default_factory=list)
    ingredient_quantities: list[str] = Field(default_factory=list)
    ingredient_units: list[str] = Field(default_factory=list)
    step_instructions: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class RecipeRead(TimestampSchema):
    title: str
    servings: Optional[int]
    prep_time_minutes: Optional[int]
    original_text: Optional[str]
    origin_story: Optional[str]
    user_id: int


class RecipeImageCreate(SchemaBase):
    original_filename: str = Field(min_length=1, max_length=255)
    stored_filename: str = Field(min_length=1, max_length=255)
    content_type: str = Field(min_length=1, max_length=100)
    relative_path: str = Field(min_length=1, max_length=500)


class RecipeImageRead(TimestampSchema):
    recipe_id: int
    original_filename: str
    stored_filename: str
    content_type: str
    relative_path: str


class IngredientCreate(SchemaBase):
    description: str = Field(min_length=1, max_length=255)
    quantity: Optional[str] = Field(default=None, max_length=50)
    unit: Optional[str] = Field(default=None, max_length=50)
    notes: Optional[str] = Field(default=None, max_length=255)
    position: int = Field(default=0, ge=0)


class IngredientUpdate(SchemaBase):
    description: Optional[str] = Field(default=None, min_length=1, max_length=255)
    quantity: Optional[str] = Field(default=None, max_length=50)
    unit: Optional[str] = Field(default=None, max_length=50)
    notes: Optional[str] = Field(default=None, max_length=255)
    position: Optional[int] = Field(default=None, ge=0)


class IngredientRead(TimestampSchema):
    recipe_id: int
    description: str
    quantity: Optional[str]
    unit: Optional[str]
    notes: Optional[str]
    position: int


class PreparationStepCreate(SchemaBase):
    position: int = Field(ge=0)
    instruction: str = Field(min_length=1)


class PreparationStepUpdate(SchemaBase):
    position: Optional[int] = Field(default=None, ge=0)
    instruction: Optional[str] = Field(default=None, min_length=1)


class PreparationStepRead(TimestampSchema):
    recipe_id: int
    position: int
    instruction: str


class TagCreate(SchemaBase):
    name: str = Field(min_length=1, max_length=80)
    user_public_id: str


class TagUpdate(SchemaBase):
    name: Optional[str] = Field(default=None, min_length=1, max_length=80)


class TagRead(TimestampSchema):
    user_id: int
    name: str


class RecipeTagCreate(SchemaBase):
    recipe_id: int
    tag_id: int


class RecipeTagRead(TimestampSchema):
    recipe_id: int
    tag_id: int


class ShoppingListCreate(SchemaBase):
    name: str = Field(min_length=1, max_length=150)
    user_public_id: str


class ShoppingListUpdate(SchemaBase):
    name: Optional[str] = Field(default=None, min_length=1, max_length=150)


class ShoppingListRead(TimestampSchema):
    user_id: int
    name: str


class ShoppingListItemCreate(SchemaBase):
    description: str = Field(min_length=1, max_length=255)
    quantity: Optional[str] = Field(default=None, max_length=50)
    unit: Optional[str] = Field(default=None, max_length=50)
    recipe_id: Optional[int] = None
    is_checked: bool = False


class ShoppingListItemUpdate(SchemaBase):
    description: Optional[str] = Field(default=None, min_length=1, max_length=255)
    quantity: Optional[str] = Field(default=None, max_length=50)
    unit: Optional[str] = Field(default=None, max_length=50)
    recipe_id: Optional[int] = None
    is_checked: Optional[bool] = None


class ShoppingListItemRead(TimestampSchema):
    shopping_list_id: int
    recipe_id: Optional[int]
    description: str
    quantity: Optional[str]
    unit: Optional[str]
    is_checked: bool


class ImportJobCreate(SchemaBase):
    source_type: str = Field(min_length=1, max_length=30)
    user_public_id: str
    recipe_id: Optional[int] = None
    original_text: Optional[str] = None


class ImportJobUpdate(SchemaBase):
    status: Optional[str] = Field(default=None, pattern="^(pending|processing|completed|failed)$")
    recipe_id: Optional[int] = None
    error_message: Optional[str] = None


class ImportJobRead(TimestampSchema):
    user_id: int
    recipe_id: Optional[int]
    source_type: str
    status: str
    original_text: Optional[str]
    error_message: Optional[str]
