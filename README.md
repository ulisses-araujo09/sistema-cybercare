# CyberCare — MVP funcional de demonstração

Sistema educacional em português brasileiro para prevenção e acompanhamento de bullying e cyberbullying. Frontend React web + Vite + TypeScript + Tailwind CSS; API FastAPI + SQLAlchemy + Alembic; PostgreSQL no Neon; dois serviços preparados para Railway.

**Repositório oficial:** [ulisses-araujo09/sistema-cybercare](https://github.com/ulisses-araujo09/sistema-cybercare). **Cópia sincronizada:** [ulissesoliveiraa/CYBERCARE](https://github.com/ulissesoliveiraa/CYBERCARE).

**Aplicativo hospedado:** https://cybercare-web-production.up.railway.app • **API:** https://cybercare-api-production.up.railway.app/api/health

**Somente dados fictícios. Não utilizar para denúncias reais.** O servidor recusa inicialização com `DEMO_MODE=false`. Essa proteção identifica o ambiente; não detecta automaticamente se um texto contém informações reais. Nenhum usuário deve inserir dados de estudantes.

## Entregas

- Início, denúncia anônima com identificação fictícia opcional, protocolo e chave privada, acompanhamento, apoio, quiz, sobre e login.
- Persistência real, histórico de status, paginação, filtros, notas internas e auditoria sem conteúdo de relatos.
- Setor socioemocional acessa casos. Gestão acessa exclusivamente faixas agregadas, com supressão de grupos pequenos.
- Chave criptograficamente aleatória mostrada apenas após envio, armazenada como SHA-256. Protocolo separado com 96 bits aleatórios; chave com 256 bits.
- Senhas Argon2; JWT de 20 minutos, exclusivamente em memória no navegador; logout revoga o token no banco; RBAC validado em cada endpoint.
- Quiz de cinco perguntas persistidas no banco; resposta correta não vem no endpoint de perguntas. Validação pelo servidor, pontuação da rodada no navegador.
- Cores e composição derivadas do pôster: navegação verde, cabeçalho laranja, fundo creme, cartões azul, roxo e verde. Desktop amplo e mobile reorganizado.
- PWA com ícone próprio, manifest pt-BR, opção de instalação e página offline educativa. O cache nunca guarda respostas da API, relatos, credenciais ou chaves. Consulte `docs/PWA_E_PUBLICACAO.md`.

Os materiais originais estão preservados em `CyberCare_Codex/`. O pôster cita React Native e MySQL; a decisão atual solicitada é React web e PostgreSQL. A implementação não altera nem atribui resultados científicos ao resumo original.

## Executar no Windows

Requisitos: Python 3.12+, Node.js 22 e npm. A configuração de desenvolvimento oferece SQLite persistente para demonstração sem serviços externos. **SQLite é somente alternativa local; a hospedagem exige PostgreSQL.**

Na pasta do projeto:

```powershell
.\iniciar-demo.ps1
```

O script prepara dependências, gera segredos aleatórios em `backend/.env`, aplica migrações, carrega 50 casos fictícios e cinco perguntas e inicia os serviços locais. Não sobrescreve um `.env` existente. Requer conectividade apenas se precisar instalar dependências. Nesta entrega, dependências locais já estão instaladas em `.deps/` e `frontend/node_modules/`.

Abra **http://127.0.0.1:5173**. A API fica em **http://127.0.0.1:8000**, com documentação em `/docs`. As duas contas e senhas geradas ficam no arquivo local **`demo-acessos.txt`**, ignorado no versionamento. Não publique esse arquivo. Os e-mails fictícios são `socioemocional@demo.cybercare.local` e `gestao@demo.cybercare.local`.

O launcher usa o Python do runtime Codex quando instalado e as dependências locais disponíveis; em outra máquina, cria `.venv`. Processos de frontend/backend rodam ocultos, com logs sem acesso HTTP em `tmp/demo/`. Para encerrar os processos iniciados pelo launcher, use o Gerenciador de Tarefas com os IDs salvos em `tmp/demo/processos.txt`; se os serviços já estavam ativos, o launcher não os reinicia.

## Execução manual

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
cd backend
python -m app.bootstrap_demo
python -m alembic upgrade head
python -m app.seed
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --no-access-log --no-proxy-headers
```

Em outro terminal:

```powershell
cd frontend
npm ci
npm run dev
```

O proxy Vite encaminha `/api` à API local; `VITE_API_URL` fica vazio em desenvolvimento. Não use `app.bootstrap_demo` na hospedagem.

## PostgreSQL local

Para testar o mesmo mecanismo de banco da hospedagem com Docker:

```powershell
$env:POSTGRES_PASSWORD = 'defina-uma-senha-local-forte'
docker compose up -d db
```

Em `backend/.env`, defina `DATABASE_URL=postgresql+psycopg://cybercare:SENHA@localhost:5432/cybercare` (codifique caracteres especiais da senha na URL). Depois execute migração e seed conforme acima. O Docker Compose persiste o banco em volume e expõe a porta somente em loopback. Não executar `docker compose down -v` se quiser preservar os dados.

## Implantação Neon + Railway

A versão atual do Railway usa `.railway/railway.ts`; os antigos `railway.json` foram removidos por não serem aceitos em novos serviços. Instale a CLI oficial e execute `npm ci` na raiz para o SDK, `railway login`, `railway link`, `railway config plan` e, depois da revisão, `railway config apply`. A infraestrutura descreve os dois serviços, pastas e health checks e mantém as variáveis como `unmanaged`, somente no Railway.

1. Crie um projeto Neon dedicado a dados fictícios. Copie a URL de conexão da console com `sslmode=require`, preservando os parâmetros TLS. URLs `postgres://` e `postgresql://` são normalizadas para o driver psycopg pelo backend.
2. Envie o código para um repositório privado sem `.env`, banco, `.deps`, `node_modules` ou `demo-acessos.txt`. Crie dois serviços Railway a partir desse repositório.
3. Serviço API: configure Root Directory `/backend`. O `Dockerfile` instala dependências e executa `python -m app.start`, que valida o ambiente e aplica as migrações antes do Uvicorn. Configure as variáveis listadas abaixo. Use uma réplica neste MVP, evitando migrações concorrentes na inicialização. Configure health check `/api/health` e gere domínio HTTPS.
4. Serviço frontend: Root Directory `/frontend`. Configure `VITE_API_URL=https://DOMINIO-API` **antes do build**, sem barra final. O Dockerfile recusa build sem URL HTTPS da API, faz o build PWA e serve SPA pelo Nginx, respeitando `PORT` do Railway. Gere domínio HTTPS.
5. Atualize `CORS_ORIGINS=https://DOMINIO-FRONTEND` na API. Não inclua caminhos nem barra final; não use `*`. Se houver mais de uma origem autorizada, separe por vírgulas sem espaços.
6. Configure as duas senhas de demonstração e `SEED_DEMO=true` na primeira implantação da API, para carregar explicitamente os dados fictícios na inicialização. Depois, pode voltar a `false`. Alternativamente, execute `python -m app.seed` no ambiente da API. O seed é idempotente e não troca senhas existentes. Nunca exponha senhas nas variáveis `VITE_*`.
7. Mantenha `MAINTENANCE_ENABLED=true`: a API aplica a retenção ao iniciar e a cada hora, usando sessões independentes. Ela elimina relatos/eventos expirados, auditoria expirada, buckets e revogações temporários. O comando `python -m app.retention` continua disponível para execução manual. Quando a API estiver parada, a limpeza física aguarda sua inicialização; consultas sempre ocultam registros expirados.
8. Valide no domínio HTTPS: criar denúncia fictícia → baixar acesso → consultar → entrar como socioemocional → atualizar → consultar → entrar como gestão → aplicar filtros. Configure monitoramento de disponibilidade sem capturar corpos ou dados de formulários.

### Variáveis da API

| Variável | Valor / finalidade |
|---|---|
| `DATABASE_URL` | URL PostgreSQL Neon com TLS; segredo apenas na API |
| `JWT_SECRET` | Aleatório, pelo menos 32 caracteres; gerar com `secrets.token_urlsafe(48)` |
| `ENVIRONMENT` | `production` na hospedagem; `local` no desenvolvimento |
| `DEMO_MODE` | `true`, obrigatório neste MVP |
| `SEED_DEMO` | `true` para carregar explicitamente contas/casos na inicialização; depois pode ficar `false` |
| `CORS_ORIGINS` | Domínio HTTPS exato do frontend |
| `PRIVACY_THRESHOLD` | `5`, mínimo permitido; define as faixas e o limiar |
| `RETENTION_DAYS` | `30`, ajustar conforme governança da demonstração |
| `MAINTENANCE_ENABLED` | `true`: limpeza na inicialização e a cada hora, sem serviço extra |
| `SUPPORT_NAME`, `SUPPORT_CONTACT` | Vazio até configuração de contato institucional autorizado |
| `DEMO_STAFF_PASSWORD`, `DEMO_MANAGER_PASSWORD` | Senhas diferentes, pelo menos 12 caracteres, usadas somente no seed |
| `PORT` | Definido pelo Railway; consumido pelo comando de inicialização |

Use `backend/.env.example` e `frontend/.env.example` como referências; `.env` de desenvolvimento nunca deve entrar na imagem Docker. O secret JWT pode ser rotacionado para invalidar todas as sessões.

As configurações foram preparadas conforme a [documentação Railway de Dockerfiles](https://docs.railway.com/builds/dockerfiles), [comandos de inicialização](https://docs.railway.com/deployments/start-command), [conexão Neon](https://neon.com/docs/get-started/connect-neon) e [segurança FastAPI](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/).

## Testes

API, com dependências Python instaladas:

```powershell
cd backend
python -m pytest -q
```

Os testes usam banco SQLite isolado em memória, sem acessar o banco da demonstração. Verificam fluxo vertical, autenticação, perfis, chave, rate limit, validações, privacidade, expiração, quiz e retenção.

Frontend:

```powershell
cd frontend
npm run build
npm run preview -- --port 4173 --strictPort
```

Com a API, o frontend de desenvolvimento (5173) e o preview PWA (4173) ativos, em outro terminal:

```powershell
cd frontend
npx playwright install chromium
npm run test:e2e
```

Os testes E2E exigem os serviços locais acima ativos e `backend/.env` preparado com as contas seed. Criam novos casos fictícios no banco local. Rodam em 1440 px e 375 px, testam criação/consulta/gestão, quiz, filtros, erros e ausência de overflow; axe verifica regras automáticas de acessibilidade. Os testes PWA usam o preview em 4173 e conferem critérios de instalação, ícones, service worker, cache e fallback offline. Capturas ficam em `docs/validacao/`. Aguarde um minuto se repetir testes e atingir o limitador de login/criação. A validação automática não equivale a uma certificação WCAG nem substitui avaliação manual assistiva.

## Organização

```text
backend/app/          configuração, modelos, schemas, segurança, API, seed e retenção
backend/migrations/  histórico Alembic versionado
backend/tests/       API e regras de segurança
frontend/src/        cliente tipado, sessão, componentes e páginas
frontend/tests/      integração real e acessibilidade
docs/                roteiro de vídeo, validação e capturas
CyberCare_Codex/     referências originais preservadas
```

## Proteções e limites

- Não há anexos, chatbot, triagem automática, recuperação de chave, certificados ou notificações automáticas. Consulta atualiza por solicitação do usuário.
- Nenhuma narrativa é enviada a serviços de IA ou analytics. A API não registra IP bruto nem conteúdo nos access logs; estes estão desativados. O limitador persiste HMAC de origem por janela de um minuto, com expiração de dois minutos e limpeza diária.
- Uvicorn não confia automaticamente em headers de proxy. Assim, atrás do Railway, usuários podem compartilhar o limite do IP do proxy. É uma restrição conservadora aceitável para uma demonstração pequena; revisão de proxy confiável é necessária para escala.
- Agregados em faixas e supressão complementar reduzem exposição. Filtros repetidos não fornecem uma garantia matemática de privacidade diferencial. Este painel é destinado exclusivamente a dados fictícios.
- Não há inscrição pública de usuários; as contas são criadas pelo responsável via seed. A extensão para usuários institucionais, recuperação de senha e gestão de contas deve passar por governança própria.
- Backups Neon e retenção de backups precisam ser configurados pelo operador. Não existe autenticação de acesso ao site público demonstrativo; ele está sinalizado e exige confirmação de dados fictícios.
- Hospedagem e conexão real ao Neon dependem das contas, credenciais e domínios externos. Consulte `docs/VALIDACAO.md` para o que foi efetivamente testado.

O roteiro da apresentação está em `docs/ROTEIRO_VIDEO.md`.
