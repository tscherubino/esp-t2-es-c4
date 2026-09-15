# AGENTS.md — Livro Vivo de Receitas

## Missão do projeto

Construir incrementalmente um MVP local e simples chamado **Livro Vivo de Receitas**.
O objetivo é validar com usuários reais cinco capacidades:

1. importar uma receita por texto, foto ou print;
2. organizar automaticamente ingredientes e modo de preparo;
3. salvar a imagem original;
4. registrar a origem e a história da receita;
5. gerar uma lista de compras simples.

O foco é um MVP funcional, testável e fácil de executar localmente. Evitar
overengineering e preservar a possibilidade de evolução após a validação.

## Stack e premissas técnicas obrigatórias

- Usar **Python 3.14**, que é a versão oficial do projeto.
- Usar FastAPI para a aplicação web.
- Usar SQLite local como banco de dados.
- Usar SQLAlchemy para persistência e acesso ao banco.
- Usar Pydantic v2 para validação e schemas.
- Usar Jinja2 para renderização de templates.
- Usar HTMX somente quando trouxer simplicidade clara ao fluxo.
- Usar Tailwind CSS via CDN; não introduzir pipeline frontend complexo no MVP.
- Usar pytest para testes.
- Manter o banco em `data/app.db`.
- Manter os uploads locais em `uploads/`.
- Executar exclusivamente de forma local, sem dependências obrigatórias de
  serviços externos.

## Restrições arquiteturais

- Não usar Docker.
- Não tornar PostgreSQL obrigatório.
- Não exigir storage externo.
- Não exigir chaves, contas ou serviços externos.
- Não tornar IA real obrigatória.
- Não tornar OCR real obrigatório.
- Usar mocks, stubs ou implementações determinísticas para IA/OCR durante o MVP.
- Organizar o código por camadas, mantendo separação razoável entre rotas,
  schemas, modelos, serviços e persistência.
- Preferir soluções explícitas e pequenas a abstrações genéricas prematuras.
- Manter a aplicação executável com configuração local mínima.

## Regras de domínio e preservação de dados

- Preservar sempre a imagem original importada, quando houver.
- Preservar sempre o texto original importado.
- Nunca substituir silenciosamente os dados originais pelos dados estruturados.
- Permitir edição humana dos ingredientes, do modo de preparo e dos demais
  dados extraídos.
- Informar claramente na interface e na documentação que a estruturação
  automática pode conter erros e deve ser revisada pelo usuário.
- A origem e a história da receita devem ser dados editáveis e associados à
  receita.
- A lista de compras deve ser simples, útil e derivada dos ingredientes salvos;
  não implementar planejamento avançado de compras no MVP.

## Padrões de desenvolvimento

- Trabalhar em ciclos incrementais pequenos.
- Cada ciclo deve entregar código funcional e testável, quando houver código a
  ser implementado.
- Antes de alterar o projeto, respeitar as decisões e convenções já existentes.
- Manter README atualizado com instalação, execução, testes e limitações.
- Adicionar testes pytest para comportamento relevante, especialmente regras de
  domínio, persistência e fluxos principais.
- Validar entradas com Pydantic e tratar erros de forma explícita.
- Manter nomes, módulos e responsabilidades claros; evitar arquivos monolíticos.
- Não adicionar dependências sem necessidade demonstrável para o MVP.
- Não esconder falhas de importação, persistência ou processamento automático.
- Considerar segurança básica mesmo em ambiente local: validar uploads, evitar
  confiar cegamente em nomes de arquivos e não expor segredos ou dados de
  configuração no repositório.

## Dados locais e versionamento

- O banco local `data/app.db` não deve ser versionado.
- O conteúdo de `uploads/` não deve ser versionado.
- Arquivos `.env` não devem ser versionados.
- Se forem necessários diretórios locais vazios, documentar a necessidade sem
  incluir dados reais ou arquivos gerados de usuário.
- Não gravar dados de receitas ou imagens fora dos diretórios locais definidos
  sem uma decisão explícita de mudança de escopo.

## Processo esperado para cada ciclo

Ao executar uma tarefa de implementação, a resposta deve, de forma direta:

1. explicar brevemente o que será implementado;
2. listar os arquivos criados ou alterados;
3. apresentar as alterações relevantes de forma completa e compreensível;
4. explicar como executar localmente;
5. explicar como testar;
6. apontar limitações conhecidas;
7. sugerir o próximo passo incremental.

Se a tarefa não pedir implementação, não criar funcionalidades por iniciativa
própria. Mudanças devem permanecer dentro do escopo do MVP e preservar sua
execução exclusivamente local.

## Critério geral de aceitação

Uma entrega é aceitável quando é simples de compreender, funciona localmente
com Python 3.14, possui testes proporcionais ao risco, mantém os dados originais
da receita, permite revisão humana da estruturação e não transforma integrações
opcionais (IA, OCR, serviços externos ou infraestrutura) em requisitos do MVP.
