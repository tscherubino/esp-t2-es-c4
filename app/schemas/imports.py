"""Schemas Pydantic v2 para análise e revisão de importações."""

from pydantic import BaseModel, ConfigDict, Field


class IngredientSuggestion(BaseModel):
    """Sugestão estruturada de um ingrediente com confiança."""
    name: str = Field(min_length=1)
    quantity: str | None = None
    unit: str | None = None
    notes: str | None = None
    confidence_score: float = Field(ge=0, le=1)


class PreparationStepSuggestion(BaseModel):
    """Sugestão estruturada de uma etapa de preparo com confiança."""
    step_number: int = Field(ge=1)
    description: str = Field(min_length=1)
    confidence_score: float = Field(ge=0, le=1)


class StructuredRecipe(BaseModel):
    """Resultado editável da análise automática de uma receita."""
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=200)
    servings: str | None = None
    prep_time_minutes: int | None = Field(default=None, ge=0)
    ingredients: list[IngredientSuggestion] = Field(default_factory=list)
    preparation_steps: list[PreparationStepSuggestion] = Field(default_factory=list)
    suggested_tags: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class ImportAnalysisResponse(BaseModel):
    """Resposta da API para uma análise de importação pendente de revisão."""
    import_job_public_id: str
    source_text: str
    structured_recipe: StructuredRecipe
    status: str


class ImportReviewInput(BaseModel):
    """Dados revisados pelo usuário antes da criação da receita definitiva."""
    title: str = Field(min_length=1, max_length=200)
    servings: int | None = Field(default=None, ge=1)
    prep_time_minutes: int | None = Field(default=None, ge=0)
    origin_story: str | None = None
    ingredient_names: list[str] = Field(default_factory=list)
    ingredient_quantities: list[str] = Field(default_factory=list)
    ingredient_units: list[str] = Field(default_factory=list)
    preparation_steps: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
