# Diagramas Arquiteturais — Livro Vivo de Receitas

## 1. Objetivo

Documentar visualmente a arquitetura efetivamente implementada do MVP local
após os Prompts 01–07. Este documento complementa
`docs/ARCHITECTURE.md`, facilitando a compreensão das camadas, dos fluxos de
receitas, da importação assistida e da lista de compras.

## 2. Escopo atual

O projeto usa Python 3.14, FastAPI/Uvicorn, SQLite em `data/app.db`, SQLAlchemy,
Pydantic v2, Jinja2, Tailwind CSS via CDN e armazenamento local em `uploads/`.

Existem dois caminhos separados para criar receitas:

- **Fluxo A — Cadastro manual:** persiste diretamente uma receita preenchida
  pelo usuário.
- **Fluxo B — Importação assistida:** extrai uma sugestão com providers locais,
  apresenta uma tela de revisão e só então persiste a receita confirmada.
- **Fluxo C — Lista de compras:** seleciona uma ou mais receitas, consolida os
  ingredientes de forma simples e permite ajustes manuais.

Não há APIs externas, chaves de API, OCR real, IA real, RAG, PostgreSQL,
pgvector, Docker, storage externo ou autenticação real.

## 3. Contexto da Solução

```mermaid
flowchart LR
    User[Usuário] --> Browser[Navegador Web]
    Browser <-->|HTTP local| App[Livro Vivo de Receitas\nFastAPI + Uvicorn]
    App -->|SQLAlchemy| DB[(SQLite\ndata/app.db)]
    App -->|imagem original| Files[(Filesystem local\nuploads/)]
```

O navegador interage somente com a aplicação local. O banco e os arquivos são
recursos locais do MVP.

## 4. Arquitetura Lógica

```mermaid
flowchart TB
    Browser[Browser]
    FastAPI[FastAPI\napp.main]

    subgraph Presentation[Apresentação]
        Routers[Routers\nrecipes.py / imports.py]
        Templates[Jinja2\nTemplates HTML]
        HTMX[HTMX\nprevisto; não usado atualmente]
    end

    subgraph Application[Aplicação]
        RecipeService[recipe_service.py]
        ImportService[import_service.py]
        ShoppingService[shopping_service.py]
        Storage[storage.py]
        Providers[processors\nproviders locais]
    end

    subgraph Data[Dados]
        Schemas[Pydantic v2]
        Models[SQLAlchemy models]
        Repository[recipe_repository.py]
        ShoppingRepository[shopping_repository.py]
        SQLite[(SQLite\ndata/app.db)]
        Uploads[(uploads/)]
    end

    Browser --> FastAPI --> Routers
    Routers --> Schemas
    Routers --> Templates
    Routers --> RecipeService
    Routers --> ImportService
    Routers --> ShoppingService
    Routers -.-> HTMX
    RecipeService --> Repository
    RecipeService --> Models
    RecipeService --> Storage
    ImportService --> Providers
    ImportService --> Models
    ImportService --> Storage
    ShoppingService --> ShoppingRepository
    Repository --> Models
    ShoppingRepository --> Models
    Models --> SQLite
    Storage --> Uploads
```

O Fluxo A usa `RecipeService`; o Fluxo B usa `RecipeImportService` e providers
locais antes de chegar à persistência definitiva; o Fluxo C usa
`ShoppingListService` para consolidar e editar itens.

## 5. Componentes e Módulos

```mermaid
flowchart TB
    subgraph Presentation[Presentation]
        Main[app/main.py]
        RecipesRouter[app/routers/recipes.py]
        ImportsRouter[app/routers/imports.py]
        ShoppingRouter[app/routers/shopping.py]
        TemplatesDir[app/templates/\nbase, index, recipes, shopping_list]
    end

    subgraph Application[Application]
        RecipeSvc[app/services/recipe_service.py]
        ImportSvc[app/services/import_service.py\nRecipeImportService]
        StorageSvc[app/services/storage.py]
        ShoppingSvc[app/services/shopping_service.py\nShoppingItemInput]
    end

    subgraph Processing[Importação local]
        OCRInterface[OCRProvider]
        MockOCR[MockOCRProvider]
        ManualOCR[ManualTranscriptionOCRProvider]
        ParserInterface[LLMRecipeParser]
        MockParser[MockLLMRecipeParser]
        RuleParser[RuleBasedRecipeParser]
        Structured[schemas/import.py\nsaída estruturada]
    end

    subgraph Data[Data]
        DomainSchemas[app/schemas/domain.py]
        Entities[app/models/entities.py]
        Repo[app/repositories/recipe_repository.py]
        ShoppingRepo[app/repositories/shopping_repository.py]
        Session[app/db/session.py]
        DB[(data/app.db)]
        Uploads[(uploads/)]
    end

    Main --> RecipesRouter
    Main --> ImportsRouter
    Main --> ShoppingRouter
    Main --> Session
    RecipesRouter --> DomainSchemas
    RecipesRouter --> RecipeSvc
    RecipesRouter --> TemplatesDir
    ImportsRouter --> ImportSvc
    ImportsRouter --> TemplatesDir
    ShoppingRouter --> ShoppingSvc
    ShoppingRouter --> TemplatesDir
    RecipeSvc --> Repo
    RecipeSvc --> Entities
    RecipeSvc --> StorageSvc
    ImportSvc --> OCRInterface
    ImportSvc --> ParserInterface
    ImportSvc --> Structured
    ImportSvc --> Entities
    ShoppingSvc --> ShoppingRepo
    ShoppingSvc --> Entities
    OCRInterface -.-> MockOCR
    OCRInterface -.-> ManualOCR
    ParserInterface -.-> MockParser
    ParserInterface -.-> RuleParser
    Repo --> Entities
    ShoppingRepo --> Entities
    Session --> Entities
    Session --> DB
    StorageSvc --> Uploads
```

Os providers exibidos são implementações locais e substituíveis; não há
integração externa. A lista de compras usa um serviço explícito e não depende
de conversão avançada de unidades.

## 6. Modelo de Dados

```mermaid
erDiagram
    USER {
        int id PK
        string public_id UK
        string name
        datetime created_at
        datetime updated_at
    }
    RECIPE {
        int id PK
        string public_id UK
        int user_id FK
        string title
        int servings
        int prep_time_minutes
        text original_text
        text origin_story
        datetime created_at
        datetime updated_at
    }
    RECIPE_IMAGE {
        int id PK
        string public_id UK
        int recipe_id FK
        string original_filename
        string stored_filename UK
        string content_type
        string relative_path
    }
    INGREDIENT {
        int id PK
        string public_id UK
        int recipe_id FK
        string description
        string quantity
        string unit
        string notes
        int position
    }
    PREPARATION_STEP {
        int id PK
        string public_id UK
        int recipe_id FK
        int position
        text instruction
    }
    TAG {
        int id PK
        string public_id UK
        int user_id FK
        string name
    }
    RECIPE_TAG {
        int id PK
        string public_id UK
        int recipe_id FK
        int tag_id FK
    }
    SHOPPING_LIST {
        int id PK
        string public_id UK
        int user_id FK
        string name
    }
    SHOPPING_LIST_ITEM {
        int id PK
        string public_id UK
        int shopping_list_id FK
        int recipe_id FK
        string description
        string quantity
        string unit
        string notes
        boolean is_checked
    }
    IMPORT_JOB {
        int id PK
        string public_id UK
        int user_id FK
        int recipe_id FK
        string source_type
        string status
        text original_text
        text error_message
    }

    USER ||--o{ RECIPE : owns
    USER ||--o{ TAG : creates
    USER ||--o{ SHOPPING_LIST : owns
    USER ||--o{ IMPORT_JOB : starts
    RECIPE ||--o{ RECIPE_IMAGE : has
    RECIPE ||--o{ INGREDIENT : contains
    RECIPE ||--o{ PREPARATION_STEP : includes
    RECIPE ||--o{ RECIPE_TAG : receives
    TAG ||--o{ RECIPE_TAG : classifies
    SHOPPING_LIST ||--o{ SHOPPING_LIST_ITEM : contains
    RECIPE o|--o{ SHOPPING_LIST_ITEM : originates
    RECIPE o|--o{ IMPORT_JOB : results_in
```

