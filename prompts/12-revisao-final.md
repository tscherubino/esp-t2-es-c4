# Prompt 12 — Revisão final antes do piloto assistido

## C — Contexto

O MVP local “Livro Vivo de Receitas” já possui as funcionalidades principais implementadas:

* importação por texto;
* upload de foto ou print;
* estruturação automática com mock ou parser local;
* preservação da imagem original;
* cadastro de história/origem;
* acervo de receitas;
* lista de compras simples;
* interface web com FastAPI, Jinja2, HTMX e Tailwind;
* testes automatizados;
* execução local com ambiente virtual Python.

Agora precisamos revisar tudo antes de um piloto assistido com usuários reais.

## O — Objetivo

Faça uma revisão técnica, funcional, de segurança e de usabilidade do MVP local antes do piloto.

## S — Estilo

Atue como tech lead revisor, com foco em qualidade, segurança, usabilidade, manutenibilidade e prontidão para teste real.

## T — Tom

Crítico, construtivo e objetivo.

## A — Audiência

Equipe técnica, Product Owner e responsáveis pela validação do MVP.

## R — Resposta esperada

Entregue:

1. revisão da arquitetura;
2. revisão de código;
3. revisão de segurança;
4. revisão de privacidade;
5. revisão da experiência do usuário;
6. revisão de testes;
7. revisão do README;
8. lista de bugs prováveis;
9. lista de bloqueadores antes do piloto;
10. lista de melhorias desejáveis pós-piloto;
11. checklist final de go/no-go.

Critérios obrigatórios:

* apontar riscos de forma direta;
* diferenciar bloqueadores de melhorias desejáveis;
* validar se o MVP cobre as cinco capacidades centrais;
* verificar se o usuário consegue completar o fluxo de ponta a ponta;
* verificar se há instruções claras de execução local;
* verificar se o banco local não é versionado;
* verificar se uploads locais não são versionados;
* verificar se `.env` não é versionado;
* verificar se há tratamento de erro amigável;
* verificar se receitas e imagens podem ser excluídas;
* verificar se IA/OCR é apresentado como assistivo e sujeito a revisão;
* verificar se o app roda sem Docker e sem chaves externas.