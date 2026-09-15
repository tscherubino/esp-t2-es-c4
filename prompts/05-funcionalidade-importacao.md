# Prompt 5 — Importação por texto, foto ou print com IA/OCR mockados

## C — Contexto

O MVP “Livro Vivo de Receitas” precisa permitir importar receitas por texto, foto ou print.

No cenário local simplificado, não queremos depender obrigatoriamente de chaves externas, APIs pagas ou OCR real. Portanto, a solução deve usar mocks por padrão.

Para texto colado, o sistema deve tentar estruturar a receita com um parser local simples ou mock de LLM.

Para foto ou print, o sistema deve salvar a imagem original e permitir que o usuário informe uma transcrição manual opcional. Futuramente, esse fluxo poderá ser substituído ou complementado por OCR real.

A camada de IA/OCR deve ser desacoplada para permitir evolução futura.

## O — Objetivo

Implemente a camada de importação e estruturação automática de receitas com mocks e serviços substituíveis.

## S — Estilo

Atue como engenheiro de IA aplicada em MVPs, priorizando desacoplamento, rastreabilidade e funcionamento local sem dependências externas.

## T — Tom

Técnico, cauteloso e orientado a execução.

## A — Audiência

Desenvolvedor backend Python e especialista em IA/OCR.

## R — Resposta esperada

Entregue:

1. interface abstrata `OCRProvider`;
2. implementação `MockOCRProvider`;
3. implementação opcional `ManualTranscriptionOCRProvider`;
4. interface abstrata `LLMRecipeParser`;
5. implementação `MockLLMRecipeParser`;
6. implementação `RuleBasedRecipeParser` simples;
7. serviço `RecipeImportService`;
8. schemas Pydantic para saída estruturada;
9. prompt interno futuro para extração estruturada por LLM;
10. mecanismo simples de `confidence_score`;
11. endpoint para importar receita por texto;
12. endpoint para importar receita por imagem/print;
13. tela de revisão antes de salvar definitivamente;
14. testes unitários dos providers e do serviço de importação.

Critérios obrigatórios:

* rodar sem chave de API;
* rodar sem OCR real;
* nunca apagar o texto original;
* nunca descartar a imagem original;
* permitir edição manual dos campos extraídos;
* retornar JSON estruturado validado por Pydantic;
* tratar falhas de OCR/IA de forma amigável;
* registrar status do `ImportJob`;
* não expor chaves de API no frontend;
* manter provedores reais como evolução futura;
* permitir ativar provedor real apenas por variável de ambiente no futuro.

Formato esperado da receita estruturada:

{
"title": "string",
"servings": "string | null",
"prep_time_minutes": "integer | null",
"ingredients": [
{
"name": "string",
"quantity": "string | null",
"unit": "string | null",
"notes": "string | null",
"confidence_score": "number"
}
],
"preparation_steps": [
{
"step_number": "integer",
"description": "string",
"confidence_score": "number"
}
],
"suggested_tags": ["string"],
"warnings": ["string"]
}