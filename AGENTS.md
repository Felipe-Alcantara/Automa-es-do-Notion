# AGENTS.md — Roteamento para agentes

Este é o **mapa de roteamento** de pedidos para módulos. Leia isto **toda vez** que receber um pedido.

## Pré-requisito: bootstrap.py

Antes de qualquer coisa, verifique se `modules/` existe com os três repositórios:

```bash
python bootstrap.py
```

Se `modules/` não existe, rode isso. Se existe, `git pull` os módulos. Sem este passo, você não acessa o código dos módulos.

O `bootstrap.py` **reusa clones existentes**: se um módulo já estiver clonado na pasta acima (`../<nome>`), ele cria um link (junction no Windows, symlink no POSIX) em `modules/<nome>` apontando para lá, em vez de duplicar. Ou seja, `modules/<nome>` é sempre o caminho de dev — editar/testar/commitar ali escreve no clone real. Só clona do GitHub o que não existe em lugar nenhum.

---

## Dois modos de operação

### MODO USO — operar o Notion via CLI

O pedido é: *criar tarefa, ler página, mapear workspace, buscar dados, sincronizar…*

**Ação:** instale uma vez (`pip install notion-tasks-cli`), depois execute comandos.

```bash
notion-tasks listar
notion-tasks criar --titulo "..."
notion-tasks conteudo <id>
```

Não precise de módulos locais. O CLI já tem tudo pronto. Ver `--help` para o guia completo (escrito para IAs).

### MODO DESENVOLVIMENTO — modificar código das ferramentas

O pedido é: *corrigir bug, adicionar comando, mudar frontend, melhorar resilência…*

**Pré-requisito:** `python bootstrap.py` (primeiro). Sem isso, `modules/` não existe.

**Fluxo:**
1. Use a tabela de roteamento abaixo para encontrar o módulo (`notion-starter`, `notion-tasks-cli`, `notion-workspace-app`).
2. Edite no arquivo correto, em `modules/<nome>/`.
3. Teste dentro do módulo: `cd modules/<nome> && python -m pytest`.
4. Commit e push **dentro do módulo**, não no hub.

Nunca desenvolva funcionalidade neste hub; este é documentação e roteamento.

---

## Catálogo de módulos

