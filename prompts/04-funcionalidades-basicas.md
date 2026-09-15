# Prompt 4 — Rotas, serviços e páginas web principais

## C — Contexto

A aplicação “Livro Vivo de Receitas” já possui estrutura FastAPI, banco SQLite local, modelos SQLAlchemy e schemas Pydantic.

Precisamos implementar as rotas, os serviços de aplicação e as páginas web server-side do MVP usando Jinja2, HTMX e Tailwind CSS via CDN.

O usuário deve conseguir:

* criar receita manualmente;
* listar receitas;
* visualizar detalhe da receita;
* editar receita;
* excluir receita;
* importar receita por texto;
* fazer upload de imagem ou print;
* visualizar imagem original;
* adicionar história/origem;
* gerar lista de compras simples.

## O — Objetivo

Implemente rotas FastAPI, serviços de aplicação e templates HTML mínimos para operar o MVP de ponta a ponta em execução local.

## S — Estilo

Atue como desenvolvedor full-stack Python com foco em entrega incremental. O código deve ser limpo, simples, funcional e fácil de evoluir.

## T — Tom

Pragmático, técnico e orientado a produto.

## A — Audiência

Equipe de desenvolvimento que precisa validar rapidamente o fluxo com usuários reais.

## R — Resposta esperada

Entregue:

1. routers FastAPI organizados por domínio;
2. serviços separados das rotas;
3. templates Jinja2;
4. componentes HTMX quando fizer sentido;
5. formulários web para criar/importar receitas;
6. listagem de receitas;
7. página de detalhe da receita;
8. upload de imagem;
9. endpoint controlado para servir imagem;
10. geração de lista de compras;
11. mensagens de erro amigáveis;
12. testes básicos dos endpoints.

Critérios obrigatórios:

* não colocar regra de negócio pesada dentro dos routers;
* validar uploads por tipo e tamanho;
* permitir apenas imagens nos uploads iniciais;
* armazenar imagem em diretório configurável;
* servir imagens por endpoint controlado, não como pasta pública direta;
* usar dependência de sessão de banco compatível com SQLite local;
* retornar HTML para páginas principais;
* preparar endpoints JSON simples para futura API mobile;
* usar usuário demo no MVP;
* permitir rodar tudo sem autenticação real;
* documentar no README como testar os fluxos manualmente.