# Prompt 10 — README, execução local e scripts auxiliares

## C — Contexto

O MVP “Livro Vivo de Receitas” deve rodar localmente em uma máquina de desenvolvimento, sem Docker.

A aplicação usa Python 3.14, FastAPI, SQLite, SQLAlchemy, Jinja2, HTMX, armazenamento local de arquivos, serviços mockados de IA/OCR e testes automatizados com pytest.

O projeto deve ser fácil de executar por um desenvolvedor Python sem configuração de infraestrutura externa.

## O — Objetivo

Prepare o projeto para execução local simples, com instruções claras para instalação, configuração, execução, testes e limpeza de dados.

## S — Estilo

Atue como tech lead pragmático e desenvolvedor Python experiente. Priorize simplicidade e instruções claras.

## T — Tom

Técnico, operacional e direto.

## A — Audiência

Desenvolvedor que irá rodar, testar e demonstrar o MVP localmente.

## R — Resposta esperada

Entregue:

1. README completo;
2. `.env.example`;
3. `.gitignore`;
4. comandos para criar ambiente virtual;
5. comandos para ativar ambiente virtual no Windows;
6. comandos para ativar ambiente virtual no Linux/macOS;
7. comandos para instalar dependências;
8. comandos para iniciar a aplicação;
9. comandos para executar testes;
10. instruções para resetar banco local;
11. instruções para limpar uploads locais;
12. checklist antes de testes com usuários reais.

Critérios obrigatórios:

* não usar Docker;
* usar SQLite local por padrão;
* usar `DATABASE_URL` configurável;
* banco padrão em `data/app.db`;
* uploads padrão em `uploads/`;
* mocks de IA/OCR ativados por padrão;
* não exigir chaves externas;
* documentar variáveis obrigatórias;
* documentar variáveis opcionais;
* documentar limites de upload;
* documentar como ativar provedores reais de IA/OCR futuramente;
* incluir instruções para Windows, Linux e macOS;
* permitir execução com `uvicorn app.main:app --reload`;
* permitir testes com `pytest`.