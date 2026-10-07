# CLAUDE.md

Este é o repositório do **Felixo Notion MCP**: um pacote único, `felixo-notion-mcp` (import `felixo_notion_mcp`), com o código em `src/felixo_notion_mcp/`, organizado em camadas. Sua primeira ação em qualquer tarefa é ler o **`AGENTS.md`** deste repositório — ele roteia cada tipo de pedido (usar o Notion vs. desenvolver as ferramentas) para a camada e o arquivo corretos.

Regras essenciais:

- Pedido de **uso** do Notion → distribuição `notion-automacoes` (alias
  `notion-tasks`, instalável via `pipx`, ver AGENTS.md).
- Pedido de **desenvolvimento** → edite em `src/felixo_notion_mcp/<camada>/` (tabela de roteamento do AGENTS.md), prepare com `uv sync --locked --all-extras`, teste com `uv run python -m pytest` e `uv run ruff check .`. `python start_app.py` abre o menu. Não há mais `modules/` nem repositórios de módulo: o código é este.
- Se editou e nada mudou, `felixo-notion-mcp doctor` mostra de onde o pacote está sendo importado (só informa; não avisa).
- **Mudança manual é exceção**: para manipular dados (no Notion ou em qualquer projeto do padrão de qualidade), prefira sempre scripts e automações reutilizáveis (CLI `notion-tasks`, serviços de `src/felixo_notion_mcp/services/`) — scripts viram patrimônio que modelos de IA melhores aprimoram ao longo do tempo; se precisar editar à mão, registre o motivo.
- Organização de workspace sem instrução específica do usuário → seguir o modelo padrão em `DESIGN-WORKSPACE-NOTION.md`.
- Decisões de arquitetura ficam registradas em `IA.md` (append-only); convenções (português, Conventional Commits, um tema por commit, fronteiras de camada) estão no `AGENTS.md`; o mapa das camadas está em `docs/ARQUITETURA.md`.
