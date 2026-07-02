# Automações do Notion

Hub do ecossistema de automações do Notion — arquitetura, documentação e os módulos que nasceram aqui.

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org)
[![Notion API](https://img.shields.io/badge/Notion-API-000000?style=flat-square&logo=notion&logoColor=white)](https://developers.notion.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

---

## ⚡ Primeiro passo obrigatório

Se você está começando aqui — seja para **usar** as ferramentas (CLI) ou **desenvolver** (editar o código) — rode isto primeiro:

```bash
python bootstrap.py
```

Isso clona os 3 módulos do ecossistema em `modules/` (gitignorado, só local seu). Sem este passo, os módulos não existem.

---

## 🚀 Uso — CLI para operar o Notion

### Instalação (uma vez)

```bash
pip install git+https://github.com/Felipe-Alcantara/notion-tasks-cli.git
```

Configure o token:

```bash
export NOTION_TOKEN=ntn_...
export NOTION_DATABASE_ID=...
```

### Comandos principais

```bash
# Tarefas
notion-tasks listar
notion-tasks criar --titulo "Tarefa" --status "Em andamento"
notion-tasks mover <id> --status "Concluído"

# Workspace
notion-tasks mapear              # resume o workspace inteiro
notion-tasks buscar <termo>      # pesquisa páginas e databases
notion-tasks linhas <id>         # lista linhas de um database

# Conteúdo de páginas
notion-tasks conteudo <id>       # lê como Markdown
notion-tasks escrever <id>       # anexa Markdown
notion-tasks editar-bloco <id>   # substitui texto

# Guia completo
notion-tasks --help
```

O `--help` é um guia escrito para IAs — qualquer modelo consegue ler, entender e operar este CLI.

---

## 🛠️ Desenvolvimento — editar os módulos

Estrutura após `python bootstrap.py`:

```
modules/
├── notion-starter/          # Biblioteca Python base
├── notion-tasks-cli/        # CLI para IAs (+ camada de serviços)
└── notion-workspace-app/    # App Django + React + MCP
```

### Fluxo de trabalho

1. Rode `python bootstrap.py` (já fez? pule para 2).
2. Edite no módulo correto (ver tabela de roteamento abaixo).
3. Teste dentro do módulo: `cd modules/<nome> && python -m pytest`.
4. Commit e push **dentro do módulo**, nunca no hub.

### Roteamento: "o que preciso mexer vive em qual módulo?"

| O pedido é… | Repositório | Arquivo de interesse |
| --- | --- | --- |
| Parar de chamar a API do Notion; melhorar resilência; cliente HTTP | [notion-starter](https://github.com/Felipe-Alcantara/notion-starter) | `src/notion_starter/client.py` |
| Schema, leitura/comparação de database | notion-starter | `src/notion_starter/schema.py` |
| Modelo `Tarefa` e `TaskList` | notion-starter | `src/notion_starter/tasks.py` |
| Conversão Markdown ↔ blocos | notion-starter | `src/notion_starter/content.py` |
| Saneamento de texto/JSON (surrogates) | notion-starter | `src/notion_starter/utils.py` |
| Subcomando do CLI, saída JSON, `--help` | [notion-tasks-cli](https://github.com/Felipe-Alcantara/notion-tasks-cli) | `cli/notion_tasks.py` |
| Regra de negócio (tarefas, clonagem, conteúdo, GitHub) | notion-tasks-cli | `services/` |
| Endpoints REST, serializers, API Django | [notion-workspace-app](https://github.com/Felipe-Alcantara/notion-workspace-app) | `server/api/` |
| Servidor MCP (ferramentas `notion.*`) | notion-workspace-app | `server/mcp_server.py` |
| Interface web (kanban, filtros, exploração) | notion-workspace-app | `front/src/` |
| Launcher TUI (`start_app.py`) | notion-workspace-app | `start_app.py` |

**Dívida conhecida:** `core/`, `integrations/` e `services/` vivem duplicados em `notion-tasks-cli` e `notion-workspace-app/server/`. Quando mexer nesses pacotes, aplique a correção nos dois repos. (Roadmap: consolidar no notion-starter.)

### Exemplo: adicionar um comando ao CLI

```bash
cd modules/notion-tasks-cli
# edite cli/notion_tasks.py
python -m pytest -q
git add cli/notion_tasks.py
git commit -m "feat: novo comando"
git push
```

Você commitou no repo correto (`notion-tasks-cli`), não no hub.

---

## 🤖 Para IAs — agentes de IA como desenvolvedoras

Este hub foi desenhado para agentes operarem:

- **[AGENTS.md](AGENTS.md)** — roteamento completo de pedidos para módulos + fluxo de trabalho.
- **[CLAUDE.md](CLAUDE.md)** — contexto automático carregado pelo Claude Code.
- **[bootstrap.py](bootstrap.py)** — clona os módulos; scripts iniciais podem rodar isto automaticamente.

Se você é um agente:

1. Leia `AGENTS.md` ao receber um pedido (roteia para o módulo certo).
2. Rode `python bootstrap.py` se `modules/` não existir.
3. Edite, teste e commite no módulo, não aqui.
4. Este hub é documentação; não desenvolva funcionalidade aqui.

---

## 📐 Arquitetura do ecossistema

```
┌─────────────────────────────────────────────────┐
│                 notion-starter                  │
│   biblioteca base (cliente, schema, tarefas)    │
└────────────┬───────────────────────┬────────────┘
             │                       │
   ┌─────────▼─────────┐   ┌─────────▼──────────┐
   │  notion-tasks-cli │   │ notion-workspace-  │
   │  "MCP via CLI"    │   │ app (Django+React  │
   │  para IAs         │   │  + MCP + TUI)      │
   └───────────────────┘   └────────────────────┘
```

### Módulos

| Repositório | O que é | Depende de |
| --- | --- | --- |
| [notion-starter](https://github.com/Felipe-Alcantara/notion-starter) | Biblioteca Python para a API oficial do Notion: cliente resiliente, schema, tarefas, conteúdo, inventário, exemplos | — |
| [notion-tasks-cli](https://github.com/Felipe-Alcantara/notion-tasks-cli) | CLI pensado para IAs — um "MCP via CLI" que permite a qualquer modelo criar, editar e manipular qualquer workspace do Notion pelo terminal | notion-starter |
| [notion-workspace-app](https://github.com/Felipe-Alcantara/notion-workspace-app) | Aplicação local completa: API Django, SPA React (kanban, filtros, exploração), servidor MCP, sincronização GitHub↔Notion e launcher TUI | notion-starter |

### Convenções (valem para todos os módulos)

- Código, docstrings e mensagens em **português**.
- Fronteiras de camada sagradas: bordas (CLI/API/MCP) sem regra de negócio; `services` não conhece HTTP; só `NotionClient` fala com a API do Notion.
- Tipagem forte (`TypedDict` para payloads, `dataclass` para resultados); exceções derivam de `NotionSyncError`.
- Histórico de decisões: `IA.md` (leia antes de mudanças estruturais).
- Conventional Commits: `feat`/`fix`/`docs`/`refactor`/`chore`.
- Nunca commitar `.env`, tokens, bancos SQLite ou `node_modules`.

---

## 🌌 Ecossistema Felixo

Este projeto faz parte de um ecossistema maior de desenvolvimento com multiagentes, em ordem cronológica:

1. [Felixo-System-Design](https://github.com/Felipe-Alcantara/Felixo-System-Design) — padrão de qualidade e boas práticas de vibe coding
2. [Felixo-AI-Core](https://github.com/Felipe-Alcantara/Felixo-AI-Core) — orquestrador Electron para spawnar, monitorar e desenvolver com multiagentes
3. [Openia](https://github.com/Felipe-Alcantara/Openia) — qualquer modelo de IA na interface do Claude Code
4. **Automações do Notion** — este hub e seus três módulos
5. [OpenRouter-Monitorator](https://github.com/Felipe-Alcantara/OpenRouter-Monitorator) — métricas de uso e custo de modelos via OpenRouter

---

## 📚 Documentação

- **[AGENTS.md](AGENTS.md)** — roteamento uso vs desenvolvimento, fluxo de trabalho, convenções.
- **[CLAUDE.md](CLAUDE.md)** — contexto automático para Claude Code.
- **[IA.md](IA.md)** — histórico de decisões de arquitetura.
- **[docs/](docs/)** — material de arquitetura, contratos, MCP, modularização, escala.

---

## 📄 Licença

MIT
