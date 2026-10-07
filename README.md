# 🧩 Felixo Notion MCP

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Notion API](https://img.shields.io/badge/Notion-API-000000?style=for-the-badge&logo=notion&logoColor=white)
![MCP](https://img.shields.io/badge/MCP-Server-6C47FF?style=for-the-badge)
[![PyPI](https://img.shields.io/pypi/v/notion-automacoes?style=for-the-badge&label=PyPI)](https://pypi.org/project/notion-automacoes/)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**Notion para pessoas e para IAs: biblioteca, CLI, servidor MCP e app local num único pacote Python.**

[🚀 Como Usar](#-como-usar) • [🧰 Comandos](#-comandos-principais) • [🏛️ Arquitetura](docs/ARQUITETURA.md) • [🤖 Para IAs](#-para-ias) • [🤝 Contribuições](#-contribuições)

</div>

---

## 📋 Índice

- [⭐ **O menu de entrada**](#-o-menu-de-entrada) ⭐ **DESTAQUE**
- [📋 Sobre o Projeto](#-sobre-o-projeto)
- [📁 Estrutura do Projeto](#-estrutura-do-projeto)
- [🧰 Ferramentas Disponíveis](#-ferramentas-disponíveis)
- [🚀 Como Usar](#-como-usar)
- [📚 Guia Rápido](#-guia-rápido)
- [🔧 Funcionalidades Técnicas](#-funcionalidades-técnicas)
- [⚠️ Limitações](#️-limitações)
- [🛡️ Segurança](#️-segurança)
- [📖 Documentação](#-documentação)
- [🌌 Ecossistema Felixo](#-ecossistema-felixo)
- [📝 Licença](#-licença)
- [👤 Autor](#-autor)
- [🤝 Contribuições](#-contribuições)

---

## ⭐ O menu de entrada

> **🚀 UM COMANDO, SEM DECORAR NADA**
>
> ```bash
> python start_app.py
> ```

### 💡 Por que começar por ele?

- **🎯 Tudo num lugar**: instalar, configurar o token, subir o app web, subir o servidor MCP e ver o estado do ambiente.
- **🧭 Descritivo**: cada opção do menu explica o que vai fazer antes de fazer.
- **🪶 Abre sem nada instalado**: o `start_app.py` usa só a biblioteca padrão do Python, então funciona num clone recém-baixado, em Windows, macOS e Linux.
- **🩺 Status honesto**: a opção Status mostra o estado real do ambiente e também de onde o pacote é importado (a mesma informação do `felixo-notion-mcp doctor`).

Menu: **Usar o app** (app web local) • **Para IA e integrações** (CLI, GitHub, servidor MCP, mapa) • **Configurar e instalar** (token e database de tarefas, dependências, API, qualidade) • **Status** • **Sair**. O **Configurar** define só o token do Notion e o database de tarefas, guardados no `.env`; os perfis de workspace se gerenciam à parte, com `felixo-notion-mcp auth` (ou `notion-tasks perfis`).

Tecnologias da interface: terminal colorido com `rich` e `questionary`.

---

## 📋 Sobre o Projeto

O **Felixo Notion MCP** é um **monólito modular** em Python, centrado num **servidor MCP**: ele deixa uma IA (Claude Code, Cursor, scripts) ler, criar e editar páginas, databases e tarefas do **Notion** com segurança. A mesma base de código também entrega a **CLI `notion-tasks`**, pensada para IAs e pessoas (o "MCP via CLI"), um **app web local** (API Django e SPA React com kanban, filtros e exploração) e uma **biblioteca** importável, com cliente resiliente para a API do Notion, schema, tarefas, conteúdo em Markdown e inventário.

Ele nasceu como quatro repositórios: a biblioteca `notion-starter`, a CLI `notion-tasks-cli`, o app `notion-workspace-app` e um hub de documentação. Manter três pacotes com versões casadas custava caro, então o plano é reuni-los num produto só, em quatro etapas. **Esta é a etapa 1: a reestruturação.** O código mudou de lugar, não de comportamento.

### ✨ **NOVO: um repositório, um pacote**

- ✅ Os três módulos e o hub viraram **um pacote**, `felixo-notion-mcp` (import `felixo_notion_mcp`), com o histórico git preservado.
- ✅ O código está em **camadas** (`domain`, `services`, `repositories`, `integrations`, `api`, `core`), descritas em [`docs/ARQUITETURA.md`](docs/ARQUITETURA.md).
- ✅ **Dependências travadas** em `uv.lock` e **CI em matriz** (Ubuntu, Windows e macOS × Python 3.10 a 3.13), com `pip-audit` e `npm audit`.
- ✅ `felixo-notion-mcp doctor` mostra **de onde o pacote está sendo importado**, no lugar do antigo `check-dev.py`.
- ✅ **Nada muda para quem usa**: as mesmas linhas de comando, o mesmo apelido `notion-tasks` e o mesmo arquivo de perfis.

---

## 📁 Estrutura do Projeto

```text
Felixo-Notion-MCP/
│
├── 📁 src/felixo_notion_mcp/    # o pacote
│   ├── 📁 domain/               # regras puras: propriedades, schema, Markdown ↔ blocos, tarefas
│   ├── 📁 services/             # casos de uso (tarefas, conteúdo, relações, relatórios, GitHub…)
│   ├── 📁 repositories/         # persistência local (Django ORM): estado operacional
│   ├── 📁 integrations/         # cliente HTTP do Notion, GitHub e OpenRouter
│   ├── 📁 api/                  # bordas: cli/, mcp/, http/ (Django) e o menu launcher.py
│   └── 📁 core/                 # configuração, perfis, exceções, logging, utilitários
│
├── 📁 front/                    # fonte da SPA React (o build entra no wheel)
├── 📁 tests/                    # espelha as camadas, mais o contrato da CLI
├── 📁 scripts/                  # empacotamento nativo, migração e scripts reutilizáveis
├── 📁 examples/                 # exemplos de uso da biblioteca
├── 📁 docs/                     # arquitetura, distribuição, contratos, MCP, qualidade…
│
├── start_app.py                 # menu interativo de entrada
├── pyproject.toml · uv.lock     # metadados do pacote e dependências travadas
├── AGENTS.md · CLAUDE.md        # roteamento e contexto para agentes de IA
├── IA.md                        # linha do tempo de decisões
├── CONTRIBUTING.md              # como contribuir
├── .env.example                 # modelo de variáveis de ambiente (sem valores)
├── README.md                    # este arquivo
└── LICENSE
```

---

## 🧰 Ferramentas Disponíveis

### 💻 CLI para IAs e pessoas (`src/felixo_notion_mcp/api/cli/`)

**`notion-tasks`** (apelido permanente) e **`felixo-notion-mcp`**
- Cria, edita, move e conclui tarefas; lê e escreve o conteúdo das páginas em Markdown; mapeia o workspace; clona estruturas; importa planilhas; exporta relatórios para DOCX; sincroniza repositórios do GitHub.
- O `--help` é um guia escrito para IAs, e os erros em `--json` vêm num envelope único (`codigo`, `mensagem`, `proximo_passo`).
- Exemplo: `notion-tasks conteudo <id>` → propriedades e corpo da página, avisando quando ela contém um database.

📖 [Ver o roteamento e as regras de operação](AGENTS.md)

---

### 🔌 Servidor MCP (`src/felixo_notion_mcp/api/mcp/`)

**`server.py`**
- Expõe as capacidades de Notion como ferramentas MCP (transporte stdio, e Streamable HTTP para depuração local).
- Operações destrutivas sinalizam `destructiveHint` para o cliente pedir confirmação.
- Exemplo: `felixo-notion-mcp mcp start` → servidor pronto para o Claude Code ou o Cursor.

📖 [Ver ferramentas, transportes e integração](docs/MCP.md)

---

### 🌐 App web local (`src/felixo_notion_mcp/api/http/` e `front/`)

**API Django + SPA React**
- Kanban, lista e grade de tarefas, filtros e exploração de qualquer database.
- A SPA já vem compilada no wheel; Node e npm só são necessários no checkout de desenvolvimento.
- Exemplo: `felixo-notion-mcp app start` → API e SPA em `127.0.0.1`.

📖 [Ver os contratos REST](docs/CONTRATOS.md) • [infraestrutura](docs/INFRA.md)

---

### 📚 Biblioteca (`domain/`, `services/`, `integrations/`)

**`NotionClient`, `TaskList`, conversão Markdown ↔ blocos**
- Cliente com retries, rate limit e paginação; builders e leitores de propriedade; comparação de schema.
- Exemplo: `markdown_para_blocos("# Título")` → blocos prontos para a API.

📖 [Ver o mapa das camadas](docs/ARQUITETURA.md) • [exemplos](examples/)

---

## 🚀 Como Usar

### Opção 1: instalar o pacote publicado (mais simples) 📦

Para só **usar** o Notion, sem clone, Git ou Node:

```bash
pipx install "notion-automacoes[app]"
# ou: uv tool install "notion-automacoes[app]"
notion-automacoes --version
notion-automacoes doctor
```

> **Em transição.** Os pacotes publicados no PyPI hoje são `notion-automacoes` (CLI), `notion-starter` e `notion-workspace-app`. O pacote `felixo-notion-mcp` é construído a partir deste repositório e será publicado na etapa 4. Os comandos `notion-tasks` são os mesmos nos dois. Os detalhes estão em [`docs/DISTRIBUICAO.md`](docs/DISTRIBUICAO.md).

### Opção 2: pelo checkout (para mexer no código) 🛠️

#### Instalação

```bash
# Clone o repositório
git clone https://github.com/Felipe-Alcantara/Felixo-Notion-MCP.git
cd Felixo-Notion-MCP

# O caminho mais curto: o menu instala e configura por você
python start_app.py

# Ou manualmente, com as dependências travadas
uv sync --locked --all-extras
```

#### Executando

```bash
uv run felixo-notion-mcp doctor      # diagnóstico: Python, dependências, perfis, rede, origem do pacote
uv run notion-tasks --help           # o guia completo da CLI
uv run python -m pytest              # a suíte (HTTP mockado: não precisa de token nem de rede)
uv run ruff check .                  # lint
```

### Configurar o token

```bash
export NOTION_TOKEN=ntn_...          # ou copie .env.example para .env
export NOTION_DATABASE_ID=...        # opcional: o database de tarefas padrão
```

Ou salve workspaces como **perfis** (recomendado para quem alterna entre workspaces):

```bash
notion-tasks perfis adicionar <alias>   # salva uma key/workspace local
notion-tasks perfis usar <alias>        # define o perfil ativo
notion-tasks perfis listar              # mostra os perfis sem expor tokens
notion-tasks --perfil <alias> <comando> # usa outro perfil só nesta execução
```

> **Atenção à precedência** (da maior para a menor): `--perfil <alias>` → **perfil ativo** → `NOTION_TOKEN` do ambiente ou do `.env`. Com um perfil ativo, o token dele **vence silenciosamente** a variável de ambiente. Se um link válido devolve "Recurso não encontrado", confira primeiro o perfil ativo com `notion-tasks perfis listar` — você pode estar consultando outro workspace.

Os perfis ficam na **pasta de configuração do usuário** (`~/.config/notion-tasks/` ou `%APPDATA%\notion-tasks\`), não ao lado do pacote, então trocar o modo de instalação não os afeta.

### 🧰 Comandos principais

```bash
# 1. SEMPRE comece lendo o que o link é
notion-tasks conteudo <id>       # propriedades + corpo. Se vier "databases_dentro",
                                 # o conteúdo são as LINHAS da tabela, não esta página
notion-tasks schema <id>         # colunas, tipos, valores aceitos e relações do database

# Tarefas
notion-tasks listar
notion-tasks criar "Tarefa" --status "Entrada" \
  --set "Prioridade=Alta" --conteudo "## Contexto..."   # linha completa numa chamada
notion-tasks mover <id> --status "Concluído"

# Workspace
notion-tasks mapear              # resume o workspace inteiro
notion-tasks buscar <termo>      # pesquisa páginas e databases
notion-tasks linhas <id>         # lista linhas de um database

# Linha de database (propriedades ANTES do conteúdo)
notion-tasks editar-linha <id> --set "Status=Feito"      # substitui uma coluna
notion-tasks editar-linha <id> --append "Resumo=..."     # acrescenta sem perder o atual
notion-tasks relacionar <a> <b> --coluna "Relacionadas"  # liga nos dois sentidos

# Conteúdo de páginas
notion-tasks escrever <id>                 # anexa Markdown (recusa página que contém database)
notion-tasks escrever <id> --apos <bloco>  # insere no meio da página
notion-tasks blocos <id> --metadados       # blocos com ID, criado/editado em
notion-tasks editar-bloco <id> --trocar "de" --por "para"  # troca um trecho sem perder formatação
notion-tasks restaurar-bloco <id>          # desfaz uma exclusão

# Relatórios diários (saída programática: acabamento fino pode pedir ajuste manual no Word)
notion-tasks exportar-docx --database <id> --de 2026-07-01 --ate 2026-07-06 --saida ./exports

# Servidor MCP e app local
felixo-notion-mcp mcp start      # servidor MCP (stdio)
felixo-notion-mcp app start      # API e SPA locais

# Guia completo
notion-tasks --help
```

---

## 📚 Guia Rápido

### Para Iniciantes
1. Rode `python start_app.py`.
2. Escolha **Instalar/Setup** e depois **Configurar** para salvar o token do Notion.
3. Escolha **Iniciar** para abrir o app web, ou **Status** para conferir o ambiente.

### 🤖 Para IAs
1. Leia [`AGENTS.md`](AGENTS.md): ele roteia cada pedido (usar o Notion ou desenvolver as ferramentas) e traz as regras de operação.
2. Ao receber um link do Notion, rode `notion-tasks conteudo <id>` **antes de escrever qualquer coisa**.
3. [`CLAUDE.md`](CLAUDE.md) é o contexto carregado automaticamente pelo Claude Code.

### Para Desenvolvedores
1. `uv sync --locked --all-extras` e `uv run python -m pytest`.
2. Ache o arquivo certo na tabela de [`AGENTS.md`](AGENTS.md) ou no mapa de [`docs/ARQUITETURA.md`](docs/ARQUITETURA.md).
3. Leia o [`CONTRIBUTING.md`](CONTRIBUTING.md) antes de abrir o PR.

---

## 🔧 Funcionalidades Técnicas

- **Camadas com direção única**: `api` → `services` → `integrations` → `domain` → `core`. A borda não tem regra de negócio, `domain` e `services` não conhecem HTTP, e só `integrations/notion_client.py` fala com a API do Notion.
- **Contrato da CLI preso por teste**: o retrato do parser (`tests/contrato/retrato_cli.json`) garante que o que a CLI aceitava continua aceito.
- **Envelope de erro único** na CLI: `{"ok": false, "erro": {"codigo", "mensagem", "proximo_passo", ...}}`.
- **Importação sob demanda**: `import felixo_notion_mcp` não carrega `requests`; por isso o menu abre num Python sem dependências.
- **Dependências travadas** em `uv.lock`, com auditoria (`pip-audit`, `npm audit`) e conferência do conteúdo do wheel na CI.

---

## ⚠️ Limitações

- **Distribuição em transição**: o pacote `felixo-notion-mcp` ainda não está no PyPI; os pacotes publicados continuam `notion-automacoes`, `notion-starter` e `notion-workspace-app`.
- **Binário nativo**: o build com PyInstaller foi construído e testado só em **Linux x64**. Windows e macOS rodam a suíte na CI, mas o build e o smoke do binário nesses sistemas ainda não foram exercitados.
- **MCP local**: o servidor roda na sua máquina (stdio). O modo hospedado, com contas e OAuth, ainda não existe.
- **DOCX**: a exportação de relatórios reproduz o modelo visual de forma programática; o acabamento fino pode exigir ajuste manual no Word.

---

## 🛡️ Segurança

⚠️ **IMPORTANTE:** o token do Notion dá acesso ao seu workspace. Trate-o como uma senha.

- O token **nunca é impresso** pela CLI, e os perfis ficam na pasta de configuração do seu usuário, fora do repositório.
- O `.env` é ignorado pelo git; o repositório só traz o `.env.example`, sem valores.
- Operações destrutivas pedem confirmação explícita (`--sim`), e os backups de bloco ficam na pasta de estado do usuário, nunca no diretório atual.
- Compartilhe com a integração do Notion só as páginas e os databases que ela precisa enxergar.

---

## 📖 Documentação

- 🏛️ [`docs/ARQUITETURA.md`](docs/ARQUITETURA.md): as camadas, a direção das dependências e de onde veio cada arquivo.
- 📦 [`docs/DISTRIBUICAO.md`](docs/DISTRIBUICAO.md): pacotes, binários nativos e a transição para o pacote único.
- ✅ [`docs/QUALIDADE.md`](docs/QUALIDADE.md): o gate e o critério de pronto.
- 🔗 [`docs/MCP.md`](docs/MCP.md): ferramentas MCP e integração com clientes.
- 🧱 [`docs/CONTRATOS.md`](docs/CONTRATOS.md): objetos, rotas REST e erros.
- 🐙 [`docs/GITHUB-DATABASE.md`](docs/GITHUB-DATABASE.md): manter seus repositórios do GitHub numa database do Notion.
- 🗂️ [`docs/`](docs/README.md): o índice completo.
- 🤖 [`AGENTS.md`](AGENTS.md) • [`CLAUDE.md`](CLAUDE.md) • [`IA.md`](IA.md): roteamento, contexto e histórico de decisões.

---

## 🌌 Ecossistema Felixo

Este projeto faz parte de um ecossistema maior de desenvolvimento com multiagentes, em ordem cronológica:

1. [Felixo-System-Design](https://github.com/Felipe-Alcantara/Felixo-System-Design) — padrão de qualidade e boas práticas de vibe coding
2. [Felixo-AI-Core](https://github.com/Felipe-Alcantara/Felixo-AI-Core) — orquestrador Electron para spawnar, monitorar e desenvolver com multiagentes
3. [Openia](https://github.com/Felipe-Alcantara/Openia) — qualquer modelo de IA na interface do Claude Code
4. **Felixo Notion MCP** — este projeto (antes, "Automações do Notion")
5. [OpenRouter-Monitorator](https://github.com/Felipe-Alcantara/OpenRouter-Monitorator) — métricas de uso e custo de modelos via OpenRouter

---

## 📝 Licença

Este projeto está sob a licença MIT — veja o arquivo [`LICENSE`](LICENSE).

---

## 👤 Autor

**Felipe Alcantara**

- GitHub: [@Felipe-Alcantara](https://github.com/Felipe-Alcantara)
- Repositório: [Felixo-Notion-MCP](https://github.com/Felipe-Alcantara/Felixo-Notion-MCP)

---

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para:

- Reportar bugs e propor melhorias
- Sugerir novas automações ou comandos
- Melhorar a documentação e o roteamento para agentes

Veja o [`CONTRIBUTING.md`](CONTRIBUTING.md) para o ambiente, os padrões e o fluxo de PR.

### 💡 Ideias para quem quiser contribuir

O projeto ainda pode crescer em várias direções, e qualquer uma delas é um bom ponto de partida:

- **Um registro único de operações**, do qual o servidor MCP, a CLI e a API REST sejam geradas, com paridade entre elas.
- **Um modo hospedado** do servidor MCP, com contas, OAuth do Notion e chaves pessoais, para usar de qualquer cliente.
- **Um teste de arquitetura** que falhe quando uma camada importar o que não deve.
- **Build e smoke do binário nativo** em Windows e macOS, e a assinatura dos executáveis.
- **Upload de arquivo** no modo hospedado, contas de equipe e um redesenho da SPA.

---

⭐ Se este projeto foi útil, considere deixar uma estrela no GitHub!
