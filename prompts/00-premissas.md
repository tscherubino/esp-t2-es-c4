# Pacote de Prompts CO-STAR — MVP Local “Livro Vivo de Receitas”

## Premissas gerais do MVP local

O produto é uma aplicação web em Python para organizar receitas culinárias pessoais e familiares. A primeira versão deve testar cinco capacidades centrais:

1. importar receita por texto, foto ou print;
2. organizar automaticamente ingredientes e modo de preparo;
3. salvar imagem original;
4. adicionar origem/história da receita;
5. gerar lista de compras simples.

A aplicação deverá ser desenvolvida e testada com Python 3.14, utilizando versões atuais das dependências com suporte declarado ou comprovado a essa versão. Utilizar exclusivamente Pydantic v2 e SQLAlchemy 2.x. Não utilizar bibliotecas ou padrões legados dependentes de Pydantic v1.

A stack simplificada será:

* Python 3.14;
* FastAPI atual;
* Uvicorn;
* Jinja2;
* HTMX;
* Tailwind CSS via CDN;
* SQLite local;
* SQLAlchemy 2.x;
* Pydantic v2;
* pydantic-settings ou python-dotenv;
* pytest;
* armazenamento local em `uploads/`;
* banco local em `data/app.db`;
* mocks para IA/OCR por padrão;
* execução local com ambiente virtual Python;
* sem Docker;
* sem PostgreSQL obrigatório;
* sem storage externo obrigatório;
* sem chaves externas obrigatórias.

A arquitetura deve permitir evolução futura para:

* PostgreSQL;
* pgvector;
* storage S3 compatível;
* OCR real;
* LLM real;
* RAG;
* autenticação real;
* deploy em ambiente de homologação/produção.
