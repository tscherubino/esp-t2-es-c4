# Checklist de submissão — Livro Vivo de Receitas

**Data da auditoria:** 17/09/2026  
**Versão avaliada:** MVP local na branch `feature/checklist-submissao`  
**Base de referência:** checklist fornecido para a submissão do projeto.

## Resultado executivo

O projeto atende aos requisitos funcionais e documentais principais do
checklist. O README foi complementado com a relação consolidada de tecnologias,
providers locais de IA/OCR e assistente de código. Também foram adicionados
créditos explícitos e a licença MIT em `LICENSE`.

| Item | Resultado | Evidência |
|---|---|---|
| README detalhado | **Atende** | `README.md` |
| Configuração e execução local | **Atende** | Seções Instalação e Execução do README |
| Exemplos de uso e interação com a aplicação/API | **Atende** | Fluxos manual, importação, lista de compras e endpoints documentados |
| Tecnologias, modelos e assistentes | **Atende** | Seção “Tecnologias, modelos e assistentes” do README |
| Limitações e próximos passos | **Atende** | Seção de limitações e `docs/ARCHITECTURE.md` |
| Créditos e licença | **Atende** | Seção de créditos e arquivo `LICENSE` |
| Gerenciamento de dependências | **Atende** | `requirements.txt` |
| Testes automatizados | **Atende** | `tests/` e `docs/TESTING.md` |
| Release ou tag | **Pendente operacional** | Nenhuma tag/release foi criada nesta auditoria |

## 1. README detalhado

**Status: Atende.**

O `README.md` contém título, descrição, stack técnica, requisitos, criação e
ativação do ambiente Python 3.14, instalação, configuração opcional via
`.env.example`, inicialização do SQLite, execução com Uvicorn, navegação,
fluxos manual e assistido, lista de compras, exemplos de API, segurança,
testes, providers, evolução futura, limitações, créditos e licença.

## 2. Configuração, execução e uso

**Status: Atende.**

As instruções principais são compatíveis com Windows 10/11 e Python 3.14:

```powershell
py -3.14 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
pytest
```

O README também apresenta a alternativa de ativação do PowerShell e comandos
equivalentes para Linux/macOS. Os exemplos cobrem `/`, `/health`, receitas,
importação e lista de compras.

## 3. Tecnologias, modelos e assistentes

**Status: Atende.**

O projeto lista FastAPI, Uvicorn, SQLite, SQLAlchemy, Pydantic v2, Jinja2,
Tailwind CSS via CDN e pytest. Também identifica os providers locais
`MockOCRProvider`, `ManualTranscriptionOCRProvider`, `RuleBasedRecipeParser` e
`MockLLMRecipeParser`.

Não existe modelo de IA real obrigatório nem integração externa. O README
registra o OpenAI Codex como assistente de código utilizado no desenvolvimento,
sem torná-lo uma dependência de execução.

## 4. Limitações e próximos passos

**Status: Atende.**

Estão documentadas a ausência de OCR e IA real, a ausência de autenticação real,
a falta de conversões complexas de unidades, a dependência de CDN para o
Tailwind e o escopo local de MVP. Os próximos passos arquiteturais estão em
`docs/ARCHITECTURE.md`.

## 5. Créditos e licença

**Status: Atende.**

Foi adicionado o arquivo `LICENSE` com a licença MIT e uma seção de créditos no
README, identificando o autor do projeto e o uso do OpenAI Codex como assistente
de desenvolvimento.

## 6. Dependências

**Status: Atende.**

`requirements.txt` lista FastAPI, Uvicorn, SQLAlchemy, Pydantic, Pydantic
Settings, Jinja2, python-multipart, pytest e httpx. Não há serviços externos ou
infraestrutura empresarial obrigatória.

## 7. Testes automatizados

**Status: Atende.**

A suíte cobre endpoints básicos, banco, cadastro e exclusão de receitas,
imagens, importação assistida, revisão humana, providers locais, lista de
compras, segurança e regressões críticas.

Resultado da última execução:

```text
25 passed, 2 warnings
```

Os avisos são depreciações emitidas pelas dependências de teste e não indicam
falhas funcionais do projeto.

## 8. Release ou tag

**Status: Pendente operacional.**

O histórico possui commits organizados em Conventional Commits e a branch foi
integrada à `main`, mas não havia uma tag ou Release GitHub criada no momento da
auditoria. Recomenda-se publicar uma Release `v0.1.0` baseada no commit de
merge desta entrega.

## 9. Conclusão

Com os ajustes realizados, o projeto está documentalmente preparado para a
submissão. A única atividade restante é operacional: criar e publicar a tag ou
Release `v0.1.0` no GitHub, caso esse requisito seja obrigatório para a
avaliação.
