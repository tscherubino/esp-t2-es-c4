# Livro Vivo de Receitas

MVP local executado com Python 3.14, FastAPI e SQLite. O fluxo manual de
receitas já permite cadastrar, consultar, editar e excluir receitas com
ingredientes, preparo, tags, história/origem e imagem opcional.

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

## Fluxo manual de receitas

1. Acesse <http://127.0.0.1:8000/recipes>.
2. Clique em **Nova receita**.
3. Preencha título, porções, tempo, ingredientes, preparo, tags, história/origem
   e, opcionalmente, uma imagem JPEG, PNG ou WebP de até 5 MB.
4. Salve para consultar a página de detalhe.
5. Use **Editar** ou **Excluir** na página da receita.

Também estão disponíveis `/api/recipes` e `/api/recipes/{public_id}` como
endpoints JSON iniciais. A rota `/recipes/import` preserva texto e imagem e
cria uma importação pendente; IA e OCR ainda não são executados.

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

- a importação ainda não estrutura automaticamente o conteúdo;
- não há OCR ou IA real;
- não há autenticação real;
- não há lista de compras;
- Tailwind é carregado via CDN e, portanto, requer rede apenas para os estilos
  no navegador; a aplicação e o banco continuam locais.
