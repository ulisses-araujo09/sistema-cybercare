# CyberCare — implantação e operação

## Endereços

- Aplicativo/PWA: https://cybercare-web-production.up.railway.app
- Saúde da API: https://cybercare-api-production.up.railway.app/api/health
- Documentação da API: https://cybercare-api-production.up.railway.app/docs
- Repositório oficial: https://github.com/ulisses-araujo09/sistema-cybercare
- Cópia sincronizada: https://github.com/ulissesoliveiraa/CYBERCARE

## Configuração aplicada

O projeto Railway **CyberCare**, ambiente `production`, contém `cybercare-api` e `cybercare-web`, com uma réplica por serviço. As pastas são `/backend` e `/frontend`, os builds usam Dockerfiles e os domínios gerados usam HTTPS. O banco é o projeto **Cybercare** já criado pelo responsável no Neon, branch `production` e banco `neondb`, com conexão TLS.

A API valida o ambiente, aplica Alembic e inicia o FastAPI. A carga inicial criou 50 casos fictícios, cinco perguntas e duas contas. Depois da primeira carga, `SEED_DEMO=false` evita novas execuções automáticas do seed. Os testes acrescentaram alguns casos exclusivamente fictícios.

Senhas e chave JWT foram geradas aleatoriamente para a hospedagem. A URL do banco permanece no Railway; nenhum desses valores foi incluído nos repositórios. As senhas das contas locais não são as mesmas da hospedagem. O responsável encontra os acessos hospedados no arquivo local privado `tmp/deploy/acessos-hospedagem.txt`; esse arquivo é ignorado pelo Git.

As contas são `socioemocional@demo.cybercare.local` e `gestao@demo.cybercare.local`. Seus perfis são isolados no backend. Não há cadastro público de contas.

## Verificações executadas

- Builds Docker e health checks dos dois serviços aprovados no Railway.
- Conexão PostgreSQL Neon real, migrações e persistência confirmadas.
- Doze testes de navegador na hospedagem: computador e celular, fluxo vertical, quiz, filtros, erros, acessibilidade automática e PWA.
- Instalação PWA sem erros nos critérios do Chromium; ícones e manifest conferidos.
- Cache sem respostas da API, páginas privadas, relatos, chaves, senhas ou sessões; fallback offline educativo.
- Dez testes de backend aprovados após os ajustes de manutenção.

## Operação

`MAINTENANCE_ENABLED=true` executa a limpeza de retenção ao iniciar a API e a cada hora, sem criar um terceiro serviço. Registros fictícios expiram após `RETENTION_DAYS=30`. O comando `python -m app.retention` também pode ser executado manualmente. Enquanto a API estiver parada, a limpeza física aguarda a próxima execução, mas as consultas não exibem registros expirados.

Os access logs da API e do Nginx estão desativados. Falhas de manutenção usam mensagem genérica, sem parâmetros SQL, URL do banco ou conteúdo de relatos. Instrumentação automática de conteúdo não foi habilitada.

A infraestrutura está em `.railway/railway.ts`, com variáveis `unmanaged` para preservar os segredos no Railway. Após mudanças autorizadas: revisar, testar, criar o commit, executar `scripts/publicar.ps1` para os dois repositórios e implantar um snapshot limpo desse commit.

A primeira implantação foi feita via CLI. **Autodeploy por push GitHub ainda não está conectado:** a conta Railway não tinha repositórios autorizados no GitHub App. Essa ligação pode ser habilitada depois, exclusivamente para o repositório oficial, preservando as pastas dos serviços. A sincronização dos dois repositórios Git é independente disso.

## Limites mantidos

Ambiente exclusivamente demonstrativo. Não usar dados reais de estudantes. Anexos, notificações automáticas, chatbot, certificados e recuperação de chave permanecem fora do MVP. Contatos institucionais e governança para qualquer uso real dependem do responsável pela escola. Nenhum plano pago foi contratado ou alterado nesta implantação.
