# Prompt 11 — Preparação para evolução futura com IA real, OCR real e RAG

## C — Contexto

O MVP local “Livro Vivo de Receitas” não deve implementar IA real, OCR real ou RAG completo neste momento. Porém, a arquitetura deve estar preparada para evoluir.

No futuro, o usuário poderá usar recursos como:

* transcrição automática de receitas manuscritas;
* extração automática de ingredientes a partir de imagens;
* busca semântica no acervo;
* perguntas ao acervo pessoal;
* sugestões de receitas com base em ingredientes;
* geração de lista de compras a partir de conversa;
* assistente culinário familiar.

## O — Objetivo

Proponha uma evolução futura da arquitetura do MVP local para suportar IA real, OCR real, PostgreSQL, pgvector, RAG e integrações externas, sem alterar o núcleo do produto.

## S — Estilo

Atue como arquiteto de IA aplicada e evolução de produtos digitais, com foco em transição segura de MVP local para produto escalável.

## T — Tom

Técnico, estratégico e objetivo.

## A — Audiência

Tech lead, especialista em IA, Product Owner e equipe de desenvolvimento.

## R — Resposta esperada

Entregue:

1. plano de evolução pós-MVP;
2. quais interfaces atuais devem ser preservadas;
3. como substituir mocks por provedores reais;
4. estratégia futura de OCR;
5. estratégia futura de LLM;
6. estratégia futura de embeddings;
7. estratégia futura com PostgreSQL + pgvector;
8. campos que devem ser indexados para RAG;
9. exemplos de consultas semânticas;
10. riscos de privacidade;
11. riscos de custo;
12. critérios para decidir quando implementar cada evolução.

Critérios obrigatórios:

* não implementar RAG agora;
* não implementar PostgreSQL agora;
* não tornar IA real obrigatória agora;
* preservar arquitetura de providers;
* manter independência de provedor;
* prever exclusão de embeddings quando receita for apagada;
* prever isolamento por usuário/família;
* prever logs e rastreabilidade;
* prever camada de configuração por variáveis de ambiente;
* diferenciar claramente MVP local de evolução futura.