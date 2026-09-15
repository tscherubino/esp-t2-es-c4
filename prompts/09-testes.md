# Prompt 9 — Testes automatizados com pytest

## C — Contexto

O MVP “Livro Vivo de Receitas” precisa ser testável localmente sem Docker, sem PostgreSQL, sem OCR real e sem LLM real.

A aplicação usa FastAPI, SQLite, SQLAlchemy, Jinja2, HTMX, serviços mockados de IA/OCR e geração de lista de compras.

## O — Objetivo

Crie uma suíte inicial de testes automatizados e uma matriz de critérios de aceite para o MVP local.

## S — Estilo

Atue como engenheiro de qualidade de software com foco em MVP, testes automatizados e critérios objetivos de aceite.

## T — Tom

Técnico, estruturado e orientado à validação.

## A — Audiência

Equipe de desenvolvimento, Product Owner e responsáveis pela homologação funcional.

## R — Resposta esperada

Entregue:

1. estratégia de testes;
2. configuração do pytest;
3. testes unitários dos serviços;
4. testes de integração dos endpoints;
5. testes de upload;
6. testes do parser mock;
7. testes da lista de compras;
8. fixture de banco SQLite temporário;
9. diretório temporário para uploads nos testes;
10. matriz de critérios de aceite por funcionalidade;
11. instruções para executar os testes.

Critérios obrigatórios:

* não depender de Docker;
* não depender de PostgreSQL;
* não depender de APIs externas;
* usar SQLite temporário nos testes;
* usar mocks para OCR e LLM;
* testar criação de receita;
* testar listagem de receitas;
* testar upload válido;
* testar upload inválido;
* testar importação por texto;
* testar preservação de `original_text`;
* testar preservação da imagem original;
* testar geração de ingredientes e etapas;
* testar geração de lista de compras;
* testar edição manual de itens;
* testar falha de OCR/IA;
* testar health check;
* manter testes fáceis de rodar com `pytest`.