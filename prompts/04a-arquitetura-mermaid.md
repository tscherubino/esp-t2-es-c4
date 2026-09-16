# Prompt — Geração de Diagramas Arquiteturais do MVP com Mermaid

## C — Contexto

Estamos desenvolvendo o MVP local da aplicação web **“Livro Vivo de Receitas”**, uma solução para organização de receitas culinárias pessoais e familiares.

O projeto já passou pelas seguintes etapas:

1. definição da arquitetura;
2. criação da estrutura inicial FastAPI;
3. modelagem de dados com SQLite e SQLAlchemy;
4. implementação das rotas, serviços e páginas web principais, incluindo cadastro manual e operações CRUD de receitas.

O projeto possui como documentos e fontes de referência:

* `AGENTS.md`: contém as diretrizes permanentes, restrições e padrões técnicos do projeto;
* `docs/ARCHITECTURE.md`: contém a arquitetura aprovada;
* código-fonte atual: representa a implementação efetivamente existente.

A stack atual utiliza, entre outras tecnologias:

* Python 3.14;
* FastAPI;
* Uvicorn;
* SQLite;
* SQLAlchemy 2.x;
* Pydantic v2;
* Jinja2;
* HTMX;
* Tailwind CSS via CDN;
* armazenamento local de imagens;
* pytest.

O projeto é executado exclusivamente em ambiente local nesta fase.

Ainda **não foram implementados IA real, OCR real, RAG, PostgreSQL, pgvector, Docker, storage externo ou infraestrutura de produção**.

A próxima etapa do desenvolvimento será a implementação da importação assistida de receitas por texto, foto ou print, inicialmente com providers mockados.

Antes dessa evolução, desejamos consolidar visualmente a arquitetura atual utilizando **Mermaid**.

---

## O — Objetivo

Analise a documentação e o código existente e produza um conjunto de **diagramas arquiteturais em Mermaid** que represente fielmente o estado atual do MVP.

Os diagramas devem permitir compreender:

* contexto da solução;
* arquitetura lógica;
* componentes e camadas;
* dependências entre módulos;
* persistência de dados;
* fluxo das requisições;
* fluxo de cadastro manual de receitas;
* modelo de dados;
* execução local da aplicação.

Os diagramas devem servir tanto como documentação técnica quanto como material para explicar a arquitetura a novos desenvolvedores e demais participantes do projeto.

A documentação produzida deverá ser salva preferencialmente em:

`docs/ARCHITECTURE_DIAGRAMS.md`

---

## S — Estilo

Atue como um **arquiteto de software sênior especializado em documentação arquitetural, Python, FastAPI e modelagem visual de sistemas com Mermaid**.

Adote princípios inspirados no modelo C4 quando úteis, mas sem introduzir formalismo ou complexidade desnecessária ao MVP.

Os diagramas devem:

* ser tecnicamente precisos;
* ser visualmente simples;
* evitar excesso de elementos;
* usar nomenclatura consistente com o código;
* privilegiar legibilidade;
* refletir a arquitetura real, e não uma arquitetura idealizada futura.

Utilize tipos de diagramas Mermaid adequados ao objetivo de cada visão, especialmente:

* `flowchart`;
* `sequenceDiagram`;
* `erDiagram`.

Não use recursos experimentais ou sintaxe Mermaid desnecessariamente complexa.

---

## T — Tom

Técnico, claro, objetivo, didático e documental.

A documentação deve permitir que um desenvolvedor que nunca viu o projeto compreenda rapidamente como a solução está estruturada.

---

## A — Audiência

A documentação destina-se principalmente a:

* desenvolvedores Python;
* arquitetos de software;
* Product Owner;
* UX Designer;
* futuros integrantes da equipe;
* responsáveis técnicos pela evolução do MVP.

Também deve possuir clareza suficiente para ser utilizada em apresentações técnicas ou reuniões de arquitetura.

---

## R — Resposta esperada

### Etapa 1 — Inspeção

Antes de gerar qualquer diagrama:

1. leia integralmente `AGENTS.md`;
2. leia integralmente `docs/ARCHITECTURE.md`;
3. inspecione a árvore atual do projeto;
4. examine os principais arquivos de:

   * configuração;
   * banco de dados;
   * modelos;
   * schemas;
   * routers;
   * services;
   * templates;
   * uploads;
   * testes;
