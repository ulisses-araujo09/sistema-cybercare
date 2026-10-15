# PWA e publicação do CyberCare

## Aplicativo instalável

O build de produção contém manifest em português, ícones de 192 e 512 px, ícone adaptável de 512 px e ícone Apple de 180 px. A marca própria usa o escudo de proteção nas cores do projeto. Não utiliza logomarcas governamentais.

O botão **Instalar app** aciona o recurso nativo quando o navegador o oferece; caso contrário, mostra as orientações. No iPhone/iPad, usar Safari → Compartilhar → Adicionar à Tela de Início. No Android e no computador, usar Chrome/Edge e a opção de instalação disponível no navegador. A apresentação exata depende da plataforma.

A instalação hospedada exige HTTPS. `localhost`/`127.0.0.1` permitem validação local. O modo `npm run dev` serve ao desenvolvimento e não habilita o service worker; para testar a PWA:

```powershell
cd frontend
npm ci
npm run build
npm run preview -- --port 4173 --strictPort
```

Com a API local ativa, abrir `http://127.0.0.1:4173`. O proxy de preview também encaminha `/api` ao FastAPI local.

## Privacidade no dispositivo

- Cache contém somente JavaScript/CSS de build, ícones, logo e página offline educativa.
- Não contém respostas da API, páginas da aplicação, conteúdo dos painéis, relatos, protocolos, chaves, senhas ou tokens de sessão.
- Sem internet, a navegação exibe página estática de orientação. Não existem fila de denúncias nem envio posterior automático.
- Sessões continuam somente em memória, com as mesmas permissões e expiração do backend.
- Nova versão exige clique em **Atualizar aplicativo**, com orientação para guardar a chave e concluir formulários antes. Não há recarga automática de uma denúncia em preenchimento.

Os requisitos foram conferidos com a [documentação de instalação MDN](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Guides/Making_PWAs_installable) e a estratégia de [service worker personalizado Vite PWA](https://vite-pwa-org.netlify.app/guide/inject-manifest).

## Repositório oficial e cópia

Por definição do responsável:

- Oficial: [ulisses-araujo09/sistema-cybercare](https://github.com/ulisses-araujo09/sistema-cybercare)
- Cópia: [ulissesoliveiraa/CYBERCARE](https://github.com/ulissesoliveiraa/CYBERCARE)

Os remotes locais são `origin` e `backup`, respectivamente. Para publicar alterações autorizadas:

```powershell
git push origin main
git push backup main
git ls-remote origin refs/heads/main
git ls-remote backup refs/heads/main
```

Ambos devem apontar para o mesmo commit. Nunca enviar `.env`, `demo-acessos.txt`, bancos ou dependências instaladas. Os arquivos de configuração exemplificativos e o lockfile npm são versionados.

O comando `scripts/publicar.ps1` realiza os dois envios e confere os hashes remotos, sem force push. Requer alterações revisadas e commitadas na branch `main`. O workflow `.github/workflows/verificar.yml` executa testes da API e build PWA em cada push/PR; os testes de navegador completos foram executados localmente e não são simulados pelo workflow.

## Próxima etapa: Neon e Railway

Criar o banco Neon e os dois serviços Railway **depois da publicação Git**, conforme a ordem definida pelo usuário. Não é preciso colocar credenciais no repositório.

API Railway: Root Directory `/backend`, conforme `.railway/railway.ts`. A inicialização `python -m app.start` valida o ambiente, aplica Alembic e inicia Uvicorn. Com `SEED_DEMO=true`, também carrega explicitamente as contas e os casos fictícios, usando as senhas configuradas nas variáveis privadas. Depois da primeira carga, `SEED_DEMO` pode voltar a `false`.

Frontend Railway: Root Directory `/frontend`, conforme `.railway/railway.ts`. Definir `VITE_API_URL` com a URL HTTPS pública da API antes do build. O Dockerfile recusa build sem essa configuração, evitando publicar um frontend sem conexão à API.

O banco hospedado deve usar conexão PostgreSQL com `sslmode=require` ou verificação de certificado. `ENVIRONMENT=production`, `DEMO_MODE=true`, `JWT_SECRET` forte e `CORS_ORIGINS` com o domínio HTTPS exato do frontend são obrigatórios. Completar os contatos institucionais. A retenção física agora é executada pela API ao iniciar e a cada hora, com `MAINTENANCE_ENABLED=true`.

A infraestrutura atual é gerenciada por `railway config plan` / `railway config apply`, com o SDK instalado por `npm ci` na raiz. Os antigos arquivos `railway.json` foram substituídos, pois o Railway deixou de aceitá-los em novos serviços. A primeira implantação usa um snapshot limpo do commit via CLI. O autodeploy por GitHub depende de autorizar o GitHub App Railway para o repositório oficial; não é necessário para o upload via CLI.
