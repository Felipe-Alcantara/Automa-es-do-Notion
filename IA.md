# 🤖 IA.md — Contexto operacional do projeto

> **O que é**: Memória técnica do projeto para retomada de contexto por IA ou por
> um novo mantenedor, sem precisar reler todo o código ou o histórico de conversa.
> Baseado no template de contexto do Felixo System Design.

> ⚠️ **NOTA DE ESTRUTURA (2026-07-02)**: o monorepo descrito neste documento foi
> separado em módulos. Os caminhos citados abaixo (`src/`, `cli/`, `server/`,
> `front/`) hoje vivem em repositórios próprios — veja o mapa de roteamento no
> **`AGENTS.md`** deste hub, que é o guia operacional atual. Este arquivo permanece
> como **histórico de decisões** (as decisões continuam válidas; só os caminhos
> mudaram): `src/notion_starter` → repo `notion-starter`; `cli/` + `core/` +
> `integrations/` + `services/` → repo `notion-tasks-cli`; `server/` + `front/` +
> `start_app.py` → repo `notion-workspace-app`.

---

## 🎯 OBJETIVO DO PROJETO

[2026-06-24] `notion-starter-boilerplate` é um boilerplate/template open source para
iniciar projetos sobre a API do Notion. Traz um cliente Python tipado, helpers de
propriedade, validação de schema e exceções claras como base pronta para clonar e
adaptar. Independente de framework, uma única dependência de runtime (`requests`).
Público: desenvolvedores que vão começar uma integração com o Notion.
Distribuição: como TEMPLATE (clone/"Use this template" e renomeie), não como pacote
PyPI fechado. O `pyproject.toml` segue funcional para `pip install -e` local.

[2026-06-29] O repositório público `Automa-es-do-Notion` passou a ser documentado como
aplicação local de automações para Notion, GitHub e IA, não como template genérico.
O core `notion_starter` continua sendo a base importável, mas README, metadados do
`pyproject.toml`, CONTRIBUTING e `start_app.py` agora descrevem o produto real.

---

## 🏁 METAS & MILESTONES

- [2026-06-24] ✅ Extração da biblioteca a partir do app Django interno `notion_sync`.
- [2026-06-24] ✅ Tradução de toda a biblioteca para português (código, docs, erros).
- [2026-06-24] ✅ Documentação alinhada ao padrão de qualidade (README, CONTRIBUTING, IA.md).
- [2026-06-24] ✅ `start_app.py` — menu de entrada interativo (Iniciar/Rodar, Instalar/Setup,
  Configurar, Status/Sair), fechando o último item obrigatório do padrão Felixo.
- [2026-06-24] ✅ Reposicionamento de "biblioteca notion-sync" para boilerplate/template
  `notion-starter-boilerplate`: pacote renomeado para `notion_starter`, README/CONTRIBUTING/
  IA.md reescritos no enquadramento de template, e exemplo end-to-end `sync_from_csv.py`.
- [2026-06-25] ✅ `NotionClient.buscar()` — varredura do workspace via `/search` com
  paginação (base para inventariar/mapear o que a integração enxerga).
- [2026-06-25] ✅ `inventory.py` — lógica pura que monta árvore (via `parent`),
  duplicatas por nome, vazios e órfãos a partir dos itens de `buscar()`. Sem rede,
  testado em `tests/test_inventory.py`.
- [2026-06-25] ✅ Mapeamento end-to-end: `examples/coletar_mapa.py` (varre + conta
  linhas dos databases → `mapa.json`) e `examples/gerar_arvore_html.py`
  (`mapa.json` → `mapa.html` navegável). `listar_paginas.py` refatorado para usar
  `buscar()`. Menu (`start_app.py`) ganhou a ação "Mapear workspace".
- [2026-06-25] ✅ `inventory.extrair_perfil_database`/`assinatura_perfil` —
  assinatura rica (colunas + opções de select/status/multi_select) para distinguir
  databases "geralzões" de mesma estrutura mas conteúdo diferente.
- [2026-06-25] ✅ `tasks.py` — camada de alto nível de tasklist (objeto `Tarefa`,
  classe `TaskList` com listar/criar/atualizar_status/concluir) sobre o
  `NotionClient`. Colunas configuráveis via `CamposTarefa`. Base para o front + IA.
- [2026-06-25] ✅ Fechamento da `TaskList` no padrão: exemplo executável
  `examples/gerenciar_tarefas.py` (lista/cria/conclui), ação no menu
  (`start_app.py` → Iniciar/Rodar) e menção no README. Assim o recurso fica
  alcançável pela porta de entrada e documentado, não só no core + teste.
- [2026-06-25] ✅ `start_app.py` → Configurar ganhou passo a passo guiado
  (painel `rich`) para obter o token do Notion: criar a integração, copiar o
  secret e — o passo que mais derruba iniciante — compartilhar a página com a
  integração via ••• → Conexões. Antes a orientação só existia no `.env.example`.
- [2026-06-25] ✅ O menu de `start_app.py` passou a abrir cada ação em um terminal
  dedicado (`--action <nome>` no processo filho). O menu principal não espera o
  término da ação, permitindo manter servidor web, MCP e outras opções em paralelo.
  O lançador cobre Windows, macOS e os principais emuladores de terminal Linux.
- [2026-06-25] ✅ “Iniciar tudo” virou a ação principal de um clique: usa
  `127.0.0.1:8000`, prepara o Django, aplica migrações, sobe front + API e abre o
  navegador quando o health check confirma que o app está pronto. O MCP permanece
  separado por ser uma integração opcional com o Felixo-AI-Core.
- [2026-06-25] ✅ Biblioteca de visão/estratégia em `docs/`: `PLANO.md` (roadmap
  completo + visão final — front próprio + IA sobre o Notion, em 6 fases),
  `MODELOS-DE-USO.md`, `PORTABILIDADE.md`, `SAAS.md`, `ESCALA.md`, `OTIMIZACAO.md`,
  `IDEIAS-EXTRAS.md` e um índice `README.md`. Decisões direcionais registradas:
  stack-alvo Django + SQLite; integração de agentes via MCP com o projeto irmão
  Felixo-AI-Core; camada de IA com provedor plugável — OpenRouter (pague por uso)
  **e** assinaturas (Codex, Claude Code Pro, Cursor; futuramente Gemini CLI e
  Copilot CLI), espelhando o projeto Openia. São documentos de direção (não código),
  abertos à contribuição; o `notion_starter` atual vira a base de tudo.
- [2026-06-25] ✅ **Agente 0 (Contratos & Fundação)** — Fase 0 entregue: `readers.py`
  (par de leitura de `properties.py`: `ler_title/ler_select/ler_status/ler_date/
  ler_multi_select/ler_relation/ler_people…`, `ler_propriedade` por `type` e
  `extrair_valores(pagina)` → mapa coluna→valor simples), com testes puros em
  `tests/test_readers.py` (19) e export em `__init__.py`. Contrato formalizado em
  `docs/CONTRATOS.md`: objetos de domínio (`Tarefa` + serialização da API), rotas REST
  (`GET/POST /api/tarefas`, `PATCH /api/tarefas/{id}`), envelope de erro e a estrutura de
  pastas por camadas. Trabalho coordenado no canvas multi-agente (Infra montou o esqueleto
  Django em `server/` em paralelo).
- [2026-06-25] ✅ **Agente 1 (Infra)** — Esqueleto do servidor Django em `server/`,
  100% alinhado a `docs/CONTRATOS.md` §4 (camadas config/core/integrations/services/
  api/operations). Entregas: `core/config.py` (config por ambiente + leitor de `.env`,
  guarda de produção p/ `SECRET_KEY`), `integrations/notion.py` (fábrica fina sobre
  `notion_starter`), app `operations` (modelos Job/Lock + migração SQLite p/ estado
  operacional), `api/health` (smoke test), extra `[server]` no `pyproject.toml`
  (`django>=5.0`), exclude de migrações no ruff, `.gitignore` do `*.sqlite3`,
  ação "Subir servidor" no `start_app.py` (instala extras, pergunta host:porta,
  aplica migrações e sobe `runserver`) e `docs/INFRA.md`. `manage.py check` limpo.
  Commits: `e68a6db feat` (esqueleto) e `b2ef639 docs` (índice coordenado).
