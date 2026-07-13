# CLAUDE.md

Este é o **hub** do ecossistema Automações do Notion. O código das ferramentas vive em módulos separados; sua primeira ação em qualquer tarefa é ler o **`AGENTS.md`** deste repositório — ele roteia cada tipo de pedido (usar o Notion vs. desenvolver as ferramentas) para o repositório e arquivo corretos.

Regras essenciais:

- Pedido de **uso** do Notion → CLI `notion-tasks` (instalável via pip, ver AGENTS.md).
- Pedido de **desenvolvimento** → `python bootstrap.py` para clonar/atualizar os módulos em `modules/`, edite lá, teste lá (`python -m pytest`), commite e push **no repositório do módulo**.
- Nunca desenvolva funcionalidade neste hub; aqui só vivem documentação, roteamento e o `bootstrap.py`.
- **Mudança manual é exceção**: para manipular dados (no Notion ou em qualquer projeto do padrão de qualidade), prefira sempre scripts e automações reutilizáveis (CLI `notion-tasks`, serviços do `notion-starter`) — scripts viram patrimônio que modelos de IA melhores aprimoram ao longo do tempo; se precisar editar à mão, registre o motivo.
- Decisões de arquitetura ficam registradas em `IA.md`; convenções (português, Conventional Commits, fronteiras de camada) estão no `AGENTS.md`.
