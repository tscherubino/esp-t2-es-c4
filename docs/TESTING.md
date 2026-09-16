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
