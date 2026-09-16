"""Prompt interno reservado para futura implementação de LLM.

O MVP não envia este prompt a nenhum serviço externo. Ele documenta o contrato
estrutural esperado para uma futura implementação compatível com
``LLMRecipeParser``.
"""

STRUCTURED_RECIPE_PROMPT = """
Extraia a receita do texto fornecido e responda somente com JSON válido contendo:
title, servings, prep_time_minutes, ingredients, preparation_steps,
suggested_tags e warnings. Cada ingrediente e etapa deve conter
confidence_score entre 0 e 1. Preserve o texto original fora da resposta
estruturada e sinalize incertezas em warnings.
""".strip()

__all__ = ["STRUCTURED_RECIPE_PROMPT"]
