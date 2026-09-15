# Arquitetura do MVP — Livro Vivo de Receitas

**Status:** aprovada como arquitetura inicial para implementação incremental
**Versão:** 1.0
**Data:** 2026-09-15
**Escopo:** MVP local, sem código de aplicação nesta etapa

## 1. Visão geral da arquitetura

O Livro Vivo de Receitas será um monólito modular Python executado localmente.
O FastAPI atenderá as rotas web e coordenará os casos de uso; Jinja2 renderizará
as páginas HTML; HTMX será usado apenas em interações pequenas que simplifiquem
o fluxo; e Tailwind CSS será carregado via CDN.

O SQLite será o banco padrão, localizado em `data/app.db`, acessado por
SQLAlchemy. Imagens importadas serão salvas localmente em `uploads/`. O texto
original e a imagem original serão mantidos separados dos dados estruturados,
para permitir revisão e edição humana sem perda da fonte.

O processamento automático de texto, IA e OCR ficará atrás de serviços internos
com uma implementação mock determinística por padrão. Assim, o MVP funciona sem
chaves, contas ou serviços externos e pode evoluir para integrações reais sem
acoplar as rotas a um fornecedor.

## 2. Diagrama textual da solução

```text
Usuário no navegador
        |
        v
FastAPI (rotas web e endpoints HTMX)
        |
        v
Casos de uso / serviços de aplicação
   |             |              |
   v             v              v
Receitas     Importação      Lista de compras
   |             |
   v             v
SQLAlchemy   Parser/OCR/IA mockados
   |             |
   v             v
SQLite       uploads/
data/app.db (imagem original)
```

Fluxo transversal: rotas recebem e validam dados com Pydantic, serviços
coordenam regras de negócio, repositórios persistem entidades e templates
apresentam o resultado. Nenhuma camada de domínio deve depender diretamente de
FastAPI, Jinja2 ou de um fornecedor de IA/OCR.

## 3. Estrutura de pastas sugerida

```text
.
├── app/
│   ├── main.py                 # ponto de entrada FastAPI
│   ├── config.py               # configurações locais e caminhos
│   ├── db/
│   │   ├── base.py             # base declarativa e configuração SQLAlchemy
│   │   └── session.py          # engine e sessões
│   ├── models/                 # modelos ORM persistidos
│   ├── schemas/                # schemas Pydantic v2 de entrada e saída
│   ├── repositories/           # persistência e consultas
│   ├── services/               # casos de uso e regras de negócio
│   ├── processors/             # contratos e mocks de parser/OCR/IA
│   ├── routers/                # rotas HTTP e endpoints HTMX
│   ├── templates/              # templates Jinja2 e fragmentos HTMX
│   └── static/                 # apenas estáticos mínimos locais
├── tests/                      # testes pytest
├── docs/
│   └── ARCHITECTURE.md         # esta decisão arquitetural
├── data/                       # criado localmente; contém data/app.db
├── uploads/                    # criado localmente; contém imagens importadas
├── prompts/                    # roteiro de execução incremental
├── AGENTS.md                   # instruções permanentes do projeto
├── README.md                   # instalação, execução, testes e limitações
└── pyproject.toml              # dependências e configuração de ferramentas
```

`data/app.db` e o conteúdo de `uploads/` são artefatos locais e não devem ser
versionados. Arquivos `.env` também não devem ser versionados.

## 4. Módulos e responsabilidades

### Configuração e infraestrutura

- `config.py`: define configurações com valores locais seguros, incluindo
  `DATABASE_URL` opcional e o diretório local de uploads. O padrão deve ser
  `sqlite:///./data/app.db` e `uploads/`.
- `db/`: cria engine, sessões e base ORM. A configuração não deve exigir
  PostgreSQL nem serviço externo.
- `models/`: representa as tabelas e relacionamentos mínimos do domínio.

### Interface e validação

- `routers/`: traduz HTTP para casos de uso, escolhe templates e trata respostas
  e erros. Não deve concentrar regras de negócio ou consultas SQL.
- `schemas/`: valida entradas e saídas com Pydantic v2, incluindo dados de
  receita, ingredientes, etapas, importação e lista de compras.
- `templates/`: páginas server-side com Jinja2. A mensagem de que a
  estruturação automática pode errar deve aparecer no fluxo de revisão.
- HTMX: opcional, para salvar ou atualizar pequenos fragmentos sem criar uma
  SPA. Não introduzir framework JavaScript ou build frontend.

### Aplicação e domínio

- `services/`: implementa casos de uso como criar receita, importar conteúdo,
  revisar/editar estrutura, registrar história e montar lista de compras.
- `repositories/`: encapsula persistência e consultas necessárias, mantendo os
  serviços independentes dos detalhes de SQLAlchemy.