5. compare a arquitetura documentada com a implementação atual.

Caso exista divergência entre `ARCHITECTURE.md` e o código:

* não invente uma solução;
* registre a divergência;
* considere o código atual como evidência do estado implementado;
* indique separadamente se o `ARCHITECTURE.md` precisa ser atualizado.

---

# Diagramas obrigatórios

Produza, no mínimo, os diagramas abaixo.

## Diagrama 1 — Contexto da solução

Crie um `flowchart` apresentando o sistema no seu contexto atual.

Deve mostrar pelo menos:

* Usuário;
* Navegador Web;
* aplicação Livro Vivo de Receitas;
* banco SQLite;
* armazenamento local de imagens.

Objetivo:

mostrar de forma simples quem usa o sistema e quais recursos externos ou locais participam da solução.

Não inclua IA/OCR como componente implementado nesta visão.

---

## Diagrama 2 — Arquitetura lógica de alto nível

Crie um `flowchart` mostrando as principais camadas da aplicação.

Representar, conforme a implementação existente:

* Browser;
* FastAPI;
* Routers;
* Services;
* Schemas/Pydantic;
* Models/SQLAlchemy;
* Templates Jinja2;
* HTMX;
* SQLite;
* filesystem/uploads.

Demonstre as principais dependências e o sentido das interações.

Objetivo:

permitir compreender rapidamente como uma requisição percorre a aplicação.

---

## Diagrama 3 — Estrutura de módulos/componentes

Crie um `flowchart` mais detalhado representando os módulos efetivamente existentes no projeto.

Use os nomes reais de pacotes, módulos, routers e services encontrados no código.

Exemplo conceitual:

`main.py → routers → services → models → database`

mas não utilize esse exemplo caso a implementação real seja diferente.

Agrupe componentes visualmente por responsabilidade quando isso melhorar a compreensão, por exemplo:

* Presentation;
* Application;
* Domain/Data;
* Infrastructure.

Não invente camadas que não existem.

---

## Diagrama 4 — Modelo de dados

Utilize `erDiagram`.

Represente as entidades atualmente implementadas, tais como, se realmente existentes:

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

Para cada relacionamento, indique corretamente:

* cardinalidade;
* obrigatoriedade quando possível;
* chaves relevantes.

Não invente atributos ou relacionamentos.

Caso alguma dessas entidades ainda não exista no código, represente somente as existentes e registre a diferença.

---

## Diagrama 5 — Fluxo de cadastro manual de receita

Utilize `sequenceDiagram`.

Represente o fluxo real:

1. usuário acessa o formulário;
2. FastAPI recebe a requisição;
3. template é renderizado;
4. usuário preenche os dados;
5. formulário é enviado;
6. router recebe os dados;
7. validação Pydantic ocorre, se aplicável;
8. service processa a operação;
9. SQLAlchemy persiste os dados;
10. SQLite armazena a receita;
11. usuário recebe confirmação ou página de detalhe.

Inclua upload da imagem apenas se isso já fizer parte do fluxo implementado.

Objetivo:

demonstrar claramente o caminho de uma operação completa de cadastro.

---

## Diagrama 6 — Ciclo CRUD de receitas

Crie um `flowchart` mostrando as operações disponíveis atualmente:

* criar;
* listar;
* consultar;
* editar;
* excluir.

Mostre a relação dessas operações com:

* interface web;
* routers;
* services;
* banco;
* armazenamento de imagem quando aplicável.

O objetivo não é mostrar todas as funções do código, mas documentar o ciclo funcional principal.

---

## Diagrama 7 — Execução local

Crie um `flowchart` representando a arquitetura física/local atual.

Representar:

* máquina do desenvolvedor;
* Python 3.14;
* ambiente virtual `.venv`;
* Uvicorn;
* FastAPI;
* SQLite em `data/app.db`;
* uploads em `uploads/`;
* navegador acessando `localhost`.

Deixe explicitamente claro que esta arquitetura representa:

**Ambiente Local do MVP**

e não uma arquitetura de produção.

---

# Diagrama opcional — Fronteira para evolução do Prompt 5

Depois dos diagramas da arquitetura atual, crie **uma única visão opcional** intitulada:

### “Ponto de extensão planejado para Importação Assistida”