- [2026-06-25] ✅ **Agente 2 (Backend)** — Casos de uso e rotas REST conforme
  `docs/CONTRATOS.md` §1-3. Entregas: `server/services/tarefas.py` (listar/criar/
  mover_status/concluir_tarefa, `TaskList` injetável), `server/api/views.py` +
  `urls.py` (`GET/POST /api/tarefas`, `PATCH /api/tarefas/{id}`),
  `server/api/serializers.py` (`tarefa_para_dict`), envelope de erro padrão
  (`validacao/nao_encontrado/erro_upstream/erro_interno`). Testes:
  `test_services_tarefas.py` (5) + `test_api_tarefas.py` (9, Django test client) +
  `conftest.py`. Commit: `d60d428 feat`.
- [2026-06-25] ✅ **Agente 3 (IA / OpenRouter)** — Camada de IA plugável (Fase 5).
  `server/integrations/openrouter.py`: catálogo de modelos (cache 24 h, `Modelo`
  dataclass, agrupamento por empresa/preço), protocolo `ProvedorIA`,
  `ProvedorOpenRouter` (chat completions via `requests`). `server/services/ia.py`:
  `interpretar_comando` (NL → `AcaoSugerida`) + `executar_acao` (delega p/
  `services.tarefas`), modo copiloto (sugere, pessoa confirma). Testes: 15
  (openrouter) + 19 (ia) = 34 novos testes mockados. Doc: `docs/IA-CAMADA.md`.
  Commit: `6ed8256 feat`.
- [2026-06-25] ✅ **Agente 4 (Front-end)** — Front web para ver e editar tarefas
  reais (Fase 2 do PLANO). `server/templates/tarefas.html` (template Django),
  `server/static/css/app.css` (estilos responsivos), `server/static/js/app.js`
  (JS vanilla consumindo `GET/POST /api/tarefas`, `PATCH /api/tarefas/{id}` via
  fetch). Rota `/` via `TemplateView` em `config/urls.py`. Features: lista com
  filtro por status, criação de tarefa, modal de mover/concluir por status, estados
  de carregando/vazio/erro, feedback acessível (`aria-live`, diálogo semântico e
  restauração de foco). Testes de integração do front: 4. Zero dependências novas.
- [2026-06-25] ✅ **Agente 7 (Otimização & Qualidade)** — Fase 1 entregue no
  `NotionClient`: retry/backoff configurável para operações idempotentes, suporte a
  `Retry-After`, status transitórios do Notion, cache de schema com TTL/invalidação
  e cópias defensivas. Criações só repetem 429/529; rede/5xx ambíguos falham sem retry.
- [2026-06-25] ✅ **Agente 6 (MCP)** — servidor MCP e contrato do host concluídos:
  ferramentas `notion.list_tasks/create_task/move_status/conclude_task` e
  `notion.update_project_page`, validação da borda, erros sanitizados, anotações
  read/write/idempotência e transportes `stdio` + Streamable HTTP. As entradas
  `notion.*` foram incorporadas ao catálogo do Felixo-AI-Core no commit `75c8a12`,
  com confirmação obrigatória em todas as operações de escrita.

- [2026-06-25] ✅ **"Iniciar tudo" → seleção do database de tarefas**: na primeira
  execução, `start_app.py` procura databases compartilhados com a integração que
  atendem ao schema do front (`Tarefa`/title, `Etapa`/status, `Prazo`/date),
  escolhe automaticamente quando há só um, pergunta quando há vários e grava
  `NOTION_DATABASE_ID` no `.env` para reusar depois. Antes o app subia sem saber
  qual database alimentar a lista. Mensagem de erro `erro_interno` da API passou a
  orientar a rodar "Iniciar tudo" novamente em vez do texto genérico.
- [2026-06-25] ✅ **Trocar o database pelo menu**: o menu **Configurar** virou
  submenu (Token / Database) e a opção "Escolher database de tarefas" re-consulta e
  regrava `NOTION_DATABASE_ID` — sem editar o `.env` na mão (padrão Felixo:
  configurar sem editar arquivo). O núcleo busca/escolhe/grava foi extraído p/
  `_selecionar_database_tarefas`; `_garantir_database_tarefas` é a porta do "Iniciar
  tudo" (Open/Closed: trocar pelo menu não mexe no fluxo de subir). O database em
  uso aparece marcado `[atual]` na lista de escolhas.
- [2026-06-26] ✅ **"Iniciar tudo" sempre pergunta o database**: a pedido, deixou de
  reusar em silêncio — toda vez que sobe o site, pergunta qual database usar com o
  atual **pré-selecionado** (Enter mantém). Cancelar mantém o database já salvo e
  segue subindo (só barra se nunca houve um configurado); falha de rede ao consultar
  o Notion também não trava quem já tem um database salvo. Implementado via flag
  `manter_atual_ao_cancelar` em `_selecionar_database_tarefas` (o menu Configurar
  continua com `Cancelar` = não altera nada).
- [2026-06-26] ✅ **Lista todos os databases (sem filtro rígido)**: diagnóstico no
  workspace real mostrou 112 databases compartilhados, mas só 2 batiam o schema
  exato (`Tarefa`/title, `Etapa`/status, `Prazo`/date) — escondendo databases
  de tarefas reais que só diferiam no nome de uma coluna (ex.: `Task Name`). A seleção
  passou a listar **todos** os databases: `_buscar_databases` devolve
  `(titulo, db_id, compativel, faltantes)` ordenando compatíveis primeiro; o menu
  marca `✓`/`⚠` e, ao escolher um incompatível, avisa as colunas faltantes
  (`_colunas_faltantes`) e pede confirmação antes de gravar. O front é de tarefas,
  mas nada impede apontar `NOTION_DATABASE_ID` para outra tabela do projeto.
- [2026-06-26] 📐 **Ciclo 2 planejado nas docs (multiagente)**: as Fases 0–6 estão
  entregues; abriu-se um novo ciclo de evolução, documentado em `docs/` para
  desenvolvimento multiagente. Quatro frentes **independentes o bastante para andar em
  paralelo** (escopos de pasta distintos, mesmo contrato escrito): **A** Núcleo & API v2
  (campos `duracao`/`areas`, `properties.relation`, `PATCH` amplo, `GET /api/opcoes`);
  **B** front **SPA React + Tailwind + Vite** (em `front/`, grade/lista/kanban, busca,
  filtros persistentes — substitui o front vanilla, alinhado ao design system do padrão de
  qualidade); **C** **CLI completa para IA** (em `cli/`, borda fina sobre `services/`, par
  do MCP); **D** Qualidade transversal. Contrato v2 fixado em `docs/CONTRATOS.md`; frentes
  em `docs/PLANO.md` (*Ciclo 2*); agentes em `docs/AGENTES.md`. Decisão de origem:
  diagnóstico leu 15 linhas do database real → só Etapa/Esforço/Áreas da vida são usados
  (Prazo/Prioridade/Projeto/Subitens ficam vazios); o site reflete o uso real.
- [2026-06-26] ✅ **Agente A (Núcleo & API v2)** — contrato v2 de tarefas implementado:
  `properties.relation`, `Tarefa`/`CamposTarefa` com `duracao`/`areas`,
  `TaskList.editar`, resolução/cache de nomes de áreas, `TaskList.opcoes`,
  `services.tarefas.editar_tarefa`/`listar_opcoes`, serializer público com
  `duracao`/`areas`/`areas_nomes`, `POST /api/tarefas` aceitando os campos novos,
  `PATCH /api/tarefas/{id}` amplo e retrocompatível com `{status}`, e `GET /api/opcoes`.
  Validação: 34 testes do escopo A verdes no `.venv` (`test_api_tarefas`, `test_tasks`,
  `test_services_tarefas`), `ruff check` do escopo limpo e
  `DJANGO_DEBUG=1 .venv/bin/python server/manage.py check` sem issues.
- [2026-06-26] ✅ **Agente B (Front React)** — SPA do Ciclo 2 entregue em `front/`
  (`bd35500`): Vite + React 18 + Tailwind, componentes em `components/ui`,
  visualizações grade/lista/kanban, busca, filtros persistentes por status/duração/área,
  ordenação, modais de criar/editar e estados de carregando/vazio/erro. O client consome
  `GET /api/tarefas`, `POST /api/tarefas`, `PATCH /api/tarefas/{id}` e `GET /api/opcoes`
  conforme `docs/CONTRATOS.md`. Atualização posterior: mock do front só roda com
  `VITE_MOCK_API=true`; em uso normal, falha de API/Notion aparece como erro. Filtros de
  status/duração/área descem por API/CLI até a query do Notion; busca textual e ordenação
  ficam no navegador. Documentação viva em `front/README.md`; validação: `npm run lint`,
  `npm run build` e smoke HTTP do Vite em `http://127.0.0.1:5174/`.