- `processors/`: define contratos simples para extração/normalização e fornece
  mocks determinísticos de parser, OCR e IA. A saída automática deve ser tratada
  como sugestão editável, nunca como verdade definitiva.

## 5. Modelo de domínio inicial

### Receita (`Recipe`)

Representa o acervo principal. Deve conter, no mínimo:

- identificador;
- título editável;
- texto original importado, quando houver;
- origem e história editáveis;
- ingredientes estruturados;
- etapas do modo de preparo;
- referência para a imagem original, quando houver;
- datas de criação e atualização.

### Ingrediente (`Ingredient`)

Item estruturado pertencente a uma receita, com descrição editável e, quando
possível, quantidade, unidade e observações. A descrição original não deve ser
descartada quando a estruturação automática produzir campos separados.

### Etapa (`InstructionStep`)

Etapa ordenada do modo de preparo, com texto editável e posição explícita.

### Imagem original (`RecipeImage`)

Metadados da imagem preservada em `uploads/`, incluindo nome interno seguro,
nome original informativo, tipo validado e caminho relativo. O nome fornecido
pelo usuário não deve ser usado diretamente como caminho de armazenamento.

### Lista de compras (`ShoppingList` e itens)

Representação simples, derivada dos ingredientes de uma ou mais receitas
selecionadas. Cada item pode conter descrição, quantidade/unidade quando
disponíveis e estado de concluído. Não haverá estoque, preços, sincronização ou
planejamento de compras no MVP.

### Usuário demo

O MVP usará um usuário demo/sessão local simulada para delimitar o acervo sem
implementar autenticação, cadastro, autorização ou recuperação de senha reais.

## 6. Fluxos principais do MVP

### 6.1 Criar ou importar receita

1. O usuário abre o formulário de nova receita.
2. Informa texto, seleciona uma foto/print ou combina as fontes disponíveis.
3. A aplicação valida o upload e salva a imagem original em `uploads/`.
4. O texto original é preservado no registro da receita.
5. O processor mockado sugere título, ingredientes e etapas.
6. A aplicação mostra a revisão, sinalizando que a extração pode conter erros.
7. O usuário edita e confirma os dados estruturados.
8. A receita é persistida e fica disponível no acervo.

### 6.2 Editar receita

1. O usuário abre uma receita existente.
2. Ajusta título, origem, história, ingredientes ou etapas.
3. Salva a versão editada sem alterar o texto ou a imagem originais.

### 6.3 Consultar receita

1. O usuário visualiza o acervo do usuário demo.
2. Seleciona uma receita.
3. Consulta dados estruturados, história, texto original e imagem original.

### 6.4 Gerar lista de compras

1. O usuário seleciona uma ou mais receitas.
2. O serviço coleta os ingredientes salvos.
3. Itens compatíveis podem ser agrupados de forma simples e transparente.
4. A lista é apresentada para conferência e marcação manual.

## 7. Fluxos técnicos

### Requisição web

`router -> schema Pydantic -> service -> repository/model -> template ou
resposta HTMX`.

Erros de validação e falhas de persistência devem ser tratados explicitamente,
com mensagens úteis para o usuário e sem ocultar a causa técnica nos logs locais.

### Importação

`upload/texto -> validação e armazenamento original -> processor mock ->
resultado sugerido -> revisão humana -> persistência estruturada`.

O processor não deve sobrescrever fontes originais. A troca futura do mock por
OCR ou IA real deve exigir apenas uma implementação compatível com o contrato,
sem alterar o fluxo de revisão.

### Persistência

O banco padrão é SQLite em `data/app.db`. A camada de configuração deve aceitar
uma `DATABASE_URL` para futura migração a PostgreSQL, mas essa possibilidade não
deve adicionar dependência operacional ao MVP local.

## 8. Decisões arquiteturais

1. **Monólito modular:** reduz custo cognitivo e operacional para uma equipe
   enxuta, mantendo separação suficiente para evoluir.
2. **Server-side rendering:** Jinja2 e HTML simplificam o MVP; HTMX entra apenas
   onde reduzir recarregamentos e complexidade.
3. **SQLite local:** atende o uso individual/local e elimina infraestrutura.
4. **Uploads em filesystem:** mantém a imagem original acessível e evita storage
   externo obrigatório.
5. **Fontes e sugestões separadas:** preserva auditabilidade e permite correção
   humana da extração.
6. **Mocks por padrão:** IA/OCR reais são opcionais e não bloqueiam testes nem
   execução sem chaves externas.
7. **Usuário demo:** permite testar o conceito sem antecipar decisões de
   autenticação e multiusuário.
8. **Configuração por ambiente:** mantém defaults locais e reserva
   `DATABASE_URL` para evolução, sem abandonar o SQLite como padrão.

## 9. Stack local recomendada

