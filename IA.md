# 🤖 IA.md — Contexto operacional do projeto

> **O que é**: Memória técnica do projeto para retomada de contexto por IA ou por
> um novo mantenedor, sem precisar reler todo o código ou o histórico de conversa.
> Baseado no template de contexto do Felixo System Design.

---

## 🎯 OBJETIVO DO PROJETO

[2026-06-24] `notion-starter-boilerplate` é um boilerplate/template open source para
iniciar projetos sobre a API do Notion. Traz um cliente Python tipado, helpers de
propriedade, validação de schema e exceções claras como base pronta para clonar e
adaptar. Independente de framework, uma única dependência de runtime (`requests`).
Público: desenvolvedores que vão começar uma integração com o Notion.
Distribuição: como TEMPLATE (clone/"Use this template" e renomeie), não como pacote
PyPI fechado. O `pyproject.toml` segue funcional para `pip install -e` local.

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

Ideias abertas à comunidade: cobertura de mais tipos de propriedade do Notion,
suporte a blocos, mais exemplos de "Iniciar/Rodar" por fonte de dados
(banco, API, planilha).

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
- [2026-06-25] ✅ `tests/test_start_app.py` (8) — comando filho, seleção de
  terminal Linux, processo independente, fallback sem emulador e novo console Windows.
- [2026-06-25] ✅ Suíte completa do working tree compartilhado:
  **246 testes passando**; `ruff` limpo e `manage.py check` sem problemas.

---

## 🐛 BUGS & FIXES RELEVANTES

- [2026-06-25] BUG: o `display: flex` do overlay podia prevalecer sobre o atributo
  HTML `hidden` e exibir o modal de status antes da interação. FIX: regra global
  `[hidden] { display: none !important; }`, coberta por teste de regressão.
- [2026-06-25] BUG: a primeira implementação de resiliência repetia `POST /pages`
  após 5xx ou falha de rede, podendo duplicar uma página já processada pelo Notion.
  FIX: retry ambíguo restrito a operações explicitamente idempotentes; criações só
  repetem 429/529, com regressão cobrindo página e database.

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
