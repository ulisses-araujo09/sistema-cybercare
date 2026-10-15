# AGENTS.md — CyberCare | FECULEMA 2026

## Missão e fontes
Implementar um MVP web responsivo real e demonstrável para a apresentação virtual da FECULEMA 2026. Leia PRIMEIRO `PROMPT_CODEX.md`, `DOCUMENTACAO_TECNICA.pdf` e `referencias/poster_original.jpg`. A imagem do pôster é referência visual e conceitual, NÃO comprovação de software pronto. O protótipo em `prototipo/index.html` é referência de interface, não backend funcional. O edital está em `referencias/edital_feculema_2026.pdf`.

## Restrições inegociáveis
- React web, NÃO React Native. React + Vite + TypeScript + Tailwind; FastAPI + SQLAlchemy + Alembic; PostgreSQL Neon; deploy frontend/backend Railway.
- Linguagem pt-BR em toda interface; responsividade mobile-first; acessibilidade WCAG 2.2 AA como objetivo.
- Dados de denúncia são altamente sensíveis, envolvendo possivelmente menores. Ambiente de feira deve usar EXCLUSIVAMENTE dados fictícios. NÃO abrir coleta real ao público nem alegar aprovação institucional.
- Não inventar resultados científicos, estatísticas reais, contatos escolares, psicólogos ou serviços de emergência. Onde faltarem dados, usar configuração editável e aviso explícito.
- Denúncia anônima sem login, com protocolo imprevisível + segredo de consulta separado; nunca permitir enumeração ou consulta só pelo protocolo. Segredo armazenado como hash. Rate limit em criação e consulta.
- Acesso ao conteúdo da denúncia SOMENTE perfil socioemocional autorizado. Perfil gerencial vê dados agregados e suprimidos em grupos pequenos; não deve consultar narrativas individuais.
- Não enviar conteúdos de denúncias a LLMs, serviços analíticos ou logs. Não registrar IPs ou identificadores desnecessários. Sanitizar entradas, impor limites e políticas de retenção.
- Autenticação robusta com hash Argon2, tokens curtos, cookies seguros quando aplicável, CORS restrito e RBAC validado no servidor. Sem credenciais hardcoded em produção.
- Anexos: apenas se armazenamento privado seguro estiver implementado com validação de tipo/tamanho, autorização e acesso temporário. Caso contrário, deixar desativado e documentado; nunca salvar anexos sensíveis no filesystem efêmero do Railway.
- Botão 'Emergência' deve mostrar orientação para procurar adulto/responsável e serviço local competente, sem prometer atendimento em tempo real.
- IA é escopo futuro: não implementar chatbot terapêutico ou triagem automática.

## Método de execução
1. Inspecionar diretório e dependências. Preservar arquivos existentes.
2. Criar monorepo `frontend/` e `backend/`, .env.example, README, migrações e testes.
3. Priorizar fluxo vertical funcional: criar denúncia fictícia -> protocolo + chave -> consultar -> login socioemocional -> atualizar status -> consultar novamente.
4. Implementar apoio e quiz com conteúdo educativo revisável; dashboard agregado em seguida.
5. Fazer testes automatizados de API, permissões e fluxos; build frontend e smoke test; corrigir erros antes de encerrar.
6. Preparar seed demo explícito e instruções Railway/Neon; nunca publicar segredos.
7. Ao concluir cada etapa, informar: arquivos alterados, comandos executados, testes, limitações e próximo passo.

## Critérios de pronto
- `npm run build` e testes de backend passam.
- UI funciona em 375px e desktop; estados de carregamento, vazio, erro e sucesso.
- Demo acessível com casos fictícios, sem exigir serviços pagos para testes locais.
- Perfis isolados no backend; endpoints não revelam dados pessoais.
- README permite execução local e deploy independente no Railway.
- Não declarar funcionalidade pronta sem testá-la.

## Identidade visual e layouts (OBRIGATÓRIO)
- Todo texto de interface, mensagens, botões, rótulos, navegação, validações, exemplos e documentação voltada ao usuário em português brasileiro.
- Reproduzir a identidade do pôster: laranja #E84B18, verde-escuro #073F39, creme #FFF8EF, verde #087B5A; cartões complementares azul #216FA8, roxo #7B3895 e amarelo #E8A01D.
- Referência principal de telas: `prototipo/index.html`, que tem modos Computador e Celular. Não gerar UI apenas em inglês nem limitar desktop a um telefone centralizado.
- Desktop: barra lateral fixa, cabeçalho largo, cards em colunas, formulários de duas colunas, dashboard com indicadores e gráficos. Mobile: menu rolável ou navegação acessível, cards em duas colunas, formulários em uma coluna, sem rolagem horizontal indevida.
- Todas as seis telas devem ter versão responsiva: Início, Denúncia, Acompanhamento, Apoio emocional, Quiz e Painel escolar.
- O protótipo é somente visual; implementar fluxos reais com backend e permissões, sem confundir dados de exemplo com dados reais.
