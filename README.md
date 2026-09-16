# Livro Vivo de Receitas

Estrutura inicial do MVP local, executada com Python 3.14, FastAPI e SQLite.
Nesta etapa existem apenas a página inicial, o health check, a configuração
básica de banco e os diretórios locais. Modelos de receitas, ingredientes e
lista de compras serão implementados em ciclos posteriores.

## Requisitos

- Python 3.14;
- `pip` atualizado;
- nenhum serviço externo, Docker ou chave de API.

## Instalação

### Windows PowerShell

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

### Linux/macOS

```bash
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

O arquivo `.env` é opcional. Sem ele, a aplicação usa SQLite em
`data/app.db` e uploads em `uploads/`. Os valores podem ser alterados por
variáveis de ambiente, especialmente `DATABASE_URL` para uma evolução futura.

## Banco de dados

As tabelas do modelo inicial são criadas automaticamente na inicialização da
aplicação. Esta etapa ainda não usa Alembic. Para resetar o banco durante o
desenvolvimento, pare a aplicação e remova somente o arquivo local:

```powershell
Remove-Item data/app.db
```

No Linux/macOS:

```bash
rm data/app.db
```

Na próxima execução, o SQLite será recriado com as tabelas declaradas pelos
modelos atuais.

O modelo inicial contém as tabelas `users`, `recipes`, `recipe_images`,
`ingredients`, `preparation_steps`, `tags`, `recipe_tags`, `shopping_lists`,
`shopping_list_items` e `import_jobs`.

## Execução

Com o ambiente virtual ativado:

```bash
uvicorn app.main:app --reload
```

Abra <http://127.0.0.1:8000/> no navegador.

## Verificação

Página inicial:

```bash
curl http://127.0.0.1:8000/
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Resposta esperada do health check:

```json
{"status":"ok"}
```

## Testes

```bash
pytest
```

## Limitações desta etapa

- não há páginas CRUD ou serviços de receitas;
- não há importação, OCR ou IA;
- não há autenticação real;
- não há lista de compras;
- Tailwind é carregado via CDN e, portanto, requer rede apenas para os estilos
  no navegador; a aplicação e o banco continuam locais.