- [2026-06-26] ✅ **Agente C (CLI para IA)** — CLI em `cli/` entregue como borda fina
  sobre `server/services/tarefas.py`, irmã do MCP: `python -m cli` suporta
  `listar`, `ler`, `criar`, `editar`, `mover`, `concluir`, `opcoes`, `databases`,
  `escolher-database` e `mapear`; `--json` emite envelope estável
  `{ok,dados}` / `{ok,erro}` para IA/script. `start_app.py` ganhou ação "CLI para IA"
  para mostrar ajuda e exemplos. Docs vivas atualizadas (`README`, `docs/MCP.md`,
  `docs/MODELOS-DE-USO.md`).
- [2026-06-26] ✅ **Nomes intuitivos na fonte Notion** — a fonte de verdade foi
  migrada pelo comando `python -m cli --json normalizar-nomes`: propriedades do
  database principal viraram `Tarefa`, `Etapa`, `Esforço`, `Prazo`, `Áreas da vida`,
  `Prioridade`, `Subtarefas`, `Subtarefas relacionadas` e `Tarefa principal`;
  opções antigas como `00. Inbox`, `02. ASAP`, `06. Feito`,
  `Mais rápido possível` e `Concluido` foram substituídas por `Entrada`,
  `Assim que possível`, `Concluída`, `Agora` e `Hoje`; áreas `Money`, `Projects`
  e `Shoppe` viraram `Finanças`, `Projetos` e `Compras`. O front não traduz mais
  rótulos localmente — exibe o que vem de `GET /api/opcoes`.
- [2026-06-26] ✅ **Conteúdo do workspace para IA** — a IA passou a acessar o
  **corpo** das páginas, não só as propriedades. Camada base nova em
  `src/notion_starter/content.py` (conversor puro Markdown ↔ blocos) e métodos de
  blocos no `NotionClient` (`ler_blocos`, `anexar_blocos`, `atualizar_bloco`,
  `excluir_bloco`). Service `server/services/conteudo.py` (cliente injetável)
  orquestra ler/escrever/editar/excluir/buscar. Exposto na CLI (`buscar`,
  `conteudo`, `escrever`, `editar-bloco`, `apagar-bloco --sim`) e no MCP
  (`notion.search`, `notion.read_page_content`, `notion.append_content`,
  `notion.edit_block`, `notion.delete_block`). Escopo: acesso total (inclui
  apagar), em tudo que a integração enxerga. `delete_block` é destrutivo
  (`destructiveHint=True`) e a CLI exige `--sim`. +23 testes (incl. fluxo
  destrutivo); suíte e ruff verdes. Docs: `README`, `docs/MCP.md`.

