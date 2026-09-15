# Prompt 8 — Segurança, privacidade e cuidados mínimos no ambiente local

## C — Contexto

O MVP “Livro Vivo de Receitas” lida com dados pessoais e familiares, incluindo receitas privadas, imagens de cadernos, nomes de familiares, histórias afetivas e possivelmente informações sobre hábitos alimentares.

Mesmo sendo um MVP local, a aplicação deve nascer com práticas mínimas de privacidade, segurança e governança de IA.

Não usaremos autenticação real na primeira versão, mas haverá usuário demo. Também não usaremos APIs externas obrigatórias no início.

## O — Objetivo

Revise e implemente requisitos mínimos de segurança, privacidade e proteção de dados compatíveis com MVP local.

## S — Estilo

Atue como especialista em segurança de aplicações web, privacidade e IA responsável.

## T — Tom

Cauteloso, técnico e objetivo.

## A — Audiência

Equipe técnica e Product Owner responsáveis por preparar o MVP para testes com usuários reais.

## R — Resposta esperada

Entregue:

1. checklist de riscos;
2. recomendações de segurança para MVP local;
3. ajustes no código;
4. texto simples de aviso de privacidade para usuários testadores;
5. termo simples de consentimento para teste;
6. controles de upload;
7. controles mínimos de acesso;
8. logs mínimos;
9. política simples de retenção e exclusão de dados;
10. recomendações específicas para uso futuro de IA/OCR real.

Critérios obrigatórios:

* não usar Docker;
* não versionar banco local;
* não versionar uploads;
* não versionar `.env`;
* incluir `.gitignore` adequado;
* limitar tamanho de upload;
* validar tipo de arquivo;
* bloquear upload de arquivos executáveis;
* armazenar uploads fora da pasta pública direta;
* servir imagens por endpoint controlado;
* não registrar dados sensíveis em logs;
* permitir exclusão de receitas e imagens;
* deixar claro que IA/OCR pode errar;
* preservar imagem original para conferência;
* não usar dados reais de teste para treinar modelos sem consentimento explícito;
* incluir aviso de confidencialidade para receitas familiares.