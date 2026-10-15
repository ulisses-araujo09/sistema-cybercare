# CyberCare — instruções do projeto

## Desenvolvimento

- Interface e documentação para o usuário em português brasileiro.
- React web, Vite, TypeScript e Tailwind; FastAPI, SQLAlchemy e Alembic; PostgreSQL Neon na hospedagem e Railway para os dois serviços.
- Preservar as referências originais em `CyberCare_Codex/`. A identidade usa laranja, verde-escuro e creme, com cartões azul, roxo e verde.
- Somente dados fictícios. Nunca publicar senhas, arquivos `.env`, chaves, banco local, dados de estudantes ou conteúdo de denúncias reais.
- Acesso individual somente socioemocional. Gestão somente agregados. Segredos de consulta armazenados como hash.
- A PWA armazena somente recursos estáticos. Nunca adicionar cache de `/api`, páginas privadas, protocolos, chaves, relatos ou credenciais. Atualizações não devem recarregar formulários automaticamente.
- Validar mudanças com build e testes adequados. Testes de PWA precisam do build servido em `127.0.0.1:4173`.

## Repositórios definidos pelo usuário

- **Oficial / origin:** `https://github.com/ulisses-araujo09/sistema-cybercare.git`
- **Cópia / backup:** `https://github.com/ulissesoliveiraa/CYBERCARE.git`

Ao publicar alterações autorizadas neste projeto, manter os dois repositórios sincronizados com o mesmo commit. Conferir os históricos antes do envio e verificar os hashes remotos após o push. Não usar force push nem substituir trabalho remoto sem autorização. Se um envio falhar, informar precisamente qual repositório foi atualizado e qual continua pendente.

O usuário determinou que o envio aos repositórios vem antes da implantação Railway/Neon. Não declarar publicação ou implantação concluída sem verificação real.
