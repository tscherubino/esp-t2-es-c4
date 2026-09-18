# Estratégia de testes e critérios de aceite

## Estratégia

A suíte usa pytest e é executada somente com Python 3.14. A fixture
`tests/conftest.py` configura um SQLite temporário e um diretório temporário de
uploads antes da importação da aplicação. Assim, nenhum teste altera
`data/app.db` ou `uploads/` do desenvolvedor.

Os testes são divididos em camadas pequenas:

- unitários: parser/OCR mockado, consolidação de ingredientes e armazenamento;
- integração: rotas FastAPI, persistência SQLAlchemy e fluxos ponta a ponta;
- segurança: whitelist, tamanho, assinatura de arquivo e proteção de caminho;
- regressão: health check, inicialização das tabelas e navegação essencial.

Não há dependência de Docker, PostgreSQL, API externa, OCR real ou LLM real.

## Inventário funcional atual

1. Página inicial e health check.
2. Cadastro manual de receita com título, porções, tempo, ingredientes, preparo,
   tags, origem/história e imagem opcional.
3. Consulta, edição e exclusão de receitas, incluindo imagem controlada.
4. Importação assistida por texto, imagem ou transcrição manual, com providers
   locais e revisão antes da persistência.
5. Preservação de texto e imagem originais da importação.
6. Lista de compras a partir de uma ou várias receitas.
7. Consolidação por nome e unidade, edição, conclusão, remoção, adição manual,
   exclusão de listas e cópia como texto.
8. Proteções locais de upload, dados ignorados no Git e avisos de privacidade.

## Matriz de critérios de aceite

| Funcionalidade | Critério | Cobertura |
|---|---|---|
| Disponibilidade | `/` e `/health` respondem corretamente | `tests/test_app.py` |
| Banco | tabelas do domínio são criadas | `tests/test_db.py` |
| Cadastro manual | criar, consultar, editar e excluir receita | `tests/test_manual_flow.py`, `tests/test_critical_regressions.py` |
| Upload válido | imagem permitida é salva com nome seguro | `tests/test_security.py` |
| Upload inválido | tipo, assinatura e tamanho inválidos são rejeitados | `tests/test_security.py` |
| Importação | texto/imagem são analisados e aguardam revisão | `tests/test_import.py` |
| Fontes originais | texto e imagem permanecem preservados | `tests/test_import.py`, `tests/test_manual_flow.py` |
| Estruturação | ingredientes, etapas, confiança e avisos são gerados | `tests/test_import.py` |
| Lista de compras | uma ou várias receitas geram itens consolidados | `tests/test_shopping.py` |
| Itens e listas | editar, marcar, remover, adicionar, excluir lista e copiar como texto | `tests/test_shopping.py` |
| Segurança | exclusão não atravessa o diretório de uploads | `tests/test_security.py` |
| Regressões P1 | upload inválido, limite, falha amigável e exclusão completa | `tests/test_critical_regressions.py` |

## Execução

Com o ambiente virtual ativado:

```bash
pytest
```

Os avisos de depreciação exibidos atualmente vêm das versões de Starlette,
httpx e AnyIO usadas pelo TestClient; não representam falhas funcionais do
projeto.

## Cobertura unitária e de API

Os testes unitários dos services verificam os componentes isoladamente, sem
depender da renderização HTML:

- criação, atualização, limpeza de valores e exclusão de receitas;
- criação, edição, marcação e exclusão de itens/listas de compras;
- consolidação de quantidades decimais e entradas vazias;
- salvamento e remoção de imagens válidas;
- injeção de providers locais no serviço de importação;
- factories dos providers padrão.

Os testes de API cobrem respostas `404` para recursos inexistentes, `422` para
campos ausentes, vazios ou com tipos inválidos, `400` para fontes inválidas de
importação e payloads sem receitas ou com identificadores desconhecidos.

Os casos de edge case incluem banco/catálogo vazio, receita sem imagem,
quantidades com vírgula decimal, listas sem receitas e receitas com mais de
cinco ingredientes ou etapas.

## Documentação dos testes adicionados

### `tests/test_services_unit.py`

Testa os services individualmente, usando uma sessão SQLite isolada e
providers locais controlados:

| Grupo | Cenários cobertos |
|---|---|
| Receitas | normalização de valores, criação, atualização dos ingredientes e etapas, tags e exclusão |
| Lista de compras | ciclo de vida da lista e dos itens, edição, marcação e exclusão |
| Edge cases | lista sem receitas, quantidades decimais com vírgula e ingredientes consolidados |
| Armazenamento | salvamento de PNG válido com nome gerado e remoção do arquivo |
| Importação | injeção de OCR/parser locais, análise, revisão e finalização da receita |
| Factories | seleção dos providers locais padrão, sem dependência de serviços externos |

### `tests/test_api_errors.py`

Testa o contrato HTTP dos principais endpoints:

- recursos inexistentes retornam `404` para receitas, imagens, jobs de
  importação, listas e itens de compras;
- payloads ausentes, vazios ou com tipos inválidos retornam `422` quando a
  validação do formulário é aplicável;
- solicitações de importação sem fonte retornam `400` com detalhe legível;
- geração de lista sem receitas ou com identificador desconhecido produz uma
  resposta controlada, sem exceção não tratada;
- a API de consulta de receita preserva um payload mínimo estável, inclusive
  para receita sem ingredientes.

A fixture `tmp_path` definida em `tests/conftest.py` cria diretórios
temporários dentro do ambiente isolado da suíte. Isso evita a dependência de
pastas temporárias globais do Windows que podem estar inacessíveis por
permissões e garante que os testes de upload e exclusão não alterem os dados
locais do desenvolvedor.

## Resultado atual

```text
40 passed, 2 warnings
```

Os testes adicionais estão em `tests/test_services_unit.py` e
`tests/test_api_errors.py`.
