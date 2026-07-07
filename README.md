# 🧩 Automações do Notion

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Notion API](https://img.shields.io/badge/Notion-API-000000?style=for-the-badge&logo=notion&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**Hub do ecossistema de automações do Notion — arquitetura, documentação e roteamento dos módulos que nasceram aqui.**

[🚀 Como Usar](#-uso--cli-para-operar-o-notion) • [🛠️ Desenvolvimento](#️-desenvolvimento--editar-os-módulos) • [🤖 Para IAs](#-para-ias--agentes-de-ia-como-desenvolvedoras) • [📐 Arquitetura](#-arquitetura-do-ecossistema)

</div>

---

## 📋 Índice

- [⚡ Primeiro passo obrigatório](#-primeiro-passo-obrigatório)
- [📁 Estrutura do Projeto](#-estrutura-do-projeto)
- [🚀 Uso — CLI para operar o Notion](#-uso--cli-para-operar-o-notion)
- [🛠️ Desenvolvimento — editar os módulos](#️-desenvolvimento--editar-os-módulos)
- [🤖 Para IAs — agentes como desenvolvedoras](#-para-ias--agentes-de-ia-como-desenvolvedoras)
- [📐 Arquitetura do ecossistema](#-arquitetura-do-ecossistema)
- [🌌 Ecossistema Felixo](#-ecossistema-felixo)
- [📚 Documentação](#-documentação)
- [📄 Licença](#-licença)
- [👤 Autor](#-autor)

---

## ⚡ Primeiro passo obrigatório

### Forma mais simples — o menu de entrada

Não quer decorar comando? Rode o menu interativo e escolha o que fazer (instalar a CLI, configurar o token, sincronizar os módulos, ver status ou operar o Notion):

```bash
python start_app.py
```

No menu você tem: **Instalar/Setup**, **Configurar**, **Usar o Notion (CLI)**, **Desenvolver** e **Status/Sair**. É a porta de entrada única do hub.

### Ou direto pelos scripts

Se você está começando aqui — seja para **usar** as ferramentas (CLI) ou **desenvolver** (editar o código) — rode isto primeiro:

```bash
python bootstrap.py
```

Isso prepara os 3 módulos do ecossistema em `modules/` (gitignorado, só local seu). Sem este passo, os módulos não existem.

> **Reusa clones que você já tem.** Se um módulo já estiver clonado **na pasta acima** deste repositório (ex.: `../notion-tasks-cli`), o `bootstrap.py` cria um **link** para reusar o mesmo working copy em vez de duplicar — assim você desenvolve num só lugar. Só clona do GitHub o que ainda não existe. O link usa junction no Windows (não precisa de administrador) e symlink no Linux/macOS.

### Depois: sincronizar regularmente

Quando os módulos tiverem atualizações no GitHub, rode:

```bash
python sync.py
```

Ou, se configurou o alias (veja [SYNC.md](SYNC.md)):

```bash
sync
```

Isso executa `git pull` em cada módulo e valida que tudo está OK.

---

## 📁 Estrutura do Projeto

Este repositório é **só o hub**: documentação, roteamento e as ferramentas de bootstrap. O código das ferramentas vive nos módulos, clonados sob demanda em `modules/` (gitignorado).

```
Automações do Notion/
│
├── 📁 docs/                # Arquitetura, contratos, MCP, modularização, escala
├── 📁 modules/             # Módulos clonados por bootstrap.py (local, gitignorado)
│
├── AGENTS.md               # Roteamento de pedidos para o módulo/arquivo certo
├── CLAUDE.md               # Contexto automático para Claude Code
├── IA.md                   # Linha do tempo de decisões de arquitetura
├── README.md               # Este arquivo
├── SYNC.md                 # Como configurar o alias `sync`
│
├── start_app.py            # Menu de entrada interativo (instalar, configurar, usar, dev)
├── bootstrap.py            # Clona os 3 módulos em modules/
├── sync.py                 # git pull em cada módulo
├── check-dev.py            # Verifica se o workspace de dev está pronto
└── LICENSE
```

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

# Linha de database (propriedades ANTES do conteúdo)
notion-tasks editar-linha <id> --set "Status=Feito"      # substitui uma coluna
notion-tasks editar-linha <id> --append "Resumo=..."     # acrescenta sem perder o atual

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
| Conversão Markdown ↔ blocos; builders de propriedade (fatia >2000) | notion-starter | `src/notion_starter/content.py`, `properties.py` |
| Ler/editar propriedades de página (`obter_pagina`/`atualizar_pagina`) | notion-starter | `src/notion_starter/client.py` |
| Saneamento de texto/JSON (surrogates), `fatiar_utf16` | notion-starter | `src/notion_starter/utils.py` |
| Subcomando do CLI, saída JSON, `--help` | [notion-tasks-cli](https://github.com/Felipe-Alcantara/notion-tasks-cli) | `cli/notion_tasks.py` |
| Regra de negócio compartilhada (tarefas, clonagem, conteúdo, GitHub) | notion-starter | `src/notion_starter/services/` |
| Editar propriedades de linha genérica (`editar-linha`) | notion-tasks-cli | `services/propriedades.py` |
| Endpoints REST, serializers, API Django | [notion-workspace-app](https://github.com/Felipe-Alcantara/notion-workspace-app) | `server/api/` |
| Servidor MCP (ferramentas `notion.*`) | notion-workspace-app | `server/mcp_server.py` |
| Interface web (kanban, filtros, exploração) | notion-workspace-app | `front/src/` |
| Launcher TUI (`start_app.py`) | notion-workspace-app | `start_app.py` |

**Consolidação:** os adaptadores GitHub/OpenRouter e os `services` compartilhados vivem em
`notion-starter`; os módulos consumidores mantêm shims compatíveis. Código específico de borda
continua nos consumidores.

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
- **[docs/GITHUB-DATABASE.md](docs/GITHUB-DATABASE.md)** — importar e manter seus repositórios do GitHub numa database do Notion.
- **[docs/QUALIDADE.md](docs/QUALIDADE.md)** — contrato de qualidade do hub e dos módulos.
- **[docs/](docs/)** — material de arquitetura, contratos, MCP, modularização, escala.

---

## 📄 Licença

Este projeto está sob a licença MIT — veja o arquivo [`LICENSE`](LICENSE).

---

## 👤 Autor

**Felipe Martin**

- GitHub: [@Felipe-Alcantara](https://github.com/Felipe-Alcantara)
- Módulos: [notion-starter](https://github.com/Felipe-Alcantara/notion-starter) · [notion-tasks-cli](https://github.com/Felipe-Alcantara/notion-tasks-cli) · [notion-workspace-app](https://github.com/Felipe-Alcantara/notion-workspace-app)

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para:

- Reportar bugs e propor melhorias
- Sugerir novas automações ou comandos
- Melhorar a documentação e o roteamento para agentes

Lembre-se: funcionalidade se desenvolve **nos módulos**, não neste hub (ver [AGENTS.md](AGENTS.md)).

---

⭐ Se este ecossistema foi útil, considere deixar uma estrela no GitHub!