| Repositório | Papel | Local após bootstrap |
| --- | --- | --- |
| [notion-starter](https://github.com/Felipe-Alcantara/notion-starter) | Biblioteca Python base + camada compartilhada: `NotionClient`, schema, tarefas, conteúdo, inventário, adaptadores e `notion_starter.services` | `modules/notion-starter/` |
| [notion-tasks-cli](https://github.com/Felipe-Alcantara/notion-tasks-cli) | CLI para IAs ("MCP via CLI"): borda fina; `integrations/` e `services/` comuns são shims para `notion-starter` | `modules/notion-tasks-cli/` |
| [notion-workspace-app](https://github.com/Felipe-Alcantara/notion-workspace-app) | App completo: API Django, SPA React, servidor MCP, launcher `start_app.py` | `modules/notion-workspace-app/` |

## Roteamento — MODO USO

Instale uma vez: `pip install git+https://github.com/Felipe-Alcantara/notion-tasks-cli.git`
Requer `NOTION_TOKEN` (e opcionalmente `NOTION_DATABASE_ID`) no ambiente ou `.env`.
`notion-tasks --help` traz o guia completo, escrito para ser lido por modelos.

| Você quer… | Comando |
| --- | --- |
| Listar/criar/editar/mover/concluir tarefas | `notion-tasks listar / criar / editar / mover / concluir` |
| Descobrir status, durações e áreas válidas | `notion-tasks opcoes` (sempre antes de criar/mover) |
| Mapear o workspace inteiro | `notion-tasks mapear` |
| Pesquisar páginas e databases | `notion-tasks buscar <termo>` |
| Listar databases / linhas de um database | `notion-tasks databases` / `notion-tasks linhas <id>` |
| Ler uma página como Markdown | `notion-tasks conteudo <id>` |
| Editar propriedades (colunas) de uma linha de database | `notion-tasks editar-linha <id> --set "Nome=valor"` (substitui) / `--append "Nome=texto"` (acrescenta preservando). **Faça isto antes de escrever o conteúdo.** |
| Escrever/editar/apagar blocos | `notion-tasks escrever / editar-bloco / apagar-bloco` (apagar exige `--sim`; o Notion arquiva, não destrói) |
| Clonar páginas/estruturas | `notion-tasks clonar <id>` |
| Importar/atualizar repositórios do GitHub numa database (vários perfis de uma vez, com dedup) | `notion-tasks atualizar-github --contas <login/@handle/URL,...>` (upsert por URL, propriedades ricas e README em subpágina). Flags: `--sem-readme` (só propriedades), `--sem-arquivados` (ignora arquivados), `--apenas-mudancas` (pula sem alteração). Guia: [`docs/GITHUB-DATABASE.md`](docs/GITHUB-DATABASE.md) |
| Interface gráfica ou servidor MCP | use o `notion-workspace-app` (`python start_app.py`) |

## Roteamento — MODO DESENVOLVIMENTO

Primeiro `python bootstrap.py` (clona ou atualiza os módulos em `modules/`). Depois localize o alvo:

| O pedido mexe em… | Repositório | Onde |
| --- | --- | --- |
| Cliente HTTP, retries, rate limit, erros da API | notion-starter | `src/notion_starter/client.py` |
| Schema de databases, comparação | notion-starter | `src/notion_starter/schema.py` |
| Modelo de tarefas (`Tarefa`, `TaskList`) | notion-starter | `src/notion_starter/tasks.py` |
| Conversão Markdown ↔ blocos; builders de propriedade (fatia de texto >2000) | notion-starter | `src/notion_starter/content.py`, `properties.py`, `readers.py` |
| Ler/editar propriedades de uma página (`obter_pagina`/`atualizar_pagina`) | notion-starter | `src/notion_starter/client.py` |
| Inventário/varredura do workspace | notion-starter | `src/notion_starter/inventory.py` |
| Saneamento de texto/JSON (surrogates), `fatiar_utf16` | notion-starter | `src/notion_starter/utils.py` |
| Subcomandos do CLI, saída JSON, `--help` | notion-tasks-cli | `cli/notion_tasks.py` |
| Regra de negócio compartilhada (tarefas, clonagem, conteúdo, ingestão, sync GitHub) | notion-starter | `src/notion_starter/services/` |
| Editar propriedades de linha genérica (`editar-linha`, set/append) | notion-tasks-cli | `services/propriedades.py` |
| Adaptadores GitHub/OpenRouter/Notion | notion-tasks-cli | `integrations/` |
| Endpoints REST, serializers | notion-workspace-app | `server/api/` |
| Servidor MCP (ferramentas `notion.*`) | notion-workspace-app | `server/mcp_server.py` |
| Interface web (kanban, filtros, exploração) | notion-workspace-app | `front/src/` |
| Launcher TUI | notion-workspace-app | `start_app.py` |

**Consolidação:** `integrations/github.py`, `integrations/openrouter.py` e os `services/`
compartilhados do CLI/app são shims para `notion-starter`. Corrija a implementação real em
`modules/notion-starter/src/notion_starter/`. O que ainda é específico do consumidor permanece
no consumidor (ex.: `services/propriedades.py` do CLI e `integrations/notion.py` de cada borda).

### Fluxo de trabalho

1. `python bootstrap.py` — garante `modules/` atualizado (`git pull` em cada módulo).
2. Edite no módulo correto. Cada módulo tem seu próprio `AGENTS.md` com detalhes locais.
3. Rode os testes **do módulo**: `python -m pytest` dentro dele.
4. Commite e push **dentro do módulo** (Conventional Commits: `feat:`/`fix:`/`docs:`/`refactor:`/`chore:`).
5. Se mudou arquitetura, contratos entre módulos ou o roteamento acima, atualize este hub (`AGENTS.md`, `README.md`) e registre a decisão no `IA.md`.

### Convenções (valem para todos os módulos)

- Código, docstrings e mensagens de erro **em português**.
- Fronteiras de camada sagradas: bordas (CLI/API/MCP) não têm regra de negócio; `services` não conhece HTTP; só o `NotionClient` fala com a API do Notion.
- Tipagem forte (`TypedDict` para payloads, `dataclass` para resultados); exceções derivam de `NotionSyncError`.
- Nunca commitar `.env`, tokens ou bancos SQLite.
- Histórico de decisões de arquitetura: `IA.md` (leia antes de mudanças estruturais).
- Falhas pré-existentes conhecidas no Windows: 2 em `test_start_app`, 1 em `test_services_ingestao` (não são regressão sua).