- Python 3.14;
- FastAPI e servidor ASGI compatível;
- SQLAlchemy 2.x com SQLite;
- Pydantic v2 e configuração correspondente;
- Jinja2;
- HTMX via CDN, somente nos pontos necessários;
- Tailwind CSS via CDN;
- pytest;
- filesystem local para `uploads/`;
- SQLite em `data/app.db`.

Não haverá Docker, PostgreSQL obrigatório, chave de API, storage externo ou
pipeline de frontend obrigatório.

## 10. O que fica fora do MVP

- autenticação real, cadastro e múltiplos perfis;
- PostgreSQL como requisito de execução;
- deploy, Docker e infraestrutura de produção;
- OCR ou IA real obrigatórios;
- RAG, embeddings, busca semântica e base vetorial;
- sincronização em nuvem e storage externo;
- planejamento avançado, preços, estoque e integração com mercados;
- aplicativo mobile ou SPA;
- edição avançada de imagens;
- colaboração e compartilhamento entre usuários.

## 11. Riscos e mitigação

| Risco | Mitigação no MVP |
|---|---|
| Extração automática incorreta | mock determinístico, aviso explícito e revisão humana obrigatória |
| Upload inválido ou caminho inseguro | validar tipo/tamanho, gerar nome interno seguro e armazenar caminho relativo |
| Perda da fonte original | persistir texto e imagem originais separadamente dos dados estruturados |
| Crescimento prematuro da arquitetura | monólito modular, contratos pequenos e poucos casos de uso |
| Divergência entre banco e arquivo | salvar metadados junto da receita e tratar falhas de armazenamento explicitamente |
| SQLite inadequado para muitos usuários | manter `DATABASE_URL` como ponto de migração futura, sem fazer PostgreSQL obrigatório |
| Dependência acidental de serviço externo | mocks e defaults locais executáveis sem chaves |
| Interface complexa demais | Jinja2, Tailwind CDN e HTMX apenas quando agregarem simplicidade |

## 12. Evoluções futuras

1. Substituir processors mockados por adaptadores de OCR e IA reais, mantendo a
   revisão humana e os contratos internos.
2. Adicionar autenticação e isolamento real por usuário.
3. Migrar para PostgreSQL configurando `DATABASE_URL` e introduzindo migrações
   formais quando o uso justificar.
4. Migrar imagens para storage externo quando houver necessidade operacional.
5. Adicionar busca textual e, posteriormente, RAG sem contaminar o núcleo do
   MVP.
6. Evoluir a lista de compras com categorias, quantidades consolidadas e estado
   persistente mais rico.
7. Criar interfaces mobile ou offline somente após validação do fluxo web.

## 13. Backlog técnico priorizado

### P0 — necessário para o primeiro fluxo validável

- criar a estrutura modular FastAPI e configuração Python 3.14;
- configurar SQLite em `data/app.db` e SQLAlchemy;
- modelar receita, ingredientes, etapas e imagem original;
- implementar criação/edição/consulta com Jinja2;
- implementar armazenamento seguro de uploads em `uploads/`;
- implementar processor mockado de importação e tela de revisão;
- adicionar usuário demo;
- adicionar testes pytest dos casos de uso e persistência;
- documentar execução e testes no README.

### P1 — completar a validação do MVP

- registrar origem e história da receita;
- gerar lista de compras simples;
- adicionar interações HTMX pontuais, se reduzirem complexidade;
- melhorar mensagens de erro e validação de uploads;
- revisar o fluxo completo com usuários reais.

### P2 — preparação para evolução

- formalizar contratos de processors para integrações reais;
- avaliar migrações de banco e compatibilidade com PostgreSQL via
  `DATABASE_URL`;
- avaliar busca, autenticação, storage externo e RAG conforme evidências do
  piloto.

## Compatibilidade com AGENTS.md

Esta proposta foi conferida contra as instruções permanentes do projeto:

- usa Python 3.14 e a stack obrigatória FastAPI, SQLite, SQLAlchemy, Pydantic v2,
  Jinja2, HTMX, Tailwind via CDN e pytest;
- mantém execução exclusivamente local, sem Docker, PostgreSQL, storage,
  chaves externas, IA real ou OCR real obrigatórios;
- fixa `data/app.db` e `uploads/` como destinos locais;
- preserva texto e imagem originais e exige edição humana dos dados extraídos;
- mantém a incerteza da estruturação automática visível ao usuário;
- limita a lista de compras ao escopo simples do MVP;
- separa rotas, schemas, modelos, serviços, processors e persistência;
- prevê testes, README atualizado, segurança básica e ciclos incrementais;
- não introduz código de aplicação nesta etapa.

Não foi identificada incompatibilidade com o `AGENTS.md`. A aceitação desta
arquitetura não autoriza implementar funcionalidades nesta etapa; ela apenas
estabelece a base para os próximos ciclos.