- [2026-06-26] ✅ **Suporte a data sources + leitura de linhas de database** —
  ao testar a leitura de conteúdo num database real do workspace ("Untitled"),
  descobrimos duas lacunas: (1) `conteudo` num database voltava `markdown: ""`
  em silêncio; (2) databases do modelo novo do Notion (multi-fonte, "data
  sources", 2025) não eram consultáveis pela versão `2022-06-28`. Corrigido:
  `NotionClient` ganhou `listar_data_sources`, `get_data_source` e
  `consultar_data_source` (endpoints `/data_sources/*`, versão `2025-09-03`
  enviada **só** nessas chamadas via override por request — a versão padrão das
  demais rotas não muda). Service `conteudo.listar_linhas` resolve as fontes e
  devolve as linhas normalizadas. CLI ganhou `linhas <database_id>` e o `conteudo`
  num database agora avisa e já traz as linhas; MCP ganhou
  `notion.list_database_rows` e o mesmo aviso em `read_page_content`. Validado no
  database de tarefas real (15 linhas lidas). Nota: o "Untitled" volta vazio
  porque **não está compartilhado** com a integração — é config no Notion, não
  bug. +13 testes; suíte e ruff verdes.

- [2026-06-26] ✅ **Leitura recursiva de conteúdo** — testando a Home real,
  vimos que `conteudo` lia só um nível: os databases dentro de `column_list` e o
  conteúdo de toggles ficavam invisíveis (a Home tinha 7 databases, mas só 3
  apareciam). Agora `ler_blocos(..., recursivo=True)` desce nos blocos com filhos
  (colunas, toggles, blocos sincronizados) e os aninha sob `_filhos`; o conversor
  inclui os filhos e marca databases embutidos como `**[database: Nome]**`.
  `ler_conteudo` passou a ler em profundidade por padrão. Bônus: *custom emojis*
  em títulos (que vinham como `:hash:`) são descartados do Markdown. Validado na
  Home real (7 databases, incl. Estudo/Trabalho/Arquivos/Observações diárias
  dentro de colunas, e a playlist do toggle). +5 testes; suíte e ruff verdes.

- [2026-06-26] ✅ **Intuitividade para IA + start_app em subtelas** — ao ver uma
  IA tatear o workspace com curl em vez de usar a CLI pronta, duas melhorias de
  UX: (1) comando `python -m cli --json guia` que auto-documenta todos os
  comandos (reflete o parser, nunca desatualiza) com descrição e exemplo — o
  primeiro lugar onde a IA deve olhar; (2) `start_app.py` reorganizado de 9 opções
  soltas para 3 categorias (Usar o app / Para IA e integrações / Configurar e
  instalar) + Status + Sair, navegando por subtelas — menos informação de uma vez,
  mais intuitivo, mantendo o mínimo obrigatório do contrato de start app. +4
  testes; suíte (334) e ruff verdes.
- [2026-06-29] ✅ **Gate de qualidade executável** — o padrão de qualidade passou a
  estar materializado no próprio repositório: `scripts/quality_check.py` roda Ruff,
  Pytest, Oxlint e build Vite; `start_app.py` ganhou a ação "Qualidade"; CI passou
  a validar também o front; raiz ganhou `AGENTS.md`; documentação dedicada em
  `docs/QUALIDADE.md`; README/CONTRIBUTING/front README atualizados.
- [2026-06-29] ✅ **Atualização do padrão Felixo absorvida** — releitura da cópia
  local atualizada às 14:05 confirmou novas ênfases operacionais: automação antes de
  edição manual, `IA.md` como linha do tempo preservada, documentação viva durante a
  execução e git direto no `main` por padrão. `AGENTS.md` e `docs/QUALIDADE.md`
  passaram a registrar essas regras explicitamente para próximos mantenedores/agentes.
- [2026-06-29] ✅ **README reescrito para o produto real** — a raiz deixou de vender o
  projeto como `notion-starter-boilerplate` e passou a apresentar `Automações do
  Notion`: menu, SPA React, API Django, CLI/MCP para IA, inventário GitHub, segurança,
  qualidade e documentação. Metadados públicos do `pyproject.toml`, título do menu e
  CONTRIBUTING foram alinhados. Também foi corrigida documentação MCP antiga que ainda
  dizia "sem delete", preservando a política atual: `notion.delete_block` é destrutiva
  e exige confirmação no host. Descrição planejada para GitHub: "Aplicação local para
  operar o Notion com API Django, SPA React, CLI/MCP para IA e inventário GitHub."

Ideias abertas à comunidade: cobertura de mais tipos de propriedade do Notion,
mais tipos de bloco no conversor Markdown (tabelas), escrita de linhas em data
sources, mais exemplos de "Iniciar/Rodar" por fonte de dados (banco, API,
planilha).

---

## 🛠️ STACK & DEPENDÊNCIAS

- [2026-06-24] Runtime: Python 3.10+ (matriz de CI: 3.10–3.13).
- [2026-06-24] Dependência única de runtime do core: `requests>=2.25`.
- [2026-06-24] `typing_extensions>=4.0` apenas em Python < 3.11 (para `NotRequired`).
- [2026-06-25] Servidor (extra opcional `[server]`): `django>=5.0`. Instalar com
  `pip install -e ".[server]"`. O Django não é dependência do core — só do servidor
  em `server/`. SQLite apenas para estado operacional (jobs, locks); o conteúdo
  continua no Notion.
- [2026-06-25] MCP (extra opcional `[mcp]`): `mcp>=1.28,<2`. O servidor
  `server/mcp_server.py` não depende do Django; usa `stdio` por padrão e oferece
  Streamable HTTP somente para depuração local.
- [2026-06-24] Dev: `pytest`, `responses` (mock de HTTP), `ruff`.
- [2026-06-29] Front/dev: `oxlint`, Vite build e gate unificado
  `python3 scripts/quality_check.py`.
- [2026-06-24] Build: `hatchling`. Layout `src/`.

---

## 📐 DECISÕES DE ARQUITETURA

- [2026-06-24] Módulos coesos por responsabilidade: `client` (HTTP), `schema`
  (comparação), `properties` (montagem de payloads), `exceptions`, `logging`,
  `constants`. Evita módulo "faz-tudo".
- [2026-06-25] `inventory` (lógica pura de mapeamento) acompanha essa fronteira:
  recebe dados crus e devolve estruturas, sem tocar em rede. Contagem de linhas de
  database (que exige rede) fica no coletor em `examples/`, não no `inventory`.
- [2026-06-24] Integração externa (Notion) isolada no `client`; o resto do
  core não depende do formato cru do provedor.
- [2026-06-24] Pacote importável é `notion_starter` (era `notion_sync`). Exceções
  ainda derivam de `NotionSyncError` (nome de classe mantido para não multiplicar
  a quebra; quem usar o template pode renomear no fork).
- [2026-06-24] Configuração centralizada em `constants.py` (URL base, timeout,
  versão da API, env var e prefixo do token).
- [2026-06-24] Sem estado global: o token é resolvido por instância de `NotionClient`.
- [2026-06-25] Servidor em `server/` com separação por camadas: `config/` (projeto
  Django), `core/` (config por ambiente, sem HTTP), `integrations/` (adaptador sobre
  o `notion_starter`, sem regra de negócio), `services/` (casos de uso),
  `api/` (borda HTTP, views finas), `operations/` (estado operacional em SQLite).
  Fronteira sagrada: `api` não tem regra de negócio, `services` não conhece HTTP.
- [2026-06-25] Config do servidor centralizada em `core/config.py` (dataclass
  `Config`, imutável, `__repr__` nunca vaza token/secret). Variáveis lidas do
  ambiente / `.env` local. Guarda de produção: `SECRET_KEY` de dev recusada
  quando `DEBUG=0`.
- [2026-06-25] SQLite para estado operacional (modelos `Job` e `Lock`), não para
  conteúdo. A fonte da verdade continua o Notion. O caminho do banco é configurável
  por variável de ambiente (`OPERATIONAL_DB_PATH`).
- [2026-06-25] Camada de IA plugável em `server/integrations/openrouter.py` e
  `server/services/ia.py`. Protocolo `ProvedorIA` (Open/Closed — adicionar provedor
  não mexe no núcleo). Modo copiloto: sugere ação, pessoa confirma antes de escrever.
- [2026-06-25] Front web servido pelo Django: templates em `server/templates/`,
  estáticos em `server/static/`. JS vanilla consumindo a API REST, sem framework de
  front. Rota `/` via `TemplateView`; interações preservam o atributo `hidden` e
  oferecem feedback semântico para tecnologias assistivas.
- [2026-06-25] Retry no `NotionClient` é decidido por semântica, não apenas pelo
  método HTTP: buscas `POST` são idempotentes e podem repetir; criação de database
  ou página só repete 429/529; atualizações `PATCH` que definem estado podem repetir.
  O cache de schema usa relógio monotônico e cópias defensivas.
- [2026-06-25] A borda MCP é um processo independente e fino sobre
  `server/services/tarefas.py`. Os nomes públicos incluem o namespace `notion.*`;
  anotações MCP são hints, enquanto `requiresConfirmation` pertence ao catálogo
  confiável do host Felixo-AI-Core.
- [2026-06-26] A CLI para IA (`cli/`) segue a mesma fronteira da borda MCP: valida
  argumentos, formata saída humana/JSON e delega a `server/services/tarefas.py`.
  Não monta payload cru do Notion. Operações de database (`databases`,
  `escolher-database`) ficam na borda operacional porque só listam/gravam a escolha
  de `NOTION_DATABASE_ID`, sem regra de domínio.
- [2026-06-26] Conteúdo das páginas segue as mesmas 4 camadas: a conversão
  Markdown ↔ blocos é pura (`notion_starter.content`, par de `properties`/
  `readers`); o HTTP de blocos vive no `NotionClient`; a orquestração no service
  `conteudo` (cliente injetável); CLI e MCP são bordas finas. **Decisão de escopo:**
  a IA tem acesso total ao workspace — pesquisar/ler/escrever/editar **e apagar** —
  em tudo que a integração enxerga. Isso muda a política anterior de "nenhuma
  ferramenta apaga": agora há delete, mas guardado — `notion.delete_block` declara
  `destructiveHint=True` (host confirma) e a CLI `apagar-bloco` exige `--sim`. A
  reversibilidade é real: o Notion arquiva o bloco (lixeira), não apaga em definitivo.

---

## 🎨 DECISÕES DE DESIGN & CONVENÇÕES

- [2026-06-24] Código, docstrings e mensagens de erro em português (i18n da lib).
- [2026-06-24] Tipagem forte: `TypedDict` para payloads, `dataclass` para resultados.
- [2026-06-24] Exceções explícitas e capturáveis, todas derivando de `NotionSyncError`.
- [2026-06-24] Commits em Conventional Commits (`feat`/`fix`/`docs`/`refactor`/`chore`).
- [2026-06-24] Logging silencioso por padrão (`NullHandler`), amigável a bibliotecas.

---

## 🧪 TESTES IMPORTANTES

- [2026-06-24] ✅ `tests/test_client.py` — endpoints, paginação e erros HTTP, com
  todo o HTTP mockado via `responses` (sem token real nem rede).
- [2026-06-24] ✅ `tests/test_schema.py` — comparação de schema (ok/faltando/tipo errado).
- [2026-06-24] ✅ `tests/test_properties.py` — montagem dos helpers de propriedade.
- [2026-06-25] ✅ `tests/test_readers.py` (19) — helpers de leitura de propriedade
  (`ler_title/ler_select/ler_status/ler_date/…`, `ler_propriedade`, `extrair_valores`).
- [2026-06-25] ✅ `tests/test_services_tarefas.py` (5) — casos de uso do servidor
  (`listar_tarefas/criar_tarefa/mover_status/concluir_tarefa`), `TaskList` injetada.
- [2026-06-25] ✅ `tests/test_api_tarefas.py` (9) — rotas REST ponta a ponta via
  Django test client (`GET/POST /api/tarefas`, `PATCH /api/tarefas/{id}`), envelope
  de erro (400/404/502/500).
- [2026-06-25] ✅ `tests/test_front.py` (4) — rota `/`, elementos essenciais,
  assets estáticos e regressão do atributo `hidden`.
- [2026-06-25] ✅ `tests/test_client_resiliencia.py` (30) — 409/429/5xx/529,
  `Retry-After`, rede, backoff, política de idempotência, cache TTL/invalidação
  e proteção contra mutação do retorno.
- [2026-06-25] ✅ MCP e projetos: **32 testes focados** cobrindo a superfície
  `notion.*`, validação, anotações, transportes, erros sanitizados e atualização
  de página de projeto.
- [2026-06-26] ✅ `tests/test_start_app.py` (23) — comando filho, seleção de
  terminal, processo independente, ação “Iniciar tudo”, health check, navegador e
  database de tarefas: pergunta sempre ao subir (com o atual pré-selecionado),
  cancelar mantém o atual e sobe, primeira escolha grava, lista todos com marca
  `✓`/`⚠`, confirma ao escolher incompatível, sem-nenhum-compartilhado falha e
  troca pelo menu Configurar (atual marcado `[atual]`).
- [2026-06-26] ✅ `tests/test_cli_notion_tasks.py` — CLI por injeção de doubles,
  cobrindo envelope JSON, listar/ler/criar/editar/mover/concluir/opções, listagem e
  escolha de database, resumo de mapeamento e `main()` sem rede real.
- [2026-06-29] ✅ Suíte completa do working tree compartilhado:
  **427 testes passando**; `ruff check .`, `npm run lint`, `npm run build` e
  `python3 scripts/quality_check.py` limpos.

---

## 🐛 BUGS & FIXES RELEVANTES

- [2026-06-25] BUG: o `display: flex` do overlay podia prevalecer sobre o atributo
  HTML `hidden` e exibir o modal de status antes da interação. FIX: regra global
  `[hidden] { display: none !important; }`, coberta por teste de regressão.
- [2026-06-25] BUG: a primeira implementação de resiliência repetia `POST /pages`
  após 5xx ou falha de rede, podendo duplicar uma página já processada pelo Notion.
  FIX: retry ambíguo restrito a operações explicitamente idempotentes; criações só
  repetem 429/529, com regressão cobrindo página e database.
- [2026-06-25] BUG (isolamento de teste): os testes de seleção de database em
  `test_start_app.py` deixavam `NOTION_DATABASE_ID` vazado em `os.environ` (a
  produção escreve `os.environ[...]` e o teste só fazia `delenv` antes). Como
  `test_api_tarefas` usava `os.environ.setdefault`, herdava o valor vazado e a
  query ia para um database sem mock → `test_get_tarefas_lista` falhava com 502
  na suíte completa (passava isolado). FIX: os testes adotam a chave via
  `monkeypatch.setenv` (revertido no teardown) e `test_api_tarefas` fixa seu
  token/database por teste com `setenv`, sem depender da ordem da suíte.

---

## 🔗 INTEGRAÇÕES & SERVIÇOS EXTERNOS

- [2026-06-24] API do Notion (`https://api.notion.com/v1`). Autenticação por token
  de integração (`NOTION_TOKEN`, prefixo `ntn_`). Header `Notion-Version` fixado
  em `constants.py`. Nenhum segredo versionado — veja `.env.example`.
- [2026-06-25] O servidor consome o Notion via `server/integrations/notion.py` —
  fábrica fina que cria `NotionClient`/`TaskList` a partir da config do ambiente
  (`core/config.py`). `services/` usa a `TaskList` como dependência injetável;
  em testes, injeta-se um mock sem precisar de token nem de Django.
- [2026-06-25] OpenRouter via `server/integrations/openrouter.py` — catálogo de
  modelos com cache 24 h, chat completions. Chave via `OPENROUTER_API_KEY` (env).
- [2026-06-25] MCP Python SDK 1.x via `server/mcp_server.py`. O catálogo do
  Felixo-AI-Core possui a camada `notion` e marca as quatro ferramentas de escrita
  com `requiresConfirmation: true`; a conexão operacional de servidores externos
  permanece no roadmap do cliente MCP do host.

---

## 📝 NOTAS GERAIS

- [2026-06-24] A pasta `Padrão de qualidade - Felixo System Design/` é referência de
  padrões e está no `.gitignore`; não faz parte do pacote distribuído.
- [2026-06-26] `mapa.json` e `mapa.html` são artefatos gerados localmente pelos
  exemplos de mapeamento do workspace. Não devem ser versionados, porque podem conter
  URLs/títulos reais de páginas do Notion; gere novamente com `python start_app.py` ou
  pelos scripts em `examples/`.
- [2026-06-24] O projeto tem exemplos executáveis, então o `start_app.py` se aplica
  (o padrão exige menu de entrada para todo programa rodável, incluindo CLI/automação).
  O menu instala, configura o token, mostra status e roda os exemplos. Não é empacotado
  no wheel — é só a porta de entrada local do repositório.
- [2026-06-24] É um TEMPLATE: o caminho de uso primário é clonar e adaptar (renomear o
  pacote, definir o schema, trocar a fonte de dados), não `pip install` de PyPI.
- [2026-06-25] O servidor (`server/`) é opcional — o core (`notion_starter`) continua
  independente de framework. O `start_app.py` ganhou a ação "Subir servidor" (instala
  extras, pergunta host:porta, aplica migrações, sobe `runserver`). Detalhes de
  estrutura, config e deploy em `docs/INFRA.md`.

---

## 🧠 RESUMOS DE DECISÃO

[2026-06-24] CONTEXTO: Alinhar o repositório ao padrão de qualidade Felixo System Design.
ALTERNATIVAS: Reescrever a arquitetura do código vs. manter o código (já modular,
tipado e testado) e focar nos artefatos de documentação ausentes.
DECISÃO: Manter o código — ele já atende ao design system de backend (modularização,
contratos estáveis, testes, segredos fora do repo). Adicionados os artefatos que
faltavam: `IA.md`, `CONTRIBUTING.md`, `.env.example`, um README no formato Felixo e,
por fim, o `start_app.py` (único item obrigatório que ainda faltava — antes tido como
não aplicável, mas o padrão exige menu de entrada para todo programa rodável).
VALIDAÇÃO: `pytest -q` (22 passados) e `ruff check .` (limpo) após as mudanças; menu
verificado renderizando o Status e com lint limpo no `start_app.py`.

[2026-06-24] CONTEXTO: O nome "notion-sync" prometia sincronização que o código não faz;
o projeto era um módulo interno e o autor decidiu abri-lo como ponto de partida para
projetos sobre o Notion.
ALTERNATIVAS: (a) manter como biblioteca e só renomear; (b) virar template puro
(clone/adapte, fora de PyPI); (c) híbrido instalável.
DECISÃO: Template puro chamado `notion-starter-boilerplate`, pacote `notion_starter`.
Reescritos README/CONTRIBUTING/IA.md no enquadramento de boilerplate e adicionado o
exemplo end-to-end `sync_from_csv.py` (lê CSV → valida schema → cria páginas), que dá
ao starter um fluxo completo para a pessoa adaptar. Trabalho feito em branch
(`refactor/reposiciona-como-boilerplate`) por ser refatoração significativa, conforme a
política de git.
VALIDAÇÃO: `pytest -q` (22 passados) e `ruff check .` (limpo) após o rename e os novos
artefatos; `pip install -e ".[dev]"` reinstalado com o pacote `notion_starter`.

[2026-06-25] CONTEXTO: Fechar as Fases 3-4 com fontes externas sem duplicar páginas ou
tarefas em reprocessamentos.
ALTERNATIVAS: Escrita direta por fonte; sincronização sempre aditiva; ou contratos
normalizados com idempotência antes da escrita.
DECISÃO: Isolar HTTP em `integrations/github.py`, modelar fontes pelo protocolo `Fonte`
e usar `Origem`/URL/título da tarefa como chaves de reconciliação. Repositórios privados
só entram quando o token pertence ao usuário consultado.
VALIDAÇÃO: 52 testes focados verdes, `ruff` limpo, compileall e diff-check; commit
`d643894`. Guia operacional em `docs/INTEGRACOES.md`.

[2026-06-28] CONTEXTO: Database "todolist" da HOME do usuário aparecia linkado a um
database da Vitis Souls (Tasks/AI Core), misturando tarefas pessoais, da Vitis e da LM
Consultoria. A casca embutida na HOME estava sem título ("Untitled") e vazia; as 15
tarefas reais moravam numa fonte única compartilhada. Necessidade: um database pessoal
isolado, com as MESMAS propriedades da origem, sem vínculo com a Vitis.
ALTERNATIVAS: (a) separar linhas na UI (preserva tudo, manual); (b) copiar linhas por
código (perde vínculos); (c) automatizar a clonagem de schema+linhas num comando.
DECISÃO: Criar `services/clonagem.clonar_database` + comando CLI `clonar-database` e tool
MCP `notion.clone_database`. Fluxo do modelo novo: cria database com a propriedade title
(o data source exige uma), faz PATCH no data source com o schema completo, e cria linhas
com parent `data_source_id`. Relações auto-referentes (apontavam para a própria fonte)
viram auto-relações do clone; relações externas (ex.: "Áreas da vida") são preservadas;
`status`/`select` recriam opções; campos automáticos (created_time, rollup, formula…)
não recebem valor ao copiar. Novos métodos no client: `atualizar_data_source` e
`criar_pagina_em_fonte`, ambos na versão 2025-09-03.
VALIDAÇÃO: 375 testes verdes (test_services_clonagem com 13 casos cobrindo auto vs
externa, status, cópia de linhas e erros; +CLI/MCP/client), ruff limpo, e teste real
contra o workspace (clone com as 14 propriedades idênticas, relações corretas, depois
arquivado). LIÇÃO: nunca apagar database da HOME sem confirmação visual — leitura "vazia"
pode ser view linkada; e validar diagnóstico antes de afirmar (as relações eram da home,
não da Vitis).

[2026-06-28] CONTEXTO: Revisão de qualidade do código contra o Felixo System Design
(Guia Mínimo + DESIGN_SYSTEM_BACKEND + política de git), com autorização para refatorar
conexão Notion/CLI/MCP onde necessário.
ALTERNATIVAS: (a) só rodar linters; (b) refatorar tudo de uma vez numa branch grande;
(c) refatorações pequenas e coesas direto no main, uma por commit, guiadas pelos
princípios de separação de camadas e DRY.
DECISÃO: Caminho (c), seguindo a política de git (commits pequenos `tipo: descrição` no
main, sem branch — eram refatorações seguras sem mudança de comportamento). Dois desvios
do padrão corrigidos: (1) ~280 linhas de regra de negócio de `normalizar-nomes` viviam na
borda CLI (controller gordo) -> movidas para `services/normalizacao.py` com cliente
injetável; CLI virou controller fino. (2) CLI e MCP duplicavam o fallback de detecção
"página vs database" -> centralizado em `services.conteudo.ler_pagina_ou_database`, com
`tipo` explícito no contrato. Revisão confirmou que client/integrations, api/views e os
demais services já respeitavam as fronteiras (sem HTTP/Django vazando para services, sem
módulos faz-tudo além dos dois tratados). `client.py` (1011 linhas) foi mantido: é um
boundary HTTP coeso e bem seccionado, não um faz-tudo — dividir fragmentaria sem ganho.
VALIDAÇÃO: 382 testes verdes (de 375; +7 dos novos services), `ruff check` limpo
inclusive com F/B/UP. CLI: 968 -> 632 linhas. Commits: `feat` (clonar-database),
`refactor` (normalizacao), `refactor` (detecção página/database).

[2026-06-28] CONTEXTO: O site (front React) só renderizava databases no schema fixo de
tarefas (Etapa/Esforço/Áreas) — não mostrava qualquer outro database. Pedido: mostrar
qualquer database, do jeito mais simples, focando na todolist principal, começando
read-only.
ALTERNATIVAS: (a) reescrever o app de tarefas para ser genérico; (b) views ricas
inferidas por database; (c) manter o app de tarefas e adicionar uma aba "Explorar"
read-only genérica.
DECISÃO: Caminho (c), o mais simples e sem risco para a todolist. Backend: novo serviço
read-only `services/exploracao.py` que descobre colunas de qualquer database e achata cada
linha em `coluna -> texto`, convertendo todo tipo do Notion (status, relation->"N
vínculo(s)", date, multi_select, formula…) sem quebrar; endpoints `GET /api/databases` e
`GET /api/databases/<id>`. Front: aba "Explorar" (seletor + tabela genérica) ao lado de
"Tarefas"; o app de tarefas foi extraído para `PainelTarefas` e segue intacto como aba
padrão. Escrita genérica ficou de fora de propósito (é o passo complexo) — convite a
contribuição futura.
VALIDAÇÃO: 388 testes Python verdes (+6 de exploração), ruff limpo; front com oxlint
limpo e build OK; teste end-to-end com Django real: `/api/databases` listou 113
databases e `/api/databases/<todolist>` trouxe 14 colunas e 12 linhas corretas; regressão
do endpoint de tarefas conferida. Commits: `feat` (API exploração), `feat` (aba Explorar).

[2026-06-29] CONTEXTO: Pedido de materializar um inventário de repositórios GitHub de
várias contas em um database do Notion, com propriedades úteis e o README de cada repo
dentro de uma subpágina filha (para a linha do database ficar organizável).
ALTERNATIVAS: (a) reusar `services/sincronizar_github` (orientado a *tarefas*, exige
tasklist, não materializa inventário); (b) script pontual fora do código; (c) novo
serviço reutilizável de inventário sobre o `GitHubClient` e o `NotionClient` existentes.
DECISÃO: Caminho (c). Novo `services/inventario_github.py` com `garantir_database`
(cria o database) e `exportar_repos` (multi-conta, upsert sem duplicar). README vai para
uma subpágina filha "README", não para o corpo da linha. Para isso, três peças
reutilizáveis: (1) `RepoInfo` enriquecido (dono, issues, observadores, tamanho, fork,
arquivado, licença, último push); (2) `NotionClient.criar_subpagina` (página filha, com
quebra automática em lotes de 100 blocos); (3) fix em `content.py` normalizando a
linguagem de blocos de código para um valor aceito pelo Notion — antes, READMEs com
cercas de código em linguagem fora da lista do Notion falhavam com HTTP 400.
VALIDAÇÃO: 407 testes verdes (+24: inventário, criar_subpagina, normalização de
linguagem, campos novos do RepoInfo), `ruff check` limpo. Teste real: database "GITHUB"
criado na HOME pessoal com 85 repositórios das contas Felipe-Alcantara (inclui privados,
via token próprio) e flaviavs-commits; READMEs exportados em subpágina por repo (só os
repos sem README no GitHub ficam sem subpágina). Commits: `feat` (RepoInfo),
`feat` (criar_subpagina), `fix` (linguagem de código), `feat` (serviço de inventário).

[2026-06-29b] CONTEXTO: Os READMEs importados apareciam como Markdown cru no Notion
(badges, divs HTML, links literais) porque o conversor era plaintext puro; e não havia
como manter o inventário em dia (atualizar repos novos/renomeados, README/estrelas).
DECISÃO: (1) Conversor `content.py` agora é **rico**: parser inline (negrito, itálico,
código, ~~tachado~~, `[link](url)`) com annotations/link; imagens e badges viram blocos
`image`; tabelas viram blocos `table`; HTML de layout (`div/center/br/a/img/h1-6`) é
convertido/limpo preservando o conteúdo; headings 4-6 → heading_3; setext suportado. O
reverso `blocos_para_markdown` reconstrói tudo (round-trip). Blocos de código seguem crus
(sem parse inline). (2) `services.inventario_github.atualizar_repos`: cria repos novos,
atualiza propriedades dos existentes e **substitui a subpágina README só quando muda**,
detectado por hash na coluna `README hash` (sem reler blocos). Coleta multi-conta extraída
para `_coletar_repos` (compartilhada com `exportar_repos`). (3) Comando CLI
`atualizar-github` (--contas/--database/--sem-readme) + opção "Atualizar inventário GitHub"
no `start_app.py`. DETALHE TÉCNICO: o limite de 2000 do Notion é por item de rich_text e
contado em UTF-16; o fatiamento preserva annotations/link em cada fatia.
VALIDAÇÃO: 435 testes verdes (+16 conversor, +6 update, +4 CLI), `ruff` limpo. Teste real:
re-renderização dos READMEs do database GITHUB (badges como imagem, links clicáveis,
negrito aplicado); rodar `atualizar-github` de novo não recria README sem mudança.
Commits: `feat` (conversor rico), `feat` (atualizar_repos), `feat` (CLI + start_app),
`docs`.

[2026-06-30] CONTEXTO: Execução da task "Testar o programa das automações", focada na
frente web do repositório com a database `Tarefas — HOME (pessoal)` como caso principal
de uso real. O objetivo foi validar bootstrap local, fluxo principal de tarefas e atritos
de produto antes de qualquer expansão para outras tabelas.
ACHADOS: (1) o `.env` local estava apontando para `Tarefas — HOME (principal)`, enquanto a
task vive em `Tarefas — HOME (pessoal)`; isso confirmou que a web ainda precisa expor com
clareza qual database está ativa. (2) leitura, filtros, criação e edição funcionaram na
base pessoal tanto pela API local quanto pelo proxy do front. (3) o caminho recomendado
`python3 start_app.py --action tudo` quebrava em ambiente Python externamente gerenciado,
mesmo com `.venv` pronta. (4) as respostas de `POST/PATCH` de tarefas voltavam com
`areas_nomes` vazio, enquanto `GET /api/tarefas` vinha enriquecido.
DECISÃO: corrigir nesta task o que afeta diretamente o uso real e o contrato público, sem
abrir uma refatoração ampla. O `start_app.py` agora relança a si mesmo no Python do `.venv`
quando ele existe, e as ações filhas passam a usar esse executável do projeto. No core,
`TaskList.criar/editar` agora enriquecem `areas_nomes` antes de devolver a tarefa. Os
achados e prioridades do teste foram registrados em `docs/TESTE-WEB-2026-06-30.md`.
VALIDAÇÃO: teste real com backend em `127.0.0.1:8000` e front em `127.0.0.1:5173`, usando
override de `NOTION_DATABASE_ID` para a database pessoal; `GET /api/health`, `GET /api/tarefas`,
`GET /api/opcoes`, filtros por `status/duracao/area`, criação e edição via API direta e via
proxy do Vite; `python3 start_app.py --action status` passou a refletir Django disponível;
testes automatizados verdes (`tests/test_start_app.py`, `tests/test_tasks.py`,
`tests/test_services_tarefas.py`) e documentação viva atualizada.

[2026-06-30b] CONTEXTO: Após a primeira rodada do teste web, ficou explícito um risco de uso:
a pessoa podia operar a interface de tarefas sem confirmação visível de qual database estava
ativa, num projeto que já convive com `Tarefas — HOME (pessoal)`, `principal`, cópias e
outras tabelas próximas.
DECISÃO: transformar esse contexto em contrato público da API em vez de esconder a solução no
front. Foi criado `GET /api/database-atual`, que devolve `id`, `titulo` e `url` da database de
tarefas ativa. O painel principal do front passou a mostrar a database corrente e oferecer o
link "Abrir no Notion" para conferência imediata.
VALIDAÇÃO: testes novos cobrindo a borda HTTP (`tests/test_api_tarefas.py`) e a fiação do front
(`tests/test_front.py`); suíte afetada verde (`77 passed`) com Ruff e Oxlint limpos. A melhoria
também atualizou `docs/CONTRATOS.md`, `front/README.md` e o relatório
`docs/TESTE-WEB-2026-06-30.md`.

[2026-06-30c] CONTEXTO: Ao comparar as duas tabelas reais no Notion, ficou claro que a
ambiguidade restante não era só de seleção, mas também de comunicação no terminal: a CLI
`database-atual` mostrava apenas o ID, e o `start_app.py` ainda confirmava "database atual"
sem reforçar o título real retornado pelo Notion.
DECISÃO: eliminar nomes implícitos no terminal. A CLI `database-atual` agora resolve a
database no Notion e exibe `titulo + id + url`; o `start_app.py` passou a mostrar o título real
nas mensagens de manter/salvar database, em vez de só truncar o ID.
VALIDAÇÃO: testes atualizados em `tests/test_cli_notion_tasks.py` e `tests/test_start_app.py`,
mais a suíte focada `tests/test_start_app.py tests/test_cli_notion_tasks.py tests/test_api_tarefas.py
tests/test_front.py` verde (`87 passed`) e gate completo executado ao final da rodada.

[2026-06-30d] CONTEXTO: Mesmo após expor `titulo + id + url`, a UX do `start_app.py`
continuava poluída por um texto auxiliar de exemplo (`Ex.: ...`) no momento exato em que a
pessoa precisava validar qual era a database real. Na prática, o exemplo desviava a atenção
do problema central: conferir nome, ID e link da tabela apontada.
DECISÃO: simplificar a seleção para informação autoritativa apenas. O `start_app.py` deixou de
mostrar exemplos de tarefas nesse fluxo e passou a imprimir, antes da pergunta, uma lista
objetiva das databases compatíveis com `título pela API do Notion + ID completo + URL`.
As opções do seletor também passaram a usar o ID completo, sem rótulos paralelos.
VALIDAÇÃO: regressão coberta em `tests/test_start_app.py`, incluindo a garantia explícita de que
`Ex.:` não volta a aparecer; `ruff check start_app.py tests/test_start_app.py`, a suíte focada
de `tests/test_start_app.py` e o gate completo do repositório foram executados nesta rodada.

[2026-06-30e] CONTEXTO: O usuário confirmou que o site abria uma tabela diferente da URL
esperada (`30296e2d-cd39-4cf3-8bbd-3fb2f53c0195`). A investigação mostrou que o `.env`
local ainda estava apontando para `1fe91f95-497e-813f-9892-cfa80d4fd341`, enquanto o link
informado era da database pessoal. Também havia uma lacuna de diagnóstico: a UI e o terminal
mostravam o título do database, mas não o nome da *data source* usada pelo modelo novo do
Notion.
DECISÃO: corrigir o `.env` local para `30296e2d-cd39-4cf3-8bbd-3fb2f53c0195` e ampliar o
contrato de `GET /api/database-atual`/`cli database-atual` para incluir `data_sources`. O
front e o `start_app.py` agora exibem a fonte de dados junto de título, ID e URL, reduzindo
a ambiguidade entre database, data source e view aberta no Notion.
VALIDAÇÃO: `python3 -m cli database-atual` retornou `Tarefas — HOME (pessoal)`,
`30296e2d-cd39-4cf3-8bbd-3fb2f53c0195`, data source `Tarefas — HOME (pessoal)` e URL do
mesmo ID; suíte focada (`tests/test_start_app.py tests/test_cli_notion_tasks.py
tests/test_api_tarefas.py tests/test_front.py`) verde com `65 passed, 2 skipped`, e Ruff
focado limpo antes do gate completo.

[2026-06-30f] CONTEXTO: Finalização da task "Testar o programa das automações". A sessão
anterior identificou que o problema principal era de configuração (`.env` apontando para
o database errado) combinado com ambiguidade de contexto (título vs data source). Após a
correção do `.env` local para `30296e2d-cd39-4cf3-8bbd-3fb2f53c0195` e a ampliação de
`GET /api/database-atual` para incluir `data_sources`, foi necessário executar o gate de
qualidade completo e registrar a conclusão da task no Notion.
DECISÃO: rodar `python3 scripts/quality_check.py` para validação final antes do registro.
O gate completo passou: Ruff limpo, 433 testes passando com 2 skipped, Oxlint limpo e
build Vite bem-sucedido. A task foi atualizada no Notion com registro técnico dos três
problemas corrigidos: (1) `.env` local apontando para database errado; (2) campo
`data_sources` ausente nos endpoints de database atual; (3) validação completa executada
com 433 testes verdes.
VALIDAÇÃO: gate completo aprovado. Referências principais: `server/services/tarefas.py:110`
(método `obter_database_atual` com resolução de data sources), `start_app.py:640` (exibição
de data source na seleção de database), `front/src/components/tarefas/painel-tarefas.jsx:232`
(hook `useDatabaseAtual` e exibição no painel). Documentação viva atualizada:
`docs/TESTE-WEB-2026-06-30.md` com registro completo da rodada de teste, `docs/CONTRATOS.md`
com novo endpoint `GET /api/database-atual`, README principal com instruções atualizadas de
variáveis de ambiente e validação. IA.md preservado como linha do tempo completa do projeto.

[2026-07-06] CONTEXTO: Rodada de padronização do hub segundo o Felixo System Design
("Padrão de qualidade"). O hub tinha diretórios fantasma remanescentes da divisão do
monorepo (`cli/`, `server/`, `src/`, `tests/` contendo apenas `__pycache__`), caches de
tooling (`.pytest_cache/`, `.ruff_cache/`) e o `operacional.sqlite3` (estado do app antigo,
gitignorado) na raiz — ruído que não pertence a um repositório que é só documentação e
roteamento. O README já era forte, mas faltavam seções obrigatórias do padrão de README.
DECISÃO: (1) remover o resíduo local do monorepo, deixando na raiz apenas docs + roteamento
+ ferramentas de bootstrap (`bootstrap.py`, `sync.py`, `check-dev.py`); (2) completar o
README com as seções ⭐ obrigatórias que faltavam — Índice, Estrutura do Projeto (árvore do
hub), Autor e o rodapé de Contribuições + CTA — e padronizar o header (badges
`for-the-badge`, descrição em negrito, links rápidos). Não alterei a titularidade do
`LICENSE` (copyright "André Gustavo" difere do autor Git "Felipe Martin"): mudança de
titularidade de licença é decisão do dono, fica registrada aqui como pendência a confirmar.
VALIDAÇÃO: âncoras do Índice conferidas contra os cabeçalhos `##` do README; `git status`
antes da limpeza estava limpo (o resíduo era não rastreado/ignorado, então a remoção não
afeta o histórico versionado). Nenhum código foi tocado — funcionalidade continua vivendo
nos módulos, conforme AGENTS.md.

[2026-07-06b] CONTEXTO: Ergonomia de desenvolvimento dos módulos (task "verificar se está
fácil tanto para uso quanto para desenvolvimento"). Observado que os módulos estavam
clonados em DOIS lugares — em `modules/` (cópia feita pelo bootstrap dentro do hub) e na
pasta acima (`../notion-starter`, `../notion-tasks-cli`, `../notion-workspace-app`), mesmos
remotes e commits. O `bootstrap.py` antigo sempre criava a cópia dentro do hub, ignorando o
clone que já existia, gerando duplicação e ambiguidade sobre "onde eu desenvolvo".
DECISÃO: `bootstrap.py` passa a reusar o clone existente. Ordem de preferência por módulo:
(1) já preparado em `modules/<nome>` → `git pull --ff-only`; (2) já clonado em `../<nome>` →
cria um LINK em `modules/<nome>` apontando para lá (junction no Windows via `mklink /J`, que
não exige admin; symlink no POSIX), reusando o mesmo working copy; (3) não existe →
`git clone` do GitHub. `modules/<nome>` segue sendo o caminho canônico de dev, então
check-dev.py e todo o roteamento do AGENTS.md continuam válidos sem mudança — o `.git` é
resolvido através do link. Escolhi o link (em vez de "só usar ../<nome>") para não quebrar
nada que já aponta para `modules/`.
VALIDAÇÃO: removido `modules/`, rodado `python bootstrap.py` → detectou os três clones em
`../` e criou junctions (confirmado por `os.path.realpath('modules/notion-starter')` →
`...\Github\notion-starter`); `git pull --ff-only` rodou dentro de cada link ("Already up to
date"); `python check-dev.py` reporta os três `[OK]` (o `.git` é encontrado através da
junction). Docs vivas atualizadas no mesmo passo: README (seção "Primeiro passo") e AGENTS.md
(pré-requisito bootstrap).

[2026-07-06c] CONTEXTO: Lote de tarefas de uso/dev vindas de agentes que operavam o Notion:
(1) "resolver as propriedades" — ao editar uma página que é linha de database, os agentes só
mexiam no conteúdo (blocos), nunca nas propriedades, a menos que explicitados; (4) proposta de
um comando "editar-linha" no notion-tasks-cli (o CLI cobria conteúdo e tarefas, mas não editava
propriedades de linhas genéricas, forçando ir à API crua com o token do hub); (3) tornar o
append de conteúdo seguro (preservar o existente, respeitar limites, verificar pós-PATCH).
DECISÃO: as tarefas 1 e 4 têm a mesma raiz — faltava um caminho de propriedades para linha
genérica. Adicionado `NotionClient.obter_pagina` no notion-starter (GET /pages/{id} já traz o
`type` de cada coluna) e o comando `editar-linha <page_id> --set "Nome=valor"` no
notion-tasks-cli (`services/propriedades.py`), que infere o tipo da própria página, converte o
valor (title, rich_text, number, checkbox, select, status, multi_select, relation, people, date
com intervalo "inicio..fim", email, phone, url), limpa com valor vazio e recusa tipos calculados.
O `--help`/guia passou a recomendar "comece pelas propriedades, depois o conteúdo" — atacando a
raiz da tarefa 1 (agora há caminho e ele é o recomendado). Tarefa 3: `escrever_conteudo` passou a
anexar em lotes de 100 (limite do Notion por requisição; o limite de 2000 chars/rich_text já era
tratado por `content.py` na lib) e a confirmar, pela resposta da API, que todos os blocos foram
criados (erro em escrita parcial); o append sempre entra ao final, preservando o existente. A
correção de conteudo.py foi espelhada em notion-workspace-app/server (camada services duplicada).
VALIDAÇÃO: notion-starter 21/21 testes; notion-tasks-cli 72/72 (incl. novos test_services_
propriedades e test_services_conteudo, e casos de editar-linha no test_cli); notion-workspace-app
test_services_conteudo 12/12 (novo teste de lotes via callback do `responses`). Smoke test:
`python -m cli editar-linha --help` e `guia` mostram o comando e a nova dica. Os três repos foram
commitados e publicados no main. PENDÊNCIA de runtime: o notion_starter instalado (site-packages,
via git+https) ainda não tem `obter_pagina` — é preciso reinstalar a dependência para o
`editar-linha` funcionar em execução real (os testes usam doubles e não dependem disso).

[2026-07-06d] CONTEXTO: Ao atualizar o relatório diário no Notion (database "Relatórios
diários"), caí exatamente no vício da tarefa 1: atualizei o CONTEÚDO (blocos, via `escrever`)
e esqueci as PROPRIEDADES (colunas rich_text "O que fiz", "Resumo", "Próximos passos"). O
usuário apontou. Além disso pediu que a PRÓPRIA ferramenta recomende, de forma explícita,
mexer nas propriedades primeiro e no conteúdo depois.
DECISÃO: (1) Atualizei as propriedades preservando o conteúdo original — peguei os objetos
rich_text originais de cada coluna e anexei um item novo ao final (respeitando o teto de 2000
unidades por item), via `atualizar_pagina`; isso é exatamente o comportamento que a tarefa 3
descrevia para rich_text. (2) Reforcei o guia do CLI: novo campo estrutural
`fluxo_recomendado` (guia --json e humano) com a REGRA "propriedades primeiro (editar-linha),
conteúdo depois (escrever)", e os `--help` de `editar-linha` e `escrever` passaram a apontar a
ordem. Commit `feat` no notion-tasks-cli (add8e33), com teste garantindo a ordem no guia.
LIMITAÇÃO REGISTRADA (próximo passo): o comando `editar-linha` faz FULL-REPLACE do valor e o
builder `properties.rich_text` cria um único item — ou seja, não fatia texto >2000 nem anexa
preservando o existente. Para colunas rich_text longas (como as do relatório) hoje é preciso ir
via `atualizar_pagina` montando o array. Ideia: dar ao `editar-linha` um modo "append" e fazer
o builder de rich_text fatiar em ≤2000 como o `content.py` já faz para blocos.
VALIDAÇÃO: notion-tasks-cli 74/74 testes; guia humano mostra o fluxo em destaque; relatório
06/07 conferido via API — "O que fiz" (6932 chars, 5 itens: 4 originais + 1 novo), "Resumo"
(2064, 2 itens) e "Próximos passos" (1355, 2 itens) com o texto original íntegro no início e a
seção Automações do Notion ao final; Status/Área/Data mantidos.

[2026-07-06e] CONTEXTO: Fechar a lacuna registrada em [2026-07-06d]: o `editar-linha` fazia
full-replace e não fatiava rich_text >2000, então atualizar propriedades longas (como as do
relatório) exigia montar o array via API na mão. Pedido: deixar tudo preparado para uso da
forma mais otimizada, seguindo o padrão.
DECISÃO: (1) Na lib (notion-starter): centralizei a fatia UTF-16 em `utils.fatiar_utf16` e o
teto em `constants.MAX_RICH_TEXT` (antes privados em content.py — agora reusados sem duplicar,
content.py passou a importá-los), e os builders `properties.title`/`rich_text` passaram a
fatiar texto >2000 em vários itens que o Notion concatena. Texto curto segue gerando 1 item
(compatível). (2) No CLI (notion-tasks-cli): `editar-linha` ganhou `--append "Nome=texto"`, que
acrescenta ao final de colunas de texto preservando os itens rich_text originais (lê via
obter_pagina, limpa os itens para forma gravável, junta o texto novo fatiado, num único PATCH);
`--set` segue substituindo. Valida conflito set+append na mesma coluna e append em coluna não
textual. O append NÃO apara espaços (preserva o separador \n\n), diferente do --set.
(3) Dev: instalei o notion-starter em modo EDITÁVEL apontando para o clone local (via o junction
de modules/), então mudanças na lib valem na hora para o CLI, sem reinstalar do git a cada vez —
o setup de desenvolvimento mais otimizado, alinhado ao fluxo de junctions do bootstrap.
VALIDAÇÃO: notion-starter 171/171 (novos testes de fatia: 4500 chars→[2000,2000,500], emoji
conta 2 unidades UTF-16, vazio→1 item); notion-tasks-cli 79/79 (append preserva original,
fatia em 2000, erro em coluna não-texto, erro set+append na mesma coluna, set+append juntos em
colunas diferentes). End-to-end real na Notion: `editar-linha <relatório> --append "Resumo="`
(no-op) reenviou os itens originais e o Resumo continuou com 2 itens/2064 chars — preservação
confirmada sem poluir. Commits e push: notion-starter (d278d3d), notion-tasks-cli (ad2e52a).
