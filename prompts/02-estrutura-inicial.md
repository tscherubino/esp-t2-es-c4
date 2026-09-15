# Prompt 2 — Criação da estrutura inicial do projeto FastAPI local

## C — Contexto

Vamos iniciar a implementação do MVP local “Livro Vivo de Receitas”.

A aplicação deve rodar localmente com Python 3.14, FastAPI, Uvicorn, SQLite, SQLAlchemy, Pydantic v2, Jinja2, HTMX, Tailwind CSS via CDN, pytest e armazenamento local de arquivos.

Não devemos usar Docker, Docker Compose, PostgreSQL obrigatório ou serviços externos obrigatórios.

O MVP precisa permitir, ao final da primeira implementação:

* abrir uma página inicial;
* verificar health check;
* criar estrutura básica do projeto;
* configurar banco SQLite local;
* configurar diretório de uploads;
* carregar variáveis de ambiente;
* rodar com `uvicorn app.main:app --reload`.

## O — Objetivo

Crie a estrutura inicial do projeto FastAPI local, incluindo:

* organização limpa de diretórios;
* arquivo principal da aplicação;
* configuração por variáveis de ambiente;
* conexão local com SQLite;
* configuração inicial do SQLAlchemy;
* templates Jinja2;
* arquivos estáticos;
* diretório local para uploads;
* README inicial;
* `.env.example`;
* `.gitignore`;
* `requirements.txt` ou `pyproject.toml`.

## S — Estilo

Atue como um desenvolvedor full-stack Python experiente, com foco em MVP local simples, funcional e fácil de executar.

## T — Tom

Prático, direto e orientado à execução.

## A — Audiência

Desenvolvedor Python que irá implementar e testar o MVP localmente.

## R — Resposta esperada

Antes de escrever o código, apresente a árvore de arquivos que será criada.

Depois, gere o conteúdo completo dos arquivos necessários.

Inclua, no mínimo:

* `app/main.py`;
* `app/core/config.py`;
* `app/db/session.py`;
* `app/db/base.py`;
* `app/templates/base.html`;
* `app/templates/index.html`;
* `app/static/.gitkeep`;
* `data/.gitkeep`;
* `uploads/.gitkeep`;
* `.env.example`;
* `.gitignore`;
* `requirements.txt`;
* `README.md`.

Critérios obrigatórios:

* não usar Docker;
* usar SQLite em `data/app.db` por padrão;
* permitir troca do banco via variável `DATABASE_URL`;
* não deixar credenciais fixas no código;
* garantir endpoint `/health`;
* garantir página inicial simples em `/`;
* criar instruções para ambiente virtual com `python -m venv .venv`;
* incluir instruções para Windows, Linux e macOS;
* incluir comando de instalação com `pip install -r requirements.txt`;
* incluir comando de execução com `uvicorn app.main:app --reload`;
* ignorar `.env`, `data/*.db`, `uploads/*`, cache Python e arquivos temporários no Git;
* manter o código compatível com Python 3.14.
