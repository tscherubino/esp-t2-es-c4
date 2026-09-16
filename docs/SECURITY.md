# Segurança, privacidade e uso responsável

## Escopo

O Livro Vivo de Receitas é um MVP local para validação com usuários. Os
controles abaixo são proporcionais a esse contexto; não substituem
autenticação, hardening de servidor ou uma avaliação de produção.

## Checklist implementado

- Uploads aceitam somente JPEG, PNG e WebP.
- O limite de cada imagem é de 5 MB e a leitura é interrompida nesse limite.
- O `Content-Type` precisa ser compatível com a assinatura binária básica do
  arquivo; arquivos executáveis renomeados não são aceitos.
- O nome original nunca é usado como caminho. O armazenamento usa UUID e
  extensão definida pela whitelist.
- Imagens ficam em `uploads/`, fora de uma pasta pública direta, e só são
  servidas pelo endpoint controlado da receita pertencente ao usuário demo.
- A exclusão de uma receita remove suas imagens locais associadas.
- O banco, uploads e arquivos `.env` são ignorados pelo Git.
- Falhas de importação registram somente tipo de evento e tipo da exceção, sem
  texto original, nomes de família ou outros dados da receita.
- As páginas informam que a aplicação é local e que a estruturação assistiva
  pode conter erros.

Os controles de upload são exercitados por testes pytest para tipo permitido,
assinatura incompatível, arquivo executável renomeado, tamanho excedido e
tentativa de exclusão fora de `uploads/`. A validação de assinatura é
intencionalmente básica e não equivale a antivírus ou análise completa do
formato.

## Arquivos e dados locais

`data/app.db` e o conteúdo de `uploads/` são dados privados do ambiente local e
não devem ser commitados. O `.env` pode conter configuração local e também não
deve ser versionado; o único arquivo de exemplo permitido é `.env.example`.

Para excluir os dados de teste, pare a aplicação e remova o banco local e os
arquivos de upload do ambiente de desenvolvimento. A exclusão é permanente,
portanto faça uma cópia somente se o usuário tiver autorizado a preservação.

## Aviso de privacidade para testadores

> Esta versão funciona somente no computador de teste. As receitas, imagens,
> histórias e listas inseridas ficam armazenadas localmente para validar o
> produto. Não inclua informações de terceiros sem autorização e não use dados
> reais de família que você não esteja autorizado a compartilhar. Os dados não
> são enviados para APIs externas nem usados para treinar modelos.

## Consentimento simples para teste

> Eu entendo que este é um protótipo local e autorizo o uso das receitas,
> imagens e histórias que eu inserir para avaliação da experiência do produto.
> Posso interromper o teste e solicitar a exclusão dos dados locais a qualquer
> momento. Não estou autorizando o uso desses dados para treinamento de modelos
> ou compartilhamento com terceiros.

## IA e OCR futuros

- Manter a revisão humana obrigatória antes de persistir dados estruturados.
- Não enviar texto, imagens ou histórias para serviços externos sem informar a
  finalidade e obter consentimento explícito.
- Nunca usar dados reais de teste para treinamento sem autorização específica.
- Minimizar dados enviados, registrar fornecedor e finalidade e oferecer uma
  alternativa local quando possível.
- Não registrar prompts, imagens ou respostas completas em logs por padrão.
- Preservar a fonte original e identificar claramente qualquer resultado como
  sugestão assistiva, não como fato garantido.
