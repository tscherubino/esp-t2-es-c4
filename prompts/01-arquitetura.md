# Prompt 1 — Arquitetura simplificada do MVP local

## C — Contexto

Estamos desenvolvendo o MVP de uma aplicação web chamada “Livro Vivo de Receitas”.

O objetivo do produto é permitir que pessoas que gostam de cozinhar possam transformar receitas dispersas, prints, fotos e cadernos antigos em um acervo culinário pessoal e familiar inteligente.

O MVP deve validar cinco capacidades:

1. importar receita por texto, foto ou print;
2. organizar automaticamente ingredientes e modo de preparo;
3. salvar imagem original;
4. adicionar origem/história da receita;
5. gerar lista de compras simples.

A aplicação será executada localmente, sem Docker, usando Python 3.14, FastAPI, SQLite, SQLAlchemy, Pydantic v2, Jinja2, HTMX e Tailwind CSS via CDN. O armazenamento de imagens será local, em diretório configurável. A IA/OCR deve ser mockada por padrão, para que o MVP funcione sem chaves externas.

## O — Objetivo

Elabore a arquitetura técnica inicial do MVP local, incluindo:

* visão geral da solução;
* módulos principais;
* estrutura de pastas;
* responsabilidades de cada camada;
* modelo de domínio inicial;
* fluxos principais de usuário;
* fluxos técnicos;
* decisões arquiteturais;
* riscos técnicos;
* trade-offs;
* plano de evolução futura.

## S — Estilo

Atue como um arquiteto de software sênior, pragmático e orientado a MVP. Evite overengineering. Priorize simplicidade, legibilidade, execução local rápida e evolução incremental.

## T — Tom

Técnico, claro, objetivo e didático.

## A — Audiência

Equipe enxuta formada por Product Owner, UX designer, desenvolvedor full-stack Python e especialista em IA/OCR em dedicação parcial.

## R — Resposta esperada

Entregue a resposta em Markdown, com as seguintes seções:

1. Visão geral da arquitetura;
2. Diagrama textual da solução;
3. Estrutura de pastas sugerida;
4. Módulos e responsabilidades;
5. Modelo de domínio inicial;
6. Fluxos principais do MVP;
7. Decisões arquiteturais;
8. Stack local recomendada;
9. O que fica fora do MVP;
10. Riscos e mitigação;
11. Evoluções futuras;
12. Backlog técnico priorizado.

Critérios obrigatórios:

* não usar Docker;
* não exigir PostgreSQL;
* usar SQLite local por padrão;
* armazenar banco em `data/app.db`;
* armazenar uploads em `uploads/`;
* usar mocks de IA/OCR por padrão;
* permitir futura migração para PostgreSQL via `DATABASE_URL`;
* separar rotas, serviços, modelos, schemas, templates e configurações;
* manter autenticação simulada ou usuário demo no MVP;
* não implementar RAG no MVP, apenas preparar evolução futura.

Não implemente código ainda. Primeiro apresente a arquitetura e aguarde validação.