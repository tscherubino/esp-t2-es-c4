# Diagramas Arquiteturais — Livro Vivo de Receitas

## 1. Objetivo

Este documento registra visualmente a arquitetura efetivamente implementada do
MVP local após os Prompts 01–04. Os diagramas complementam
`docs/ARCHITECTURE.md` e servem como referência rápida para desenvolvimento,
revisão técnica e evolução incremental.

## 2. Escopo atual

O estado documentado inclui o scaffold FastAPI, a modelagem SQLAlchemy, o fluxo
manual de receitas, o CRUD web, a preservação de imagens locais e os endpoints
JSON iniciais. A execução é local com Python 3.14, SQLite em `data/app.db` e
arquivos em `uploads/`.

IA real, OCR real, RAG, PostgreSQL, pgvector, Docker, storage externo,
autenticação real e infraestrutura de produção continuam fora do escopo. A
importação atual preserva texto/imagem e cria um `ImportJob` pendente, sem
estruturação automática.

## 3. Contexto da Solução

O usuário acessa a aplicação pelo navegador. FastAPI/Uvicorn atende as
requisições locais, SQLAlchemy persiste dados no SQLite e o storage local mantém
as imagens originais.

```mermaid
flowchart LR
    User[Usuário] --> Browser[Navegador Web]
    Browser <-->|HTTP local| App[Livro Vivo de Receitas\nFastAPI + Uvicorn]
    App -->|SQLAlchemy| DB[(SQLite\ndata/app.db)]
    App -->|imagens originais| Files[(Filesystem\nuploads/)]
```

Não há APIs de terceiros ou serviços de nuvem participando da arquitetura atual.

## 4. Arquitetura Lógica

As rotas recebem requisições, validam formulários com Pydantic, delegam casos de
uso aos services e usam repositories/modelos para consultar e persistir dados.
Templates Jinja2 retornam HTML; o endpoint JSON oferece uma base para futuras
interfaces. HTMX está previsto na arquitetura, mas ainda não participa dos
fluxos atuais.

```mermaid
flowchart TB
    Browser[Browser]
    FastAPI[FastAPI\napp.main]

    subgraph Presentation[Apresentação]
        Routers[Routers\nrecipes.py / imports.py]
        Templates[Jinja2\nTemplates HTML]
        HTMX[HTMX\nplanejado; não utilizado]
    end

    subgraph Application[Aplicação]
        Services[Services\nrecipe_service.py / import_service.py]
        Storage[Storage service\nvalidação de imagens]
    end

    subgraph DomainData[Domínio e dados]
        Schemas[Schemas\nPydantic v2]
        Models[Models\nSQLAlchemy]
        Repositories[Repositories\nrecipe_repository.py]
    end

    SQLite[(SQLite\ndata/app.db)]
    Uploads[(Filesystem\nuploads/)]

    Browser --> FastAPI --> Routers
    Routers --> Schemas
    Routers --> Services
    Routers --> Templates
    Routers -.-> HTMX
    Services --> Repositories
    Services --> Models
    Services --> Storage
    Repositories --> Models
    Models --> SQLite
    Storage --> Uploads
```

## 5. Componentes e Módulos

```mermaid
flowchart TB
    subgraph Presentation[Presentation]
        Main[app/main.py]
        RecipeRouter[app/routers/recipes.py]
        ImportRouter[app/routers/imports.py]
        WebTemplates[app/templates/\nbase, index, recipes]
    end

    subgraph Application[Application]
        RecipeService[app/services/recipe_service.py]
        ImportService[app/services/import_service.py]
        StorageService[app/services/storage.py]
    end

    subgraph Domain[Domain / Data]
        DomainSchemas[app/schemas/domain.py]
        Entities[app/models/entities.py]
        RecipeRepository[app/repositories/recipe_repository.py]
    end

    subgraph Infrastructure[Infrastructure]
        Config[app/core/config.py]
        Session[app/db/session.py]
        Base[app/db/base.py]
        DB[(data/app.db)]
        Uploads[(uploads/)]
    end

    Main --> RecipeRouter
    Main --> ImportRouter
    Main --> Config
    Main --> Session
    RecipeRouter --> DomainSchemas
    RecipeRouter --> RecipeService
    RecipeRouter --> RecipeRepository
    RecipeRouter --> WebTemplates
    ImportRouter --> ImportService
    ImportRouter --> RecipeRepository
    ImportRouter --> WebTemplates
    RecipeService --> Entities
    RecipeService --> RecipeRepository
    RecipeService --> StorageService
    ImportService --> Entities
    ImportService --> StorageService
    RecipeRepository --> Entities
    StorageService --> Uploads
    Session --> Base
    Session --> Entities
    Session --> DB
```

Os testes em `tests/` cobrem endpoints básicos, criação do banco e o fluxo
manual ponta a ponta. `app/static/` existe para estáticos locais mínimos; o
estilo atual usa Tailwind CSS via CDN.

## 6. Modelo de Dados

As entidades abaixo são as implementadas em `app/models/entities.py`. Os IDs
inteiros são internos e cada entidade possui `public_id` textual UUID.

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

`recipe_id` é opcional em `ShoppingListItem` e `ImportJob`; por isso esses dois
relacionamentos são representados como opcionais. As tabelas de lista de
compras existem no modelo, mas ainda não possuem páginas ou services próprios.

## 7. Fluxo de Cadastro Manual

```mermaid
sequenceDiagram
    actor User as Usuário
    participant Browser as Navegador
    participant App as FastAPI/Uvicorn
    participant Router as recipes.py
    participant Schema as RecipeManualInput
    participant Service as recipe_service.py
    participant Storage as storage.py
    participant ORM as SQLAlchemy
    participant DB as SQLite
    participant Files as uploads/

    User->>Browser: Acessa /recipes/new
    Browser->>App: GET /recipes/new
    App->>Router: encaminha requisição
    Router-->>Browser: Jinja2 renderiza formulário
    User->>Browser: Preenche receita e imagem opcional
    Browser->>App: POST /recipes multipart/form-data
    App->>Router: recebe formulário
    Router->>Schema: valida dados e listas
    Schema-->>Router: entrada válida
    Router->>Service: create_recipe(...)
    Service->>ORM: cria Recipe e dados relacionados
    ORM->>DB: INSERT / COMMIT
    opt imagem enviada
        Router->>Storage: save_image(upload)
        Storage->>Files: grava nome UUID seguro
        Router->>ORM: associa RecipeImage
        ORM->>DB: INSERT / COMMIT
    end
    Router-->>Browser: redirect 303 para detalhe
    Browser->>App: GET /recipes/{public_id}
    App->>Router: consulta receita
    Router->>ORM: carrega relacionamentos
    ORM->>DB: SELECT
    Router-->>Browser: Jinja2 renderiza detalhe
```

O texto original, a história/origem e a imagem original permanecem separados
dos dados editáveis estruturados. A imagem é acessada por endpoint controlado.

## 8. Ciclo CRUD de Receitas

```mermaid
flowchart LR
    UI[Templates Jinja2]
    Create[POST /recipes\ncriar]
    List[GET /recipes\nlistar]
    Read[GET /recipes/{id}\nconsultar]
    Update[POST /recipes/{id}/edit\neditar]
    Delete[POST /recipes/{id}/delete\nexcluir]
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
    Delete -.->|remove imagem associada| Files
```

Também existem os endpoints JSON `GET /api/recipes` e
`GET /api/recipes/{public_id}`. O fluxo de lista de compras ainda não foi
implementado como funcionalidade web.

## 9. Arquitetura de Execução Local

```mermaid
flowchart TB
    subgraph Local[Ambiente Local do MVP]
        Python[Python 3.14]
        Venv[.venv]
        Dependencies[requirements.txt]
        Uvicorn[uvicorn app.main:app --reload]
        FastAPI[FastAPI\napp.main]
        SQLite[(SQLite\ndata/app.db)]
        Uploads[(uploads/)]
        Templates[Templates Jinja2]
        Static[Arquivos estáticos]

        Python --> Venv
        Venv --> Dependencies
        Venv --> Uvicorn
        Uvicorn --> FastAPI
        FastAPI --> SQLite
        FastAPI --> Uploads
        FastAPI --> Templates
        FastAPI --> Static
    end

    Browser[Navegador\nlocalhost / 127.0.0.1:8000]
    Browser -->|HTTP local| Uvicorn
```

Esta visão representa apenas execução local, não produção. Tailwind CSS é
carregado via CDN no navegador, conforme a decisão do MVP, mas não existe
serviço externo obrigatório para a aplicação, o banco ou o armazenamento local.

## 10. Ponto de Extensão para Importação Assistida

Os componentes tracejados são planejados para o próximo ciclo. Atualmente,
`app/services/import_service.py` apenas preserva texto/imagem e cria
`ImportJob(status="pending")`.

```mermaid
flowchart LR
    Current[imports.py\nrota atual] --> ImportService[import_service.py\nimplementado: preservação]
    ImportService -.-> Planned[RecipeImportService\nPLANEJADO — ainda não implementado]
    Planned -.-> OCR[OCRProvider\nPLANEJADO]
    Planned -.-> LLM[LLMRecipeParser\nPLANEJADO]
    Planned -.-> Mocks[implementations mock\nPLANEJADO]
    Planned -.-> Review[revisão humana\nfluxo futuro]
    ImportService --> Sources[(texto original\n+ uploads/)]
```

Nenhum provider real, chave externa, LLM ou OCR está representado como parte da
arquitetura atual.

## 11. Observações Arquiteturais

### Decisões identificadas

- monólito modular local, adequado ao MVP;
- renderização server-side com Jinja2;
- SQLite em `data/app.db` e filesystem em `uploads/`;
- usuário demo, sem autenticação real;
- nomes internos UUID para imagens e validação de tipo/tamanho;
- separação entre routers, services, repositories, schemas e modelos;
- dados originais preservados separadamente dos dados estruturados.

### Inconsistências encontradas

- `docs/ARCHITECTURE.md` sugere `app/config.py`, mas o código usa
  `app/core/config.py`;
- o documento usa `InstructionStep`, enquanto o modelo real usa
  `PreparationStep`;
- `docs/ARCHITECTURE.md` foi originalmente escrito antes da implementação e
  ainda descreve algumas capacidades como futuras;
- HTMX está na stack aprovada, mas ainda não é utilizado nos templates atuais;
- modelos de lista de compras existem, porém não há fluxo web correspondente;
- não existe ainda o pacote `processors/` previsto para providers de IA/OCR.

### Limitações atuais

- importação não estrutura automaticamente texto ou imagem;
- não há IA/OCR real;
- não há CRUD de lista de compras;
- não há autenticação ou multiusuário real;
- inicialização de banco usa `create_all` e ajuste local simples, sem Alembic;
- Tailwind depende do CDN para carregar estilos no navegador.

### Pontos de evolução

1. executar o Prompt 05 com providers mockados de importação;
2. manter a preservação e a revisão humana das fontes originais;
3. adicionar lista de compras em ciclo próprio;
4. revisar `docs/ARCHITECTURE.md` para alinhar nomes e estado implementado;
5. somente depois avaliar OCR/IA reais, autenticação e demais evoluções.