O modelo preserva `original_text`, `origin_story` e os metadados da imagem
original. O `ImportJob` registra o ciclo de importação e seu status.

## 7. Fluxo de Cadastro Manual

```mermaid
sequenceDiagram
    actor User as Usuário
    participant Browser as Navegador
    participant App as FastAPI/Uvicorn
    participant Router as recipes.py
    participant Schema as RecipeManualInput
    participant Service as RecipeService
    participant Storage as storage.py
    participant ORM as SQLAlchemy
    participant DB as SQLite

    User->>Browser: Acessa /recipes/new
    Browser->>App: GET /recipes/new
    App->>Router: encaminha requisição
    Router-->>Browser: renderiza formulário Jinja2
    User->>Browser: preenche e envia formulário
    Browser->>App: POST /recipes
    App->>Router: recebe multipart/form-data
    Router->>Schema: valida campos
    Schema-->>Router: dados válidos
    Router->>Service: create_recipe(...)
    Service->>ORM: cria receita e relacionados
    ORM->>DB: INSERT / COMMIT
    opt imagem enviada
        Router->>Storage: save_image(upload)
        Storage->>DB: registra RecipeImage via ORM
    end
    Router-->>Browser: redirect 303 para detalhe
```

Este fluxo não passa por providers de importação e permanece independente do
Fluxo B.

## 8. Ciclo CRUD de Receitas

```mermaid
flowchart LR
    UI[Templates Jinja2]
    Create[criar]
    List[listar]
    Read[consultar]
    Update[editar]
    Delete[excluir]
    Router[recipes.py]
    Service[recipe_service.py]
    Repository[recipe_repository.py]
    DB[(SQLite)]
    Files[storage.py\nuploads/]

    UI --> Create
    UI --> List
    UI --> Read
    UI --> Update
    UI --> Delete
    Create --> Router
    List --> Router
    Read --> Router
    Update --> Router
    Delete --> Router
    Router --> Service
    Router --> Repository
    Service --> DB
    Repository --> DB
    Create -.->|imagem opcional| Files
    Update -.->|imagem opcional| Files
    Read -.->|endpoint controlado| Files
    Delete -.->|remove arquivo| Files
```

## 8.1 Fluxo de lista de compras

```mermaid
sequenceDiagram
    participant User as Usuário
    participant UI as shopping_list.html
    participant Router as shopping.py
    participant Service as ShoppingListService
    participant DB as SQLite

    User->>UI: seleciona uma ou mais receitas
    UI->>Router: POST /shopping-list/generate
    Router->>Service: create_list_from_recipes(...)
    Service->>Service: consolida nome + unidade
    Service->>DB: persiste ShoppingList e itens
    DB-->>UI: lista editável
    User->>UI: edita, marca, remove ou adiciona item
    UI->>Router: POST operação do item
    Router->>Service: atualiza estado
    User->>UI: exclui uma lista anterior
    UI->>Router: POST /shopping-list/{id}/delete
    Router->>Service: delete_shopping_list(...)
    Service->>DB: remove lista e itens em cascata
    Service->>DB: COMMIT
```

Quantidades numéricas são somadas apenas quando o nome normalizado e a unidade
normalizada coincidem. Unidades diferentes, quantidades textuais e observações
não são convertidas ou descartadas; quando necessário, os itens permanecem
separados e a interface informa o motivo.

## 9. Arquitetura de Execução Local

