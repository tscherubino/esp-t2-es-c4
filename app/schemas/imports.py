"""Schemas Pydantic v2 para análise e revisão de importações."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class IngredientSuggestion(BaseModel):
    name: str = Field(min_length=1)
    quantity: Optional[str] = None
    unit: Optional[str] = None
    notes: Optional[str] = None
    confidence_score: float = Field(ge=0, le=1)


class PreparationStepSuggestion(BaseModel):
    step_number: int = Field(ge=1)
    description: str = Field(min_length=1)
    confidence_score: float = Field(ge=0, le=1)


class StructuredRecipe(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=200)
    servings: Optional[str] = None
    prep_time_minutes: Optional[int] = Field(default=None, ge=0)
    ingredients: list[IngredientSuggestion] = Field(default_factory=list)
    preparation_steps: list[PreparationStepSuggestion] = Field(default_factory=list)
    suggested_tags: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class ImportAnalysisResponse(BaseModel):
    import_job_public_id: str
    source_text: str
    structured_recipe: StructuredRecipe
    status: str


class ImportReviewInput(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    servings: Optional[int] = Field(default=None, ge=1)
    prep_time_minutes: Optional[int] = Field(default=None, ge=0)
    origin_story: Optional[str] = None
    ingredient_names: list[str] = Field(default_factory=list)
    ingredient_quantities: list[str] = Field(default_factory=list)
    ingredient_units: list[str] = Field(default_factory=list)
    preparation_steps: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
