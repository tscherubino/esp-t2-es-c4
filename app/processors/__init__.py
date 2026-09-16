"""Providers locais e contratos de processamento de importações."""

from app.processors.providers import (
    LLMRecipeParser,
    ManualTranscriptionOCRProvider,
    MockLLMRecipeParser,
    MockOCRProvider,
    OCRProvider,
    RuleBasedRecipeParser,
)

__all__ = [
    "LLMRecipeParser",
    "ManualTranscriptionOCRProvider",
    "MockLLMRecipeParser",
    "MockOCRProvider",
    "OCRProvider",
    "RuleBasedRecipeParser",
]