```mermaid
flowchart TB
    subgraph Local[Ambiente Local do MVP]
        Python[Python 3.14]
        Venv[.venv]
        Requirements[requirements.txt]
        Uvicorn[uvicorn app.main:app --reload]
        FastAPI[FastAPI]
        SQLite[(data/app.db)]
        Uploads[(uploads/)]
        Templates[Templates Jinja2]
        Static[app/static/]

        Python --> Venv
        Venv --> Requirements
        Venv --> Uvicorn
        Uvicorn --> FastAPI
        FastAPI --> SQLite
        FastAPI --> Uploads
        FastAPI --> Templates
        FastAPI --> Static
    end

    Browser[Navegador\n127.0.0.1:8000]
    Browser -->|HTTP local| Uvicorn
```

Esta é uma arquitetura local, não de produção. Tailwind CSS é carregado pelo
navegador via CDN, sem tornar serviços externos dependência da aplicação.

## 10. Importação assistida e pontos de extensão

```mermaid
flowchart LR
    ImportRoute[imports.py]
    ImportService[RecipeImportService]
    OCR[OCRProvider]
    Parser[LLMRecipeParser]
    MockOCR[MockOCRProvider]
    ManualOCR[ManualTranscriptionOCRProvider]
    MockLLM[MockLLMRecipeParser]
    RuleParser[RuleBasedRecipeParser]
    Review[Tela de revisão]
    Persist[RecipeService\npersistência após confirmação]

    ImportRoute --> ImportService
    ImportService -.-> OCR
    ImportService -.-> Parser
    OCR -.-> MockOCR
    OCR -.-> ManualOCR
    Parser -.-> MockLLM
    Parser -.-> RuleParser
    ImportService --> Review
    Review -->|usuário confirma/edita| Persist

```

Os providers locais e a revisão humana estão implementados. As interfaces
`OCRProvider` e `LLMRecipeParser` continuam sendo pontos de extensão para
providers reais futuros, sem alterar o fluxo de revisão. Não existem APIs
externas nem providers reais no MVP.

## 10.1 Controles de upload e privacidade

```mermaid
flowchart LR
    Upload[Upload de imagem]
    Type[Whitelist de tipo]
    Size[Limite de 5 MB]
    Signature[Assinatura binária]
    UUID[UUID + extensão segura]
    Private[(uploads/ fora de acesso público)]
    Endpoint[Endpoint controlado]
    Delete[Exclusão junto da receita]

    Upload --> Type --> Size --> Signature --> UUID --> Private
    Private --> Endpoint
    Private --> Delete
```

O fluxo rejeita tipos não permitidos, conteúdo incompatível e arquivos acima
do limite antes da persistência. O banco e os uploads são locais e ignorados
no Git; logs de falha não carregam texto, imagem ou história da receita.

## 11. Observações Arquiteturais

### Decisões identificadas

- Fluxo A e Fluxo B são caminhos separados para criação de receitas.
- A importação nunca persiste definitivamente sem revisão humana.
- Texto original e imagem original são preservados.
- Providers locais são substituíveis por interfaces, sem chaves externas.
- SQLite e uploads permanecem locais.
- Uploads são validados, armazenados com UUID e servidos por endpoint controlado.
- Exclusão de receita remove a imagem local associada.
- A aplicação continua um monólito modular com HTML server-side.

### Limitações atuais

- providers são mocks ou regras locais, não OCR/IA reais;
- a tela de revisão é parte do fluxo de importação e não substitui o cadastro
  manual;
- a lista de compras não converte unidades nem tenta equivalências complexas;
- a validação de assinatura é intencionalmente mínima e não substitui um
  antivírus ou uma biblioteca completa de decodificação de imagens;
- autenticação real e multiusuário continuam fora do MVP.

### Evoluções futuras

- adicionar providers reais somente atrás das interfaces existentes e por
  configuração de ambiente;
- avaliar OCR/LLM externos sem alterar a revisão humana;
- revisar `docs/ARCHITECTURE.md` para alinhar nomes e estado atual;
- implementar os próximos prompts somente após validação deste fluxo.
