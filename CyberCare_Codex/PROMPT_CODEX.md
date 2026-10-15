# PROMPT MESTRE — CODEX | CYBERCARE

Você é responsável pela implementação end-to-end de um MVP real do CyberCare, projeto educacional do IEMA para prevenção e acompanhamento de bullying/cyberbullying, a ser demonstrado em vídeo na FECULEMA 2026. Prazo de submissão do vídeo virtual: 18/10/2026. Priorize estabilidade e demonstração confiável.

## ANTES DE CODIFICAR
Leia `AGENTS.md`, `DOCUMENTACAO_TECNICA.pdf`, `referencias/poster_original.jpg`, `referencias/edital_feculema_2026.pdf` e `prototipo/index.html`. O pôster descreve proposta e telas de Figma, não um sistema implementado. Preserve as cinco áreas: denúncia, acompanhamento, apoio emocional, quiz e painel escolar. React web é a tecnologia confirmada pelo orientador; não usar React Native. A tecnologia de banco originalmente mencionada no pôster foi MySQL, mas a decisão atual de implementação é PostgreSQL Neon; documentar a alteração técnica sem falsificar o resumo submetido.

## ENTREGAS
1. `frontend/`: React + Vite + TypeScript + Tailwind, rotas, design system, formulários acessíveis, validação com Zod, cliente HTTP tipado.
2. `backend/`: FastAPI, SQLAlchemy, Alembic, Pydantic, autenticação de usuários escolares, autorização RBAC, endpoints documentados em OpenAPI, testes pytest.
3. Banco PostgreSQL Neon via DATABASE_URL, sem conexão real obrigatória para iniciar desenvolvimento; fornecer opção local de PostgreSQL com Docker Compose.
4. Dois serviços Railway (frontend e backend) e variáveis de ambiente documentadas; domínio/API configuráveis e CORS restrito.
5. Seed fictício e instruções para gravação de demonstração.

## INTERFACE E IDENTIDADE
Inspirar-se no pôster: laranja #E94F16, laranja profundo #C83C12, verde-petróleo #063E38, verde #087D58, creme #FFF8EE, branco #FFFFFF, roxo #773A8F, azul #2368A5, amarelo #EAA016. Fonte sem serifa de fácil leitura, contraste AA, botões grandes, cantos arredondados, ícones consistentes, textos pt-BR. Logo do pôster não deve ser recriado de forma enganosa: usar logotipo textual CyberCare e, se possível, recorte autorizado do pôster apenas como referência. Não copiar logomarcas governamentais para o app. Slogan: 'Respeito também é tecnologia.'

## ROTAS E TELAS
Públicas: `/` home; `/denunciar` formulário (vítima/testemunha; categoria; local opcional; relato; confirmação); `/protocolo` sucesso com protocolo e chave mostrada UMA vez; `/acompanhar` consulta de protocolo+chave, linha do tempo de status; `/apoio` orientações educativas e contatos configuráveis; `/quiz` perguntas e feedback; `/sobre` objetivo e aviso de demonstração.
Privadas: `/login` acesso da escola; `/socioemocional` lista de casos autorizados e detalhe com atualização de status; `/gestao` painel SOMENTE agregado com filtros por período/categoria e limiar de privacidade. Usar dados de demonstração claramente sinalizados.

## MODELO DE DADOS MÍNIMO
`users` (id, email, password_hash, role, active, created_at); `reports` (id UUID, protocol unique, access_secret_hash, reporter_type, category, location_optional, description, status, created_at, updated_at); `report_events` (id, report_id, status, note_private_optional, actor_id_optional, created_at); `quiz_questions` (id, question, options_json, correct_index, explanation, active); `audit_events` (id, actor_id, action, target_id, created_at) SEM conteúdo de denúncia. Implementar enums e migrações. Não coletar nome do denunciante por padrão.

## REGRAS E API
`POST /api/reports` cria denúncia fictícia, retorna protocolo e chave uma única vez; `POST /api/reports/lookup` exige ambos e usa comparação segura; `POST /api/auth/login`; `GET /api/staff/reports`, `GET /api/staff/reports/{id}`, `PATCH /api/staff/reports/{id}/status` apenas socioemocional; `GET /api/management/metrics` apenas gestão; `GET /api/quiz/questions` sem resposta correta exposta antes de submeter (ou validar resposta no servidor). Adicionar validações, limites, paginação, rate limit, CORS, tratamento de erros e logs sem conteúdo sensível.

## CONTEÚDO E SEGURANÇA
Apoio emocional: informações gerais, não substitui atendimento profissional. Sem chatbot clínico. Em situações de risco, recomendar procurar imediatamente um adulto de confiança, equipe escolar e serviços competentes; contatos institucionais são configuráveis e NÃO devem ser inventados. Exibir aviso 'Ambiente demonstrativo — não envie denúncias reais'. Upload de evidências é opcional e só entra se houver armazenamento privado seguro; caso contrário mostrar 'Em desenvolvimento'.

## FLUXO DE EXECUÇÃO
FASE A: scaffold, design system e rotas com dados mockados; validar build.
FASE B: banco, migrações, API e autenticação; testar endpoints.
FASE C: integrar denúncia/protocolo/acompanhamento/painel; teste ponta a ponta.
FASE D: apoio, quiz, métricas agregadas e responsividade.
FASE E: Railway/Neon, seed demo, documentação, testes, checklist de vídeo.
Execute de forma autônoma dentro do repositório e avance por fases, mas nunca simule sucesso de testes. Se faltar credencial externa, prepare .env.example e prossiga localmente. Não bloqueie o trabalho esperando chave Neon ou Railway.

## DEFINIÇÃO DE PRONTO
O fluxo principal deve persistir no banco; dados fictícios e contas demo identificadas; testes de autenticação/RBAC e consulta de protocolo; UI mobile; README de deploy; sem segredos commitados. Documente limitações e qualquer alteração do escopo.


## Complemento obrigatório — identidade e adaptação de telas
O projeto deve ser 100% em português brasileiro na interface. Abra `prototipo/index.html` e use os botões "Computador" e "Celular" para inspecionar as duas composições. Não replique um telefone centralizado no desktop: crie um layout desktop real com barra lateral, conteúdo amplo, cards e gráficos. No celular, reorganize navegação e formulários para telas pequenas. Siga as cores e referências do `AGENTS.md`. Todas as seis páginas precisam funcionar nos dois tamanhos. Não invente resultados ou dados reais.
