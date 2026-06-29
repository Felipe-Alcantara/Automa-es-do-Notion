# 🧠 Automações do Notion

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5-0C4B33?style=for-the-badge&logo=django&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=white)
![Notion API](https://img.shields.io/badge/Notion-API-000000?style=for-the-badge&logo=notion&logoColor=white)
![Quality](https://img.shields.io/badge/quality-ruff%20%2B%20pytest%20%2B%20front-success?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**Aplicação local para operar o Notion com API Django, SPA React, CLI/MCP para IA e inventário GitHub.**

[🚀 Ferramentas](#-ferramentas-disponíveis) • [🎯 Como Usar](#-como-usar) • [⌘ CLI para IA](#-cli-para-ia) • [✅ Qualidade](#-qualidade) • [📚 Docs](docs/README.md)

</div>

---

## 📋 Índice

- [🌟 Destaque Principal](#-destaque-principal)
- [📋 Sobre o Projeto](#-sobre-o-projeto)
- [📁 Estrutura do Projeto](#-estrutura-do-projeto)
- [🚀 Ferramentas Disponíveis](#-ferramentas-disponíveis)
- [🎯 Como Usar](#-como-usar)
- [⌘ CLI para IA](#-cli-para-ia)
- [🔌 API, MCP e Integrações](#-api-mcp-e-integrações)
- [🔒 Segurança e Dados](#-segurança-e-dados)
- [✅ Qualidade](#-qualidade)
- [📚 Documentação](#-documentação)
- [📝 Licença](#-licença)
- [👤 Autor](#-autor)
- [🤝 Contribuições](#-contribuições)

---

## 🌟 Destaque Principal

> **RODE TUDO POR UM MENU, SEM DECORAR COMANDOS**
>
> ```bash
> python3 start_app.py
> ```

O projeto centraliza automações reais em cima do Notion: escolhe o database de tarefas,
sobe a API Django, abre a SPA React, expõe uma CLI estável para IA, publica ferramentas
MCP e sincroniza inventários de repositórios GitHub.

### 💡 Por que usar?

- **Entrada única:** `start_app.py` instala, configura, sobe e diagnostica o ambiente.
- **Notion como fonte de verdade:** tarefas, páginas, databases e conteúdo continuam no workspace.
- **IA com contrato estável:** CLI JSON e MCP evitam que agentes mexam direto no JSON cru do Notion.
- **Qualidade verificável:** um gate único roda lint, testes Python e build do front.

---

## 📋 Sobre o Projeto

`Automações do Notion` é uma aplicação local para controlar e explorar um workspace do
Notion com menos atrito. Ela combina um core Python tipado (`notion_starter`), serviços
Django, SPA React, CLI para automações/IA e servidor MCP. O objetivo é permitir que uma
pessoa ou um agente leia, edite, clone, organize e inventarie conteúdo do Notion por
interfaces seguras e testáveis.

O projeto nasceu como um starter para integrações com a API do Notion e evoluiu para uma
central operacional: tarefas, conteúdo de páginas, exploração de databases genéricos,
inventário GitHub com README rico e ponte MCP para o Felixo-AI-Core.

---

## 📁 Estrutura do Projeto

```text
Automa-es-do-Notion/
│
├── 📁 src/notion_starter/        # Core Python: cliente Notion, propriedades, readers, conteúdo
├── 📁 server/                    # API Django, services, integrations e servidor MCP
├── 📁 front/                     # SPA React + Tailwind + Vite
├── 📁 cli/                       # CLI para scripts e agentes de IA
├── 📁 examples/                  # Exemplos executáveis de leitura, sync e mapeamento
├── 📁 tests/                     # Testes Python/Django/MCP/CLI com HTTP mockado
├── 📁 docs/                      # Roadmap, contratos, qualidade, integrações e arquitetura
├── 📁 scripts/                   # Automação local de qualidade
│
├── AGENTS.md                     # Roteiro operacional para agentes e mantenedores
├── IA.md                         # Memória técnica e linha do tempo do projeto
├── start_app.py                  # Menu principal de instalação, configuração e execução
├── pyproject.toml                # Metadados, extras e tooling Python
├── .env.example                  # Variáveis de ambiente sem segredos
├── CONTRIBUTING.md               # Guia de contribuição
├── README.md                     # Este arquivo
└── LICENSE
```

---

## 🚀 Ferramentas Disponíveis

### ▶️ Menu de Entrada (`start_app.py`)

**`python3 start_app.py`**

- Abre um menu interativo com categorias para uso normal, IA/integrações e configuração.
- Instala dependências, cria `.env`, configura token/database, mostra status e roda exemplos.
- Sobe API Django e front React juntos em modo local.
- Executa o gate de qualidade pelo próprio menu.

---

### 🌐 SPA React (`front/`)

**`front/src/App.jsx`**

- Interface web para tarefas do Notion com visualizações de grade, lista e kanban.
- Aba **Explorar** para visualizar qualquer database compartilhado com a integração.
- Filtros persistentes por etapa, esforço e área, usando opções vindas do Notion.
- Build Vite e lint com Oxlint.

---

### 🧱 API Django (`server/api/`)

**`server/api/views.py`**

- Rotas REST para tarefas, opções, databases e exploração.
- Views finas: validação HTTP na borda, regra de negócio em `server/services/`.
- Envelope de erro padronizado para validação, não encontrado, upstream e erro interno.
- SQLite usado só para estado operacional; o conteúdo fica no Notion.

---

### ⌘ CLI para IA (`cli/`)

**`python3 -m cli --json guia`**

- Saída humana ou JSON estável `{ "ok": true, "dados": ... }`.
- Lista, lê, cria, edita, move e conclui tarefas.
- Pesquisa, lê, escreve, edita e apaga blocos de páginas.
- Clona databases com schema e, opcionalmente, linhas.

---

### 🔗 Servidor MCP (`server/mcp_server.py`)

**`python3 server/mcp_server.py`**

- Expõe ferramentas `notion.*` para hosts MCP.
- Reusa os mesmos services da API e da CLI.
- Marca operações de escrita/destrutivas para confirmação no host.
- Pode rodar em `stdio` ou Streamable HTTP para depuração local.

---

### 🐙 Inventário GitHub (`server/services/inventario_github.py`)

**`python3 -m cli --json atualizar-github --contas conta-um,conta-dois`**

- Cria ou atualiza um database de repositórios no Notion.
- Materializa propriedades úteis: linguagem, estrelas, issues, licença, datas e flags.
- Escreve o README de cada repositório numa subpágina filha.
- Usa hash para reescrever README apenas quando o conteúdo mudou.

---

### ✅ Gate de Qualidade (`scripts/quality_check.py`)

**`python3 scripts/quality_check.py`**

- Roda Ruff, Pytest, Oxlint e build Vite.
- Tem modos parciais `--python-only` e `--front-only`.
- É o comando local obrigatório antes de fechar mudanças.

---

## 🎯 Como Usar

### Opção 1: Menu interativo (recomendado)

```bash
# Instale o pacote local e abra o menu
python3 start_app.py
```

No menu, use:

- **Iniciar tudo** para subir API Django e SPA React.
- **Configurar** para apontar token do Notion e escolher database.
- **Para IA e integrações** para acessar CLI, MCP, mapa e inventário GitHub.
- **Qualidade** para rodar o gate local.

### Opção 2: Setup manual para desenvolvimento

```bash
# Instale dependências Python de desenvolvimento
pip install -e ".[dev]"

# Instale extras opcionais do servidor e MCP
pip install -e ".[server,mcp]"

# Instale dependências do front
cd front
npm install
cd ..
```

```bash
# Configure variáveis locais
cp .env.example .env
```

Edite `.env` com valores reais apenas no seu ambiente local. Nunca versione esse arquivo.

### Variáveis principais

| Variável | Obrigatória? | Uso |
|---|---:|---|
| `NOTION_TOKEN` | Sim | Token da integração do Notion. |
| `NOTION_DATABASE_ID` | Para tarefas | Database usado pela todolist. |
| `OPENROUTER_API_KEY` | Opcional | Camada de IA copiloto. |
| `GITHUB_TOKEN` | Opcional | Repositórios privados da própria conta. |
| `GITHUB_CONTAS` | Opcional | Contas GitHub padrão para inventário. |

---

## ⌘ CLI para IA

Comece pelo guia automático:

```bash
python3 -m cli --json guia
```

Comandos comuns:

```bash
# Tarefas
python3 -m cli --json listar
python3 -m cli --json criar "Estudar API do Notion" --status "Entrada"
python3 -m cli --json editar <task_id> --status "Assim que possível"
python3 -m cli --json concluir <task_id> "Concluída"
python3 -m cli --json opcoes

# Workspace e databases
python3 -m cli --json databases
python3 -m cli --json escolher-database <database_id>
python3 -m cli --json mapear
python3 -m cli --json linhas <database_id>

# Conteúdo de páginas
python3 -m cli --json buscar "nota de reunião"
python3 -m cli --json conteudo <page_id>
python3 -m cli --json escrever <page_id> $'# Resumo\n\n- ponto um'
python3 -m cli --json editar-bloco <block_id> "## Novo título"
python3 -m cli --json apagar-bloco <block_id> --sim

# Clonagem e GitHub
python3 -m cli --json clonar-database <database_id> --titulo "Cópia" --com-linhas
python3 -m cli --json atualizar-github --contas conta-um,conta-dois
```

`apagar-bloco` é destrutivo e exige `--sim`. No Notion, a exclusão arquiva o bloco; a
recuperação depende da lixeira/permissões do workspace.

---

## 🔌 API, MCP e Integrações

### API local

Quando o menu sobe tudo, a API fica em:

```text
http://127.0.0.1:8000/
```

Rotas principais:

| Rota | Uso |
|---|---|
| `GET /api/health` | Health check. |
| `GET /api/tarefas` | Lista tarefas. |
| `POST /api/tarefas` | Cria tarefa. |
| `PATCH /api/tarefas/{id}` | Edita tarefa. |
| `GET /api/opcoes` | Lista opções de status/esforço/áreas. |
| `GET /api/databases` | Lista databases visíveis. |
| `GET /api/databases/{id}` | Explora linhas de um database genérico. |

### MCP

O servidor MCP expõe ferramentas de tarefas, conteúdo, clonagem e exploração. Consulte
[`docs/MCP.md`](docs/MCP.md) para transportes, confirmação de escrita e contratos.

### Integrações externas

- **Notion API:** fonte de verdade para páginas, databases, tarefas e conteúdo.
- **GitHub API:** inventário de repositórios e READMEs em database do Notion.
- **OpenRouter:** camada opcional de IA copiloto.

Detalhes operacionais estão em [`docs/INTEGRACOES.md`](docs/INTEGRACOES.md) e
[`docs/IA-CAMADA.md`](docs/IA-CAMADA.md).

---

## 🔒 Segurança e Dados

- `.env` fica fora do Git e deve ser criado localmente a partir de `.env.example`.
- Tokens, IDs reais e artefatos do workspace não devem ser versionados.
- `mapa.json` e `mapa.html` são gerados localmente e podem conter nomes/URLs reais.
- Testes não chamam APIs reais; HTTP externo deve ser mockado.
- Escritas destrutivas têm proteção na CLI (`--sim`) e hints de confirmação no MCP.
- Logs e mensagens devem ajudar debug sem expor segredo.

---

## ✅ Qualidade

Rode o gate completo antes de entregar mudanças:

```bash
python3 scripts/quality_check.py
```

Modos úteis:

```bash
python3 scripts/quality_check.py --python-only
python3 scripts/quality_check.py --front-only
```

O gate cobre:

- `ruff check .`
- `pytest -q`
- `npm run lint`
- `npm run build`

O contrato de pronto está em [`docs/QUALIDADE.md`](docs/QUALIDADE.md). O roteiro para
agentes e mantenedores está em [`AGENTS.md`](AGENTS.md).

---

## 📚 Documentação

| Documento | Quando ler |
|---|---|
| [`docs/README.md`](docs/README.md) | Índice geral da documentação. |
| [`docs/CONTRATOS.md`](docs/CONTRATOS.md) | Contratos de API, objetos e camadas. |
| [`docs/MCP.md`](docs/MCP.md) | Ferramentas MCP e política de confirmação. |
| [`docs/INTEGRACOES.md`](docs/INTEGRACOES.md) | GitHub, arquivos locais, schemas e segurança. |
| [`docs/PLANO.md`](docs/PLANO.md) | Roadmap e visão de evolução. |
| [`docs/QUALIDADE.md`](docs/QUALIDADE.md) | Gate local, CI e critério de pronto. |
| [`IA.md`](IA.md) | Linha do tempo técnica e decisões do projeto. |

---

## 📝 Licença

Este projeto está sob a licença MIT. Veja [`LICENSE`](LICENSE).

---

## 👤 Autor

**Felipe Alcantara**

- GitHub: [@Felipe-Alcantara](https://github.com/Felipe-Alcantara)
- Repositório: [Felipe-Alcantara/Automa-es-do-Notion](https://github.com/Felipe-Alcantara/Automa-es-do-Notion)

---

## 🤝 Contribuições

Contribuições são bem-vindas. Antes de abrir uma mudança, leia
[`CONTRIBUTING.md`](CONTRIBUTING.md), rode o gate de qualidade e mantenha a documentação
viva atualizada no mesmo passo.

⭐ Se este projeto foi útil, considere deixar uma estrela no GitHub.
