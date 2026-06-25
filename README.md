# 🧱 notion-starter-boilerplate

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Notion API](https://img.shields.io/badge/Notion-API-000000?style=for-the-badge&logo=notion&logoColor=white)
![Boilerplate](https://img.shields.io/badge/tipo-boilerplate-8A2BE2?style=for-the-badge)
![Tests](https://img.shields.io/badge/tests-246%20passing-success?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**Ponto de partida tipado para construir projetos sobre a API do Notion — clone, adapte e construa em cima.**

[📖 API do Notion](https://developers.notion.com/) • [▶️ Menu de Entrada](#️-menu-de-entrada) • [🧩 Como Usar o Template](#-como-usar-este-template) • [🤝 Contribuir](#-contribuições)

</div>

---

Um **boilerplate** (esqueleto inicial) com opinião para quem vai começar um projeto
que conversa com o **Notion**. Em vez de começar do zero, você clona este repositório
e já tem um cliente HTTP tipado, helpers para montar propriedades sem decorar o JSON
do Notion, validação de schema, exceções claras, testes, CI e um menu de entrada.

O core (`notion_starter`) é independente de framework: uma única dependência de
runtime (`requests`), sem estado global. O projeto também inclui um **servidor
Django opcional** (`server/`) com API REST para tarefas, pronto para subir com
`python start_app.py` → "Subir servidor". Você traz a sua própria fonte de dados
e constrói a lógica do seu projeto em cima da base.

> Este projeto começou como um módulo interno de empresa e foi generalizado para
> servir de ponto de partida aberto: clone, renomeie o pacote para o seu projeto e
> construa a partir daí. Não é uma dependência fechada — é o seu esqueleto.

## 📋 Índice

- [📋 Sobre o Projeto](#-sobre-o-projeto)
- [📁 Estrutura do Projeto](#-estrutura-do-projeto)
- [✨ O que já vem pronto](#-o-que-já-vem-pronto)
- [▶️ Menu de Entrada](#️-menu-de-entrada)
- [🧩 Como Usar Este Template](#-como-usar-este-template)
- [🚀 Usando o Cliente em Código](#-usando-o-cliente-em-código)
- [📖 Lendo com Paginação](#-lendo-com-paginação)
- [🛡️ Validando o Schema Primeiro](#-validando-o-schema-primeiro)
- [🔄 GitHub e Ingestão](#-github-e-ingestão)
- [🧩 Helpers de Propriedades](#-helpers-de-propriedades)
- [🔧 Superfície da API](#-superfície-da-api)
- [📊 Logging](#-logging)
- [⚠️ Exceções](#-exceções)
- [💡 Exemplos](#-exemplos)
- [🧪 Desenvolvimento](#-desenvolvimento)
- [📝 Licença](#-licença)
- [👤 Autor](#-autor)
- [🤝 Contribuições](#-contribuições)

---

## 📋 Sobre o Projeto

`notion-starter-boilerplate` resolve o "dia 1" de quem vai integrar com o **Notion**:
em vez de montar do zero a estrutura, o tratamento de erro e a tipagem, você parte de
uma base que já resolve três dores comuns:

- **Montar payloads de propriedade** sem decorar o formato JSON do Notion.
- **Falhar cedo e com clareza** — exceções explícitas em vez de erros crus de HTTP.
- **Confiar no destino** — validar o schema de um database antes de escrever nele.

Tudo isso com **tipagem forte** (`TypedDict`/`dataclass`), **uma única dependência**
de runtime e estrutura modular pronta para você estender com a lógica do seu projeto.

## 📁 Estrutura do Projeto

```
notion-starter-boilerplate/
│
├── 📁 src/notion_starter/        # O core reutilizável (renomeie para o seu projeto)
│   ├── client.py                 # NotionClient — wrapper HTTP tipado
│   ├── schema.py                 # comparar_schema / SchemaComparison
│   ├── properties.py             # Helpers de escrita de propriedade (title, email, date...)
│   ├── readers.py                # Helpers de leitura de propriedade (ler_title, extrair_valores...)
│   ├── tasks.py                  # TaskList — camada de alto nível para databases de tarefas
│   ├── inventory.py              # Mapeamento/inventário do workspace (lógica pura)
│   ├── exceptions.py             # Hierarquia de exceções (NotionSyncError)
│   ├── logging.py                # Logging opcional, silencioso por padrão
│   ├── constants.py              # URL base, timeout, versão da API, env var
│   └── __init__.py               # API pública
│
├── 📁 server/                    # Servidor Django (opcional — pip install -e ".[server]")
│   ├── manage.py                 # CLI do Django
│   ├── mcp_server.py             # Servidor MCP de ferramentas notion.*
│   ├── config/                   # Projeto Django: settings, urls, wsgi, asgi
│   ├── core/                     # Config por ambiente (sem HTTP, sem regra de negócio)
│   ├── integrations/             # Fábrica fina sobre o notion_starter + OpenRouter
│   ├── services/                 # Casos de uso (tarefas, IA copiloto)
│   ├── api/                      # Borda HTTP: rotas REST + health
│   ├── operations/               # Estado operacional em SQLite (jobs, locks)
│   ├── templates/                # Front web (template Django para tarefas)
│   └── static/                   # CSS e JS do front (vanilla, sem framework)
│
├── 📁 tests/                     # Testes (HTTP mockado + Django test client)
├── 📁 examples/                  # Scripts de exemplo executáveis (ponto de partida)
├── 📁 docs/                      # Visão e estratégia: roadmap, SaaS, escala, otimização
│
├── start_app.py                  # Menu de entrada interativo (instala, configura, roda)
├── .env.example                  # Modelo de variáveis de ambiente
├── pyproject.toml                # Build, dependências e config de tooling
├── IA.md                         # Contexto operacional para IA / mantenedores
├── CONTRIBUTING.md               # Guia de contribuição
├── README.md                     # Este arquivo
└── LICENSE
```

## ✨ O que já vem pronto

- **`NotionClient`** — cria/consulta databases, cria/atualiza/arquiva páginas, com
  paginação automática, retry/backoff seguro para operações idempotentes e cache
  de schema com TTL. Criações repetem apenas rate limit confirmado (429/529), não
  falhas ambíguas de rede/5xx que poderiam gerar duplicatas.
- **Payloads tipados** (`TypedDict`) e exceções explícitas e capturáveis.
- **Helpers de `properties`** (`title`, `email`, `select`, `date`, …) para montar
  valores de propriedade.
- **Helpers de `readers`** (`ler_title`, `ler_select`, `extrair_valores`, …) para
  ler propriedades de páginas sem mexer no JSON cru.
- **`TaskList`** — camada de alto nível para databases de tarefas (listar, criar,
  atualizar status, concluir), com colunas configuráveis.
- **`comparar_schema`** para checar se um database tem as colunas que você espera.
- **`construir_inventario`** para mapear o workspace (árvore, duplicatas, órfãos).
- **Servidor Django** (opcional) — API REST de tarefas (`GET/POST /api/tarefas`,
  `PATCH /api/tarefas/{id}`), com config por ambiente, envelope de erro padronizado
  e estado operacional em SQLite. Instale com `pip install -e ".[server]"`.
- **Front web** — interface no navegador para ver e editar tarefas reais, servida
  pelo Django em `/`. Lista com filtro por status, criação, movimentação e conclusão
  por mudança de status, com estados de carregando/vazio/erro e feedback acessível.
  JS vanilla consumindo a API REST, sem framework.
- **IA copiloto** — camada de IA plugável (OpenRouter) para linguagem natural →
  operações de tasklist. Sugere ações, pessoa confirma antes de escrever.
- **Servidor MCP** — expõe `notion.list_tasks`, `notion.create_task`,
  `notion.move_status`, `notion.conclude_task` e `notion.update_project_page` como
  invólucros dos casos de uso. Escritas são anotadas para confirmação; a política
  obrigatória fica no catálogo do host Felixo-AI-Core. Instale com
  `pip install -e ".[mcp]"`.
- **Logging opcional**; silencioso por padrão (`NullHandler`, amigável a bibliotecas).
- **Exemplos executáveis**, testes com HTTP mockado, CI e um menu de entrada — a base
  para você só adicionar a lógica do seu projeto.

---

## ▶️ Menu de Entrada

Forma mais simples de começar — abre um menu interativo onde você instala as
dependências, configura o token, vê o estado do ambiente e roda os exemplos,
sem decorar comando nenhum:

```bash
python start_app.py
```

No menu você escolhe:

- **Iniciar / Rodar** — executa um exemplo (`export_rows`, `check_schema`, `sync_from_csv`, `gerenciar_tarefas`).
- **Subir servidor** — instala o Django (se necessário), aplica migrações e sobe a API REST local (`/api/health`, `/api/tarefas`).
- **Subir servidor MCP** — instala o SDK MCP e inicia a ponte em `stdio` ou
  Streamable HTTP para depuração local.
- **Mapear workspace** — coleta o `mapa.json` e gera o `mapa.html` navegável do seu Notion.
- **Instalar / Setup** — instala o pacote com as deps de dev e cria o `.env`.
- **Configurar** — aponta o token do Notion (gravado no `.env`, fora do git).
- **Status / Sair** — mostra o estado real (Python, pacote, `.env`, token) e sai.

Cada opção abre um **terminal dedicado**. O menu principal continua disponível
para iniciar outras ações em paralelo — por exemplo, manter o servidor web e o
MCP ativos enquanto executa um exemplo ou consulta o status.

Na primeira execução, se as bibliotecas do menu (`questionary`, `rich`) não
estiverem instaladas, o script se oferece para instalá-las. Funciona em Windows,
Linux e macOS, e nenhum segredo é guardado no script — o token continua só em
variável de ambiente ou no `.env`.

---

## 🧩 Como Usar Este Template

Este repositório é feito para ser **clonado e adaptado**, não instalado como
dependência fechada. O fluxo típico:

```bash
# 1. Use como template (botão "Use this template" no GitHub) ou clone:
git clone https://github.com/flaviavs-commits/notion-starter-boilerplate.git meu-projeto
cd meu-projeto

# 2. Prepare o ambiente (ou use o menu: python start_app.py → Instalar/Setup)
pip install -e ".[dev]"

# 3. Configure o token (ou use o menu → Configurar)
cp .env.example .env   # edite e coloque seu NOTION_TOKEN
```

A partir daí, **o que você adapta**:

1. **Renomeie o pacote** `src/notion_starter/` para o nome do seu projeto e ajuste
   `name`/`packages` no [`pyproject.toml`](pyproject.toml).
2. **Defina o seu schema** — o mapa de colunas → tipos do seu database (veja
   [`examples/sync_from_csv.py`](examples/sync_from_csv.py)).
3. **Troque a fonte de dados** — os exemplos leem listas/CSV; aponte para o seu banco,
   API ou arquivo.
4. **Construa a sua lógica** em cima do `NotionClient` (uma camada de serviço, um job
   agendado, um comando, etc.).

Requer Python 3.10+.

---

## 🚀 Usando o Cliente em Código

```python
from notion_starter import NotionClient
from notion_starter import properties as p

client = NotionClient()  # lê NOTION_TOKEN do ambiente
# ou: NotionClient(token="ntn_...")

client.criar_pagina(
    database_id="seu_database_id",
    propriedades={
        "Nome": p.title("Ada Lovelace"),
        "Email": p.email("ada@example.com"),
        "Perfil": p.select("Engenharia"),
        "Cadastro": p.date("2026-06-24"),
    },
)
```

---

## 📖 Lendo com Paginação

```python
linhas = client.consultar_database("seu_database_id", buscar_todos=True)
for linha in linhas:
    print(linha["id"])
```

## 🛡️ Validando o Schema Primeiro

```python
from notion_starter import NotionClient, comparar_schema

client = NotionClient()
database = client.get_database("seu_database_id")

resultado = comparar_schema(database, {
    "Nome": "title",
    "Email": "email",
    "Cadastro": "date",
})

if resultado.compativel:
    ...  # pode exportar
else:
    print("faltando:", resultado.faltando)
    print("tipo errado:", resultado.tipo_errado)
    # resultado.levantar_se_incompativel()  # ou levanta NotionSchemaError
```

## 🗺️ Mapeando o Workspace

`construir_inventario` recebe os itens crus de `buscar()` e reconstrói a
estrutura: árvore de páginas/databases, duplicatas por nome, itens vazios e
órfãos (cujo parent não está visível). É lógica pura — sem rede.

```python
from notion_starter import NotionClient, construir_inventario

client = NotionClient()
itens = client.buscar(buscar_todos=True)
inv = construir_inventario(itens)

print(inv.total_paginas, inv.total_databases)
for titulo, repetidos in inv.duplicatas.items():
    print("duplicado:", titulo, "->", len(repetidos))
```

## ✅ Tasklist de Alto Nível

`TaskList` envolve um database de tarefas: lê, cria e atualiza tarefas com um
objeto `Tarefa` simples, sem mexer no JSON da API. Os nomes das colunas são
configuráveis (`CamposTarefa`) porque variam entre workspaces.

```python
from notion_starter import NotionClient, TaskList

tl = TaskList(NotionClient(), "seu_database_id")

for t in tl.listar(status="00. Inbox"):
    print(t.nome, "->", t.status)

tl.criar("Revisar PR", status="02. ASAP", prazo="2026-07-01")
tl.atualizar_status("id_da_tarefa", "06. Feito")
```

## 🔄 GitHub e Ingestão

O servidor inclui um cliente GitHub resiliente e fontes extensíveis para transformar
repositórios ou arquivos locais em páginas do Notion. A sincronização atualiza páginas
existentes e evita duplicar tarefas.

```python
from services.ingestao import FonteArquivos, ingerir
from services.sincronizar_github import sincronizar

ingerir(FonteArquivos("./documentos", extensoes=[".md", ".txt"]))
sincronizar("usuario", status_tarefa="Backlog")
```

Tokens ficam no ambiente; repositórios privados só são coletados quando o token pertence
ao mesmo usuário consultado. Schemas, variáveis e limites estão detalhados em
[`docs/INTEGRACOES.md`](docs/INTEGRACOES.md).

## 🧩 Helpers de Propriedades

| Helper | Tipo Notion |
|---|---|
| `title(str)` | `title` |
| `rich_text(str)` | `rich_text` |
| `email(str)` | `email` |
| `phone_number(str)` | `phone_number` |
| `url(str)` | `url` |
| `number(int \| float)` | `number` |
| `checkbox(bool)` | `checkbox` |
| `select(str)` | `select` |
| `status(str)` | `status` |
| `multi_select(list[str])` | `multi_select` |
| `date(inicio, fim=None)` | `date` (aceita `str`, `date`, `datetime`) |

## 🔧 Superfície da API

Métodos de `NotionClient`:

- **`buscar(query=None, page_size=100, buscar_todos=False, filtro=None)`** — busca páginas e databases compartilhados com a integração (endpoint `/search`); sem `query`, lista tudo o que é visível.
- **`get_database(database_id)`** — busca os metadados de um database.
- **`criar_database(pagina_id, titulo, propriedades)`** — cria um database filho de uma página.
- **`consultar_database(database_id, page_size=100, buscar_todos=False, filtro=None)`** — consulta com paginação.
- **`criar_pagina(database_id, propriedades)`** — cria uma página no database.
- **`atualizar_pagina(page_id, propriedades)`** — atualiza propriedades de uma página.
- **`arquivar_pagina(page_id)`** — arquiva uma página.

## 📊 Logging

O core é silencioso por padrão. Ative os handlers prontos ao rodar como script:

```python
from notion_starter import configure_logging

configure_logging(log_file="logs/notion_starter.log")
```

Em uma aplicação, basta configurar o logger `notion_starter` pela sua configuração
normal de logging.

## ⚠️ Exceções

Todos os erros derivam de `NotionSyncError`:

- **`NotionConfigurationError`** — token ou identificador ausente/inválido.
- **`NotionHTTPError`** — resposta não-2xx (`.status_code`, `.body`).
- **`NotionConnectionError`** — falha de rede ou timeout.
- **`NotionInvalidResponseError`** — resposta não-JSON.
- **`NotionSchemaError`** — database incompatível com o schema esperado.

## 💡 Exemplos

Veja [`examples/`](examples/) — são o ponto de partida para a sua lógica:

- [`export_rows.py`](examples/export_rows.py) — cria uma página por linha de uma lista de dicts.
- [`check_schema.py`](examples/check_schema.py) — valida o schema de um database.
- [`sync_from_csv.py`](examples/sync_from_csv.py) — fluxo end-to-end: lê um CSV, valida o schema e cria uma página por linha.
- [`gerenciar_tarefas.py`](examples/gerenciar_tarefas.py) — usa a `TaskList` para listar, criar e concluir tarefas num database de tarefas.
- [`listar_paginas.py`](examples/listar_paginas.py) — lista tudo que a integração enxerga (páginas e databases, com IDs).
- [`coletar_mapa.py`](examples/coletar_mapa.py) — varre o workspace e salva `mapa.json` (estrutura, duplicatas, órfãos, nº de linhas por database).
- [`gerar_arvore_html.py`](examples/gerar_arvore_html.py) — lê o `mapa.json` e gera um `mapa.html` navegável (árvore + destaques).

## 🗺️ Roadmap e Visão

Para onde o projeto caminha — de biblioteca tipada a um front próprio com IA sobre o
Notion — está documentado em [`docs/`](docs/README.md):
[roadmap e visão final](docs/PLANO.md), [modelos de uso](docs/MODELOS-DE-USO.md),
[portabilidade](docs/PORTABILIDADE.md) e os caminhos de evolução
([SaaS](docs/SAAS.md), [escala](docs/ESCALA.md), [otimização](docs/OTIMIZACAO.md) e
[ideias extras](docs/IDEIAS-EXTRAS.md)). A ponte com o Felixo-AI-Core está em
[`docs/MCP.md`](docs/MCP.md). São documentos de direção, abertos à contribuição.

## 🧪 Desenvolvimento

```bash
# Instale com as dependências de desenvolvimento
pip install -e ".[dev]"

# Para trabalhar no servidor (opcional):
pip install -e ".[server]"

# Para trabalhar no servidor MCP (opcional):
pip install -e ".[mcp]"

# Rode os testes e o lint
pytest -q
ruff check .
```

Os testes do core mockam todo o HTTP com [`responses`](https://github.com/getsentry/responses);
nenhum token real do Notion ou acesso à rede é necessário. Os testes do servidor
usam o Django test client e `TaskList` injetada — também sem rede. A suíte MCP valida
a superfície `notion.*`, anotações, transportes e entradas com o Notion mockado.

---

## 📝 Licença

Este projeto está sob a licença MIT — veja o arquivo [`LICENSE`](LICENSE).

## 👤 Autor

**notion-starter-boilerplate contributors**
- Repositório: [notion-starter-boilerplate](https://github.com/flaviavs-commits/notion-starter-boilerplate)
- Issues: [Reportar um problema](https://github.com/flaviavs-commits/notion-starter-boilerplate/issues)

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para:
- Reportar bugs
- Sugerir melhorias (mais tipos de propriedade, helpers de leitura, novos exemplos...)
- Melhorar a documentação

Veja o guia completo em [CONTRIBUTING.md](CONTRIBUTING.md).

---

⭐ Se este projeto foi útil, considere dar uma estrela no GitHub!
