"""Contratos e implementações locais para OCR e estruturação de receitas."""

import re
from abc import ABC, abstractmethod

from app.schemas.imports import (
    IngredientSuggestion,
    PreparationStepSuggestion,
    StructuredRecipe,
)


class OCRProvider(ABC):
    """Contrato para transformar uma imagem em texto."""

    @abstractmethod
    def extract_text(self, image: bytes, manual_transcription: str | None = None) -> str:
        """Extrai texto de uma imagem, opcionalmente usando transcrição manual."""
        raise NotImplementedError


class MockOCRProvider(OCRProvider):
    """OCR determinístico local, sem leitura real da imagem."""

    def extract_text(self, image: bytes, manual_transcription: str | None = None) -> str:
        """Retorna a transcrição manual ou um texto determinístico de demonstração."""
        if manual_transcription and manual_transcription.strip():
            return manual_transcription.strip()
        return (
            "Receita importada da imagem\n"
            "Ingredientes:\n"
            "2 xícaras de farinha\n"
            "3 ovos\n"
            "Modo de preparo:\n"
            "Misture os ingredientes.\n"
            "Asse até dourar."
        )


class ManualTranscriptionOCRProvider(OCRProvider):
    """Provider que usa exclusivamente a transcrição fornecida pelo usuário."""

    def extract_text(self, image: bytes, manual_transcription: str | None = None) -> str:
        """Valida e devolve a transcrição fornecida pelo usuário."""
        if not manual_transcription or not manual_transcription.strip():
            raise ValueError("Informe uma transcrição manual para a imagem.")
        return manual_transcription.strip()


class LLMRecipeParser(ABC):
    """Contrato para estruturar texto em dados editáveis de receita."""

    @abstractmethod
    def parse(self, text: str) -> StructuredRecipe:
        """Converta texto bruto em uma sugestão estruturada de receita."""
        raise NotImplementedError


def _confidence(value: float) -> float:
    """Limita uma confiança ao intervalo de zero a um com duas casas decimais."""
    return max(0.0, min(1.0, round(value, 2)))


class RuleBasedRecipeParser(LLMRecipeParser):
    """Parser local simples por seções e padrões de texto."""

    def parse(self, text: str) -> StructuredRecipe:
        """Identifica título, metadados, ingredientes e etapas por regras locais."""
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if not lines:
            raise ValueError("Não foi possível estruturar um texto vazio.")

        title = lines[0][:200]
        servings = None
        prep_time = None
        servings_match = re.search(r"(?:rende|porções?|serve)\s*[:\-]?\s*(\d+)", text, re.IGNORECASE)
        time_match = re.search(r"(?:tempo|preparo)\s*[:\-]?\s*(\d+)\s*(?:min|minutos)?", text, re.IGNORECASE)
        if servings_match:
            servings = servings_match.group(1)
        if time_match:
            prep_time = int(time_match.group(1))

        ingredient_lines, step_lines = self._split_sections(lines)
        ingredients = [self._ingredient(line) for line in ingredient_lines]
        steps = [
            PreparationStepSuggestion(
                step_number=index,
                description=line,
                confidence_score=_confidence(0.88),
            )
            for index, line in enumerate(step_lines, start=1)
        ]
        warnings = ["Revise os campos estruturados antes de salvar a receita."]
        if not ingredients:
            warnings.append("Nenhum ingrediente foi identificado automaticamente.")
        if not steps:
            warnings.append("Nenhuma etapa de preparo foi identificada automaticamente.")
        return StructuredRecipe(
            title=title,
            servings=servings,
            prep_time_minutes=prep_time,
            ingredients=ingredients,
            preparation_steps=steps,
            suggested_tags=[],
            warnings=warnings,
        )

    @staticmethod
    def _split_sections(lines: list[str]) -> tuple[list[str], list[str]]:
        """Separa linhas de ingredientes e preparo conforme os cabeçalhos encontrados."""
        ingredients: list[str] = []
        steps: list[str] = []
        section = "ingredients"
        for line in lines[1:]:
            normalized = line.casefold().rstrip(":")
            if normalized in {"ingredientes", "ingredient"}:
                section = "ingredients"
                continue
            if normalized in {"modo de preparo", "preparo", "instruções", "instrucoes"}:
                section = "steps"
                continue
            if re.match(r"^(rende|porções?|serve|tempo|preparo)\s*[:\-]", line, re.IGNORECASE):
                continue
            (ingredients if section == "ingredients" else steps).append(line)
        return ingredients, steps

    @staticmethod
    def _ingredient(line: str) -> IngredientSuggestion:
        """Converta uma linha de ingrediente em nome, quantidade e unidade sugeridos."""
        match = re.match(r"^(\d+(?:[,.]\d+)?)\s+([\wÀ-ÿ]+)\s+(?:de\s+)?(.+)$", line)
        if match:
            return IngredientSuggestion(
                name=match.group(3).strip(),
                quantity=match.group(1),
                unit=match.group(2),
                confidence_score=_confidence(0.9),
            )
        quantity_match = re.match(r"^(\d+(?:[,.]\d+)?)\s+(.+)$", line)
        if quantity_match:
            return IngredientSuggestion(
                name=quantity_match.group(2).strip(),
                quantity=quantity_match.group(1),
                confidence_score=_confidence(0.78),
            )
        return IngredientSuggestion(name=line, confidence_score=_confidence(0.65))


class MockLLMRecipeParser(LLMRecipeParser):
    """Parser mockado de LLM que delega em regras determinísticas locais."""

    def parse(self, text: str) -> StructuredRecipe:
        """Executa o parser local e ajusta a confiança para simular um LLM."""
        result = RuleBasedRecipeParser().parse(text)
        result.warnings.insert(0, "Estruturação gerada pelo MockLLMRecipeParser; revise antes de salvar.")
        for ingredient in result.ingredients:
            ingredient.confidence_score = _confidence(0.8)
        for step in result.preparation_steps:
            step.confidence_score = _confidence(0.8)
        return result
