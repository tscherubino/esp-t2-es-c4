# Livro Vivo de Receitas

MVP local executado com Python 3.14, FastAPI e SQLite. O fluxo manual de
receitas já permite cadastrar, consultar, editar e excluir receitas com
ingredientes, preparo, tags, história/origem e imagem opcional.

## Documentação arquitetural

- [Arquitetura aprovada](docs/ARCHITECTURE.md): decisões, camadas, modelo de
  domínio e backlog técnico.
- [Diagramas arquiteturais](docs/ARCHITECTURE_DIAGRAMS.md): visões Mermaid do
  estado implementado após o Prompt 7, incluindo receitas, importação assistida
  e lista de compras.
- [Segurança e privacidade](docs/SECURITY.md): controles do MVP, aviso para
  testadores, consentimento e orientações para IA/OCR futuros.

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

### Navegação da interface

A navegação principal está disponível em todas as telas e oferece acesso a
Início, Receitas, Importar, Lista de compras e Nova receita. A interface foi
organizada para telas pequenas, com foco visível para teclado, labels nos
campos, mensagens de erro acessíveis e um link para pular diretamente ao
conteúdo.

## Fluxo manual de receitas

1. Acesse <http://127.0.0.1:8000/recipes>.
2. Clique em **Nova receita**.
3. Preencha título, porções, tempo, ingredientes, preparo, tags, história/origem
   e, opcionalmente, uma imagem JPEG, PNG ou WebP de até 5 MB.
4. Salve para consultar a página de detalhe.
5. Use **Editar** ou **Excluir** na página da receita.

Também estão disponíveis `/api/recipes` e `/api/recipes/{public_id}` como
endpoints JSON iniciais.

## Importação assistida

O Fluxo B é separado do cadastro manual (Fluxo A):

1. Acesse <http://127.0.0.1:8000/recipes/import>.
2. Envie texto, imagem/print ou uma transcrição manual da imagem.
3. A aplicação preserva as fontes, executa a análise local e abre uma tela de
   revisão antes de criar a receita.
4. Revise e edite título, porções, tempo, ingredientes, preparo, tags e origem.
5. Confirme para criar a receita definitivamente.

O Fluxo A continua disponível em `/recipes/new` e grava a receita diretamente
após o envio do formulário. No Fluxo B, o envio cria apenas uma análise
temporária (`ImportJob`); nenhuma receita definitiva é criada antes da
confirmação na tela de revisão. Para imagens sem OCR real, informe a
transcrição manual no campo indicado antes de analisar.

Os providers são locais e substituíveis: `MockOCRProvider`,
`ManualTranscriptionOCRProvider`, `MockLLMRecipeParser` e
`RuleBasedRecipeParser`. O padrão usa `RuleBasedRecipeParser` e
`MockOCRProvider`; podem ser selecionados por `IMPORT_PARSER` e
`IMPORT_OCR_PROVIDER`. Nenhuma API externa, chave ou OCR real é necessária.

Para análise estruturada via API, use `POST /api/recipes/import/analyze` com
`multipart/form-data`. A resposta contém o `ImportJob`, o texto analisado, os
campos estruturados, avisos e os `confidence_score`s. A receita não é salva
definitivamente até a revisão humana.

## Lista de compras

1. Acesse <http://127.0.0.1:8000/shopping-list>.
2. Selecione uma ou mais receitas e informe o nome da lista.
3. Gere a lista para consolidar ingredientes com mesmo nome e unidade.
4. Edite, marque como comprado, remova ou adicione itens manualmente.
5. Use **Copiar lista** ou **Abrir como texto** para levar a lista ao celular.

Também é possível gerar uma lista diretamente pelo botão **Gerar lista de
compras** na página de uma receita. Quantidades numéricas são somadas apenas
quando a unidade é igual; conversões entre unidades não são realizadas. Itens
com observações são mantidos com suas observações.

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

## Segurança e privacidade

O MVP valida extensões e assinaturas básicas de imagens, limita uploads a 5 MB,
usa nomes internos aleatórios, mantém arquivos fora de acesso público direto e
os serve somente por endpoint controlado. O banco, uploads e `.env` são dados
locais ignorados pelo Git. Consulte [docs/SECURITY.md](docs/SECURITY.md) antes
de usar dados de receitas familiares em testes.

## Testes

```bash
pytest
```

Os testes cobrem os três fluxos principais: cadastro manual completo,
importação local com análise e revisão, e lista de compras. Também verificam os
controles mínimos de upload e proteção dos dados locais.

## Limitações desta etapa

- a importação usa somente providers locais mockados ou baseados em regras;
- não há OCR ou IA real;
- não há autenticação real;
  - a lista de compras não realiza conversões complexas de unidades;
- Tailwind é carregado via CDN e, portanto, requer rede apenas para os estilos
  no navegador; a aplicação e o banco continuam locais.
