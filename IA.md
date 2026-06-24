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

Ideias abertas à comunidade: cobertura de mais tipos de propriedade do Notion,
helpers de leitura (extrair valores de páginas), suporte a blocos, mais exemplos
de "Iniciar/Rodar" por fonte de dados (banco, API, planilha).

---

## 🛠️ STACK & DEPENDÊNCIAS

- [2026-06-24] Runtime: Python 3.10+ (matriz de CI: 3.10–3.13).
- [2026-06-24] Dependência única de runtime: `requests>=2.25`.
- [2026-06-24] `typing_extensions>=4.0` apenas em Python < 3.11 (para `NotRequired`).
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
- [2026-06-24] ✅ Suíte completa: 22 testes passando; `ruff check .` limpo.

---

## 🐛 BUGS & FIXES RELEVANTES

_Nenhum bug relevante registrado até o momento._

---

## 🔗 INTEGRAÇÕES & SERVIÇOS EXTERNOS

- [2026-06-24] API do Notion (`https://api.notion.com/v1`). Autenticação por token
  de integração (`NOTION_TOKEN`, prefixo `ntn_`). Header `Notion-Version` fixado
  em `constants.py`. Nenhum segredo versionado — veja `.env.example`.

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
