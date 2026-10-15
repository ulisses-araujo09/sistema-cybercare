# Validação da entrega CyberCare

Validação local concluída em 14/10/2026 (America/Sao_Paulo). Ambiente: Windows, Python 3.12, Node.js, Chromium Playwright. Todos os registros utilizados são fictícios.

## Resultado executado

| Verificação | Resultado |
|---|---|
| `npm run build` | Aprovado, TypeScript, Vite e PWA; manifest, ícones e service worker gerados |
| `python -m pytest -q` | **10 testes aprovados** |
| `npm run test:e2e` | **12 testes aprovados**, 43,0 segundos |
| Acessibilidade axe | Nenhuma violação nos conjuntos automáticos WCAG A/AA selecionados, nas sete rotas públicas, em ambos os tamanhos |
| Larguras | 1440×1000 e 375×812, sem overflow horizontal da página nas rotas testadas |
| Alembic SQLite | Aplicação inicial, downgrade em banco descartável e nova aplicação aprovados |
| Alembic PostgreSQL | SQL de upgrade gerado em modo offline; não equivale à execução em um servidor PostgreSQL |
| Seed | 50 casos e cinco questões; idempotência validada por teste isolado |
| `iniciar-demo.ps1` e `-PrepararSomente` | Executados com sucesso; health check local aprovado |
| npm audit durante instalação | 0 vulnerabilidades reportadas para as dependências resolvidas |
| PWA no build de produção | Critérios de instalação Chromium sem erros, nos dois tamanhos; dimensões dos ícones conferidas |
| PWA offline e cache | Fallback educativo funcional; sem API, páginas privadas, protocolos, chaves ou sessões nos caches |
| Configuração hospedada | Testes exigem PostgreSQL com TLS, segredo forte, CORS HTTPS e modo fictício |

## Fluxo real de ponta a ponta

Em cada tamanho de tela, o teste executou o frontend React conectado ao FastAPI por proxy, com persistência SQLite em disco:

1. Registrar denúncia fictícia anônima.
2. Receber protocolo aleatório e chave privada.
3. Consultar com os dois códigos e verificar “Denúncia recebida”.
4. Autenticar como socioemocional, abrir o relato e atualizar para “Em análise”, com nota interna fictícia.
5. Encerrar a sessão e consultar novamente, verificando o status atualizado e a ausência da narrativa/nota no retorno público.
6. Verificar que `/protocolo` não reapresenta a chave depois de sair da tela.

Também foram executados quiz completo com feedback do servidor, consulta inválida, acesso gerencial, filtros, checagem de páginas e capturas de tela. As imagens em `docs/validacao/` documentam o estado observado e não representam resultados científicos.

Os quatro testes PWA (dois por dispositivo) usam o build servido em 4173, com service worker real. Conferem manifest, PNGs, ausência de erros de instalabilidade no protocolo Chromium, cache após login/consulta e página offline sem formulários. Não foi realizada instalação nativa no dispositivo pessoal do usuário nem teste em um iPhone físico.

## Testes de API

- Protocolo sem chave rejeitado; segredo incorreto rejeitado; hash persistido sem segredo original.
- Narrativas restritas ao perfil socioemocional; gestão e acesso não autenticado bloqueados.
- Senha inválida, JWT inválido/expirado, usuário inativo e token revogado rejeitados.
- Limites de criação/consulta, validação de tamanho, confirmação fictícia e corpo HTTP.
- Agregação em faixas, supressão complementar e ausência de protocolos/narrativas no painel gerencial.
- Transições de status em ordem e exclusão de registros expirados das consultas.
- Quiz sem resposta correta antecipada, correção no servidor e alternativas inválidas rejeitadas.
- Rotina de retenção exclui conteúdos/eventos expirados e preserva registros recentes.
- Seed repetido não duplica casos, usuários ou perguntas.

## Correções realizadas durante a validação

- Importação de ícone ausente corrigida antes do build aprovado.
- Carregamento explícito de `.env` no seed.
- Localizador do seletor gerencial corrigido; os filtros passaram nos dois tamanhos.
- Limite de corpo HTTP também aplicado ao recebimento por chunks.
- Agregação gerencial executa consultas de contagem sem carregar narrativas.
- Parâmetros SQL ocultos em erros; falhas de banco retornam mensagem genérica.

## Dependências externas e limites da evidência

**Não implantado no Railway e não conectado ao Neon nesta sessão.** Ainda dependem do responsável: contas, projeto Neon, `DATABASE_URL`, segredos, domínios HTTPS, CORS, seed hospedado, job de retenção e contatos institucionais. Não foram fornecidas credenciais externas.

Docker não está disponível neste ambiente. Os Dockerfiles e o Nginx foram preparados e revisados, mas as imagens não foram construídas nem executadas aqui. A integração foi validada com o servidor Vite e o Uvicorn locais. PostgreSQL precisa ser exercitado antes da gravação usando Neon ou Docker Compose e o roteiro do README.

Um aviso de depreciação transitivo do Starlette/AnyIO aparece nos testes Python, sem falhas. O executor do navegador emite aviso sobre `NO_COLOR`/`FORCE_COLOR`, sem efeito funcional.

Verificação automática de acessibilidade não certifica conformidade integral WCAG 2.2 AA. Não foram realizados testes com leitores de tela humanos, estudo com estudantes, auditoria independente, teste de carga ou validação científica de eficácia.

Anexos, notificações automáticas, chatbot, certificados, recuperação de chave e gestão institucional de usuários não fazem parte desta entrega. O uso com dados reais permanece fora do escopo.
