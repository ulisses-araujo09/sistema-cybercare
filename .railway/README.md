# Infraestrutura Railway do CyberCare

O arquivo `railway.ts` descreve os serviços `cybercare-api` e `cybercare-web`, com pastas de origem, Dockerfiles, health checks, réplica e reinício em caso de falha.

Instale a CLI oficial Railway, execute `npm ci` na raiz, autentique com `railway login` e selecione o projeto correto com `railway link`.

```powershell
railway config plan
railway config apply
```

Revise o plano antes de aplicar. A configuração deve manter os dois serviços. Não utilize opções de confirmação de destruição para atualizações rotineiras.

As variáveis são `unmanaged`: senhas, JWT_SECRET e DATABASE_URL permanecem somente no Railway. Nunca execute importação com `--include-variables`, nem coloque valores privados neste arquivo.

As pastas são `/backend` e `/frontend`. O banco permanece no Neon. Os domínios gerados são preservados pelo Railway e não precisam aparecer nesta configuração.

A primeira implantação usa snapshot limpo de um commit do repositório oficial por meio da CLI. A conexão de autodeploy GitHub é uma autorização separada do GitHub App Railway. Ao habilitá-la, selecione somente o repositório oficial e preserve as pastas dos serviços.

Os arquivos `railway.json` foram removidos porque a versão atual do Railway não permite sua adoção em serviços novos. Referência: https://docs.railway.com/infrastructure-as-code