Este diagrama deve mostrar apenas onde a próxima capacidade provavelmente será integrada à arquitetura atual, contemplando conceitualmente:

* `RecipeImportService`;
* `OCRProvider`;
* `LLMRecipeParser`;
* implementations mock.

Utilize elementos tracejados ou alguma identificação textual como:

`PLANEJADO — ainda não implementado`

Não apresente esses componentes como parte da arquitetura atual.

O objetivo é documentar o ponto de extensão antes da execução do Prompt 5, não projetar toda a futura arquitetura de IA.

---

# Estrutura do documento

Crie ou atualize:

`docs/ARCHITECTURE_DIAGRAMS.md`

com esta estrutura:

# Diagramas Arquiteturais — Livro Vivo de Receitas

## 1. Objetivo

Breve explicação sobre a finalidade dos diagramas.

## 2. Escopo atual

Explique que os diagramas representam o estado do projeto após a implementação do Prompt 4.

## 3. Contexto da Solução

Descrição curta + diagrama Mermaid.

## 4. Arquitetura Lógica

Descrição curta + diagrama Mermaid.

## 5. Componentes e Módulos

Descrição curta + diagrama Mermaid.

## 6. Modelo de Dados

Descrição curta + `erDiagram`.

## 7. Fluxo de Cadastro Manual

Descrição curta + `sequenceDiagram`.

## 8. Ciclo CRUD de Receitas

Descrição curta + diagrama Mermaid.

## 9. Arquitetura de Execução Local

Descrição curta + diagrama Mermaid.

## 10. Ponto de Extensão para Importação Assistida

Descrição curta + diagrama opcional claramente identificado como futuro.

## 11. Observações Arquiteturais

Liste:

* decisões identificadas;
* inconsistências encontradas;
* limitações atuais;
* pontos de evolução.

---

# Regras de qualidade dos diagramas

Para todos os diagramas:

1. use nomes curtos e legíveis;
2. evite caixas com textos excessivamente longos;
3. evite cruzamento excessivo de linhas;
4. organize os elementos em fluxo lógico;
5. use `subgraph` apenas quando melhorar a compreensão;
6. não codifique cores personalizadas salvo necessidade real;
7. não use HTML complexo dentro dos elementos Mermaid;
8. mantenha sintaxe compatível com versões modernas do Mermaid;
9. não coloque detalhes de implementação irrelevantes;
10. priorize relações arquiteturais significativas;
11. use nomes de componentes iguais aos encontrados no projeto;
12. não exponha caminhos locais pessoais, credenciais ou informações sensíveis.

---

# Regras para evitar alucinação arquitetural

É obrigatório:

* não representar componente inexistente como implementado;
* não assumir arquitetura que não esteja documentada ou codificada;
* não adicionar Redis;
* não adicionar PostgreSQL;
* não adicionar Docker;
* não adicionar Kubernetes;
* não adicionar S3;
* não adicionar filas;
* não adicionar RAG;
* não adicionar vector database;
* não adicionar OCR real;
* não adicionar LLM real;
* não adicionar autenticação externa;
* não adicionar infraestrutura cloud.

Qualquer evolução futura deve aparecer somente na seção explicitamente marcada como **planejada**.

---

# Validação final

Após produzir os diagramas:

1. valide a sintaxe de cada bloco Mermaid;
2. procure referências a componentes inexistentes;
3. compare novamente os diagramas com `ARCHITECTURE.md`;
4. compare os diagramas com o código atual;
5. verifique que nenhum diagrama representa recursos futuros como já implementados;
6. revise legibilidade e excesso de complexidade.

Se houver ferramenta disponível para renderizar Mermaid localmente, utilize-a para validar a sintaxe.

Caso não haja, faça validação estática cuidadosa.

---

# Relatório final no chat

Depois de criar `docs/ARCHITECTURE_DIAGRAMS.md`, informe:

1. quais diagramas foram produzidos;
2. quais arquivos foram lidos para entender a arquitetura;
3. se houve divergências entre `ARCHITECTURE.md` e código;
4. se o documento arquitetural original precisa de atualização;
5. quais elementos foram considerados arquitetura atual;
6. quais elementos foram classificados como evolução futura.

Não modifique a implementação da aplicação nesta tarefa.

Não execute o Prompt 5.

Não refatore código.

O objetivo desta etapa é exclusivamente **documentar visualmente a arquitetura atual**.
