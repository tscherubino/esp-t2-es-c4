"""Schemas Pydantic v2 correspondentes às entidades do MVP."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SchemaBase(BaseModel):
    """Base Pydantic com suporte a leitura a partir de entidades ORM."""

    model_config = ConfigDict(from_attributes=True)


class TimestampSchema(SchemaBase):
    """Campos públicos comuns de auditoria temporal."""

    public_id: str
    created_at: datetime
    updated_at: datetime


class UserCreate(SchemaBase):
    """Entrada para criação de usuário."""

    name: str = Field(min_length=1, max_length=120)


class UserUpdate(SchemaBase):
    """Entrada parcial para atualização de usuário."""

    name: str | None = Field(default=None, min_length=1, max_length=120)


class UserRead(TimestampSchema):
    """Representação de leitura de usuário."""

    name: str


class RecipeCreate(SchemaBase):
    """Entrada de API para criação de receita."""

    title: str = Field(min_length=1, max_length=200)
    servings: int | None = Field(default=None, ge=1)
    prep_time_minutes: int | None = Field(default=None, ge=0)
    original_text: str | None = None
    origin_story: str | None = None
    user_public_id: str


class RecipeUpdate(SchemaBase):
    """Entrada de API para atualização parcial de receita."""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    servings: int | None = Field(default=None, ge=1)
    prep_time_minutes: int | None = Field(default=None, ge=0)
    original_text: str | None = None
    origin_story: str | None = None


class RecipeManualInput(SchemaBase):
    """Entrada já validada para criação/edição pelo formulário manual."""

    title: str = Field(min_length=1, max_length=200)
    servings: int | None = Field(default=None, ge=1)
    prep_time_minutes: int | None = Field(default=None, ge=0)
    original_text: str | None = None
    origin_story: str | None = None
    ingredient_descriptions: list[str] = Field(default_factory=list)
    ingredient_quantities: list[str] = Field(default_factory=list)
    ingredient_units: list[str] = Field(default_factory=list)
    step_instructions: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class RecipeRead(TimestampSchema):
    """Representação de leitura de receita."""

    title: str
    servings: int | None
    prep_time_minutes: int | None
    original_text: str | None
    origin_story: str | None
    user_id: int


class RecipeImageCreate(SchemaBase):
    """Metadados necessários para registrar uma imagem de receita."""

    original_filename: str = Field(min_length=1, max_length=255)
    stored_filename: str = Field(min_length=1, max_length=255)
    content_type: str = Field(min_length=1, max_length=100)
    relative_path: str = Field(min_length=1, max_length=500)


class RecipeImageRead(TimestampSchema):
    """Representação de leitura de imagem de receita."""

    recipe_id: int
    original_filename: str
    stored_filename: str
    content_type: str
    relative_path: str


class IngredientCreate(SchemaBase):
    """Entrada para criação de ingrediente."""

    description: str = Field(min_length=1, max_length=255)
    quantity: str | None = Field(default=None, max_length=50)
    unit: str | None = Field(default=None, max_length=50)
    notes: str | None = Field(default=None, max_length=255)
    position: int = Field(default=0, ge=0)


class IngredientUpdate(SchemaBase):
    """Entrada parcial para atualização de ingrediente."""

    description: str | None = Field(default=None, min_length=1, max_length=255)
    quantity: str | None = Field(default=None, max_length=50)
    unit: str | None = Field(default=None, max_length=50)
    notes: str | None = Field(default=None, max_length=255)
    position: int | None = Field(default=None, ge=0)


class IngredientRead(TimestampSchema):
    """Representação de leitura de ingrediente."""

    recipe_id: int
    description: str
    quantity: str | None
    unit: str | None
    notes: str | None
    position: int


class PreparationStepCreate(SchemaBase):
    """Entrada para criação de uma etapa de preparo."""

    position: int = Field(ge=0)
    instruction: str = Field(min_length=1)


class PreparationStepUpdate(SchemaBase):
    """Entrada parcial para atualização de uma etapa."""

    position: int | None = Field(default=None, ge=0)
    instruction: str | None = Field(default=None, min_length=1)


class PreparationStepRead(TimestampSchema):
    """Representação de leitura de etapa de preparo."""

    recipe_id: int
    position: int
    instruction: str


class TagCreate(SchemaBase):
    """Entrada para criação de tag."""

    name: str = Field(min_length=1, max_length=80)
    user_public_id: str


class TagUpdate(SchemaBase):
    """Entrada parcial para atualização de tag."""

    name: str | None = Field(default=None, min_length=1, max_length=80)


class TagRead(TimestampSchema):
    """Representação de leitura de tag."""

    user_id: int
    name: str


class RecipeTagCreate(SchemaBase):
    """Entrada para vincular uma tag a uma receita."""

    recipe_id: int
    tag_id: int


class RecipeTagRead(TimestampSchema):
    """Representação de leitura do vínculo entre receita e tag."""

    recipe_id: int
    tag_id: int


class ShoppingListCreate(SchemaBase):
    """Entrada para criação de lista de compras."""

    name: str = Field(min_length=1, max_length=150)
    user_public_id: str


class ShoppingListUpdate(SchemaBase):
    """Entrada parcial para atualização de lista de compras."""

    name: str | None = Field(default=None, min_length=1, max_length=150)


class ShoppingListRead(TimestampSchema):
    """Representação de leitura de lista de compras."""

    user_id: int
    name: str


class ShoppingListItemCreate(SchemaBase):
    """Entrada para criação de item de compras."""

    description: str = Field(min_length=1, max_length=255)
    quantity: str | None = Field(default=None, max_length=50)
    unit: str | None = Field(default=None, max_length=50)
    notes: str | None = Field(default=None, max_length=255)
    recipe_id: int | None = None
    is_checked: bool = False


class ShoppingListItemUpdate(SchemaBase):
    """Entrada parcial para atualização de item de compras."""

    description: str | None = Field(default=None, min_length=1, max_length=255)
    quantity: str | None = Field(default=None, max_length=50)
    unit: str | None = Field(default=None, max_length=50)
    notes: str | None = Field(default=None, max_length=255)
    recipe_id: int | None = None
    is_checked: bool | None = None


class ShoppingListItemRead(TimestampSchema):
    """Representação de leitura de item de compras."""

    shopping_list_id: int
    recipe_id: int | None
    description: str
    quantity: str | None
    unit: str | None
    notes: str | None
    is_checked: bool


class ImportJobCreate(SchemaBase):
    """Entrada para criação de job de importação."""

    source_type: str = Field(min_length=1, max_length=30)
    user_public_id: str
    recipe_id: int | None = None
    original_text: str | None = None


class ImportJobUpdate(SchemaBase):
    """Entrada parcial para atualização de job de importação."""

    status: str | None = Field(
        default=None, pattern="^(pending|processing|completed|failed)$"
    )
    recipe_id: int | None = None
    error_message: str | None = None


class ImportJobRead(TimestampSchema):
    """Representação de leitura de job de importação."""

    user_id: int
    recipe_id: int | None
    source_type: str
    status: str
    original_text: str | None
    extracted_text: str | None
    structured_payload: str | None
    error_message: str | None
