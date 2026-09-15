# Prompt 3 — Modelagem de dados com SQLite e SQLAlchemy

## C — Contexto

O MVP local “Livro Vivo de Receitas” precisa armazenar receitas pessoais, ingredientes, etapas de preparo, imagens originais, origem/história afetiva e listas de compras simples.

A aplicação usará SQLite local, SQLAlchemy 2.x e Pydantic v2.

Neste MVP, não usaremos PostgreSQL, pgvector, autenticação real nem RAG. Devemos manter o modelo simples, mas preparado para evolução futura.

## O — Objetivo

Projete e implemente o modelo de dados inicial do MVP com SQLAlchemy e Pydantic.

As entidades mínimas são:

* User;
* Recipe;
* RecipeImage;
* Ingredient;
* PreparationStep;
* Tag;
* RecipeTag;
* ShoppingList;
* ShoppingListItem;
* ImportJob.

## S — Estilo

Atue como especialista em modelagem de dados para MVPs. Evite complexidade desnecessária, mas preserve clareza, integridade e extensibilidade.

## T — Tom

Técnico, organizado e preciso.

## A — Audiência

Desenvolvedor backend Python responsável por implementar persistência, schemas e serviços.

## R — Resposta esperada

Entregue:

1. explicação breve do modelo;
2. diagrama textual das entidades;
3. modelos SQLAlchemy completos;
4. schemas Pydantic para criação, leitura e atualização;
5. função de inicialização do banco local;
6. ajustes necessários em `app/main.py` para inicializar tabelas no startup, se apropriado;
7. observações sobre índices, relacionamentos e exclusões.

Critérios obrigatórios:

* usar UUID textual como identificador público;
* manter `id` inteiro interno, se isso simplificar o SQLite;
* manter timestamps de criação e atualização;
* permitir receita sem imagem;
* permitir receita importada por texto puro;
* permitir imagem original associada à receita;
* preservar campo `original_text`;
* preservar campo `origin_story`;
* armazenar status do `ImportJob` como `pending`, `processing`, `completed` ou `failed`;
* evitar tipos proprietários de banco;
* manter compatibilidade futura com PostgreSQL;
* não implementar pgvector no MVP;
* não implementar Alembic, salvo se for estritamente necessário;
* se não usar Alembic, documentar como resetar o banco local durante o desenvolvimento.