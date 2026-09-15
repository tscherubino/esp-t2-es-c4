# Prompt 7 — Lista de compras simples

## C — Contexto

O MVP “Livro Vivo de Receitas” precisa gerar uma lista de compras simples a partir de uma ou mais receitas selecionadas.

A primeira versão não precisa resolver perfeitamente conversão de unidades, equivalência de ingredientes nem integração com supermercado.

O objetivo é gerar valor prático rapidamente: ajudar o usuário a transformar receitas em uma lista editável de itens para comprar.

## O — Objetivo

Implemente a funcionalidade de lista de compras simples.

O usuário deve conseguir:

* selecionar uma ou mais receitas;
* gerar lista consolidada de ingredientes;
* editar itens;
* marcar itens como comprados;
* remover itens;
* adicionar item manual;
* visualizar lista em formato amigável;
* copiar a lista como texto simples.

## S — Estilo

Atue como desenvolvedor de produto orientado a valor. Priorize uma solução simples, útil e extensível.

## T — Tom

Pragmático e direto.

## A — Audiência

Usuários que cozinham em casa e querem reduzir esforço antes de ir ao mercado.

## R — Resposta esperada

Entregue:

1. modelo de dados complementar, se necessário;
2. serviço `ShoppingListService`;
3. endpoints para criar, listar, editar e concluir itens;
4. template de lista de compras;
5. botão de geração a partir de uma receita;
6. botão de geração a partir de múltiplas receitas;
7. funcionalidade de copiar lista como texto;
8. testes unitários.

Critérios obrigatórios:

* funcionar com SQLite local;
* consolidar ingredientes com mesmo nome quando a unidade for igual;
* quando não for possível consolidar, listar separadamente;
* preservar observações do ingrediente;
* permitir edição manual;
* não tentar conversões complexas no MVP;
* indicar ao usuário quando quantidades não foram somadas por terem unidades diferentes;
* manter design simples para uso em celular;
* permitir que a lista seja usada mesmo sem login real.
