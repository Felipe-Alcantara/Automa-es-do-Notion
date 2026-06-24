# 🧱 notion-starter-boilerplate

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Notion API](https://img.shields.io/badge/Notion-API-000000?style=for-the-badge&logo=notion&logoColor=white)
![Boilerplate](https://img.shields.io/badge/tipo-boilerplate-8A2BE2?style=for-the-badge)
![Tests](https://img.shields.io/badge/tests-22%20passing-success?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**Ponto de partida tipado para construir projetos sobre a API do Notion — clone, adapte e construa em cima.**

[📖 API do Notion](https://developers.notion.com/) • [▶️ Menu de Entrada](#️-menu-de-entrada) • [🧩 Como Usar o Template](#-como-usar-este-template) • [🤝 Contribuir](#-contribuições)

</div>

---

Um **boilerplate** (esqueleto inicial) com opinião para quem vai começar um projeto
que conversa com o **Notion**. Em vez de começar do zero, você clona este repositório
e já tem um cliente HTTP tipado, helpers para montar propriedades sem decorar o JSON
do Notion, validação de schema, exceções claras, testes, CI e um menu de entrada.

É independente de framework: uma única dependência de runtime (`requests`), sem Django,
sem estado global. Você traz a sua própria fonte de dados e constrói a lógica do seu
projeto em cima da base.

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
│   ├── properties.py             # Helpers de propriedade (title, email, date...)
│   ├── exceptions.py             # Hierarquia de exceções (NotionSyncError)
│   ├── logging.py                # Logging opcional, silencioso por padrão
│   ├── constants.py              # URL base, timeout, versão da API, env var
│   └── __init__.py               # API pública
│
├── 📁 tests/                     # Testes com HTTP mockado (responses)
├── 📁 examples/                  # Scripts de exemplo executáveis (ponto de partida)
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
  paginação automática nas consultas.
- **Payloads tipados** (`TypedDict`) e exceções explícitas e capturáveis.
- **Helpers de `properties`** (`title`, `email`, `select`, `date`, …) para montar
  valores de propriedade.
- **`comparar_schema`** para checar se um database tem as colunas que você espera.
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

- **Iniciar / Rodar** — executa um exemplo (`export_rows`, `check_schema`, `sync_from_csv`).
- **Instalar / Setup** — instala o pacote com as deps de dev e cria o `.env`.
- **Configurar** — aponta o token do Notion (gravado no `.env`, fora do git).
- **Status / Sair** — mostra o estado real (Python, pacote, `.env`, token) e sai.

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

## 🧪 Desenvolvimento

```bash
# Instale com as dependências de desenvolvimento
pip install -e ".[dev]"

# Rode os testes e o lint
pytest -q
ruff check .
```

Os testes mockam todo o HTTP com [`responses`](https://github.com/getsentry/responses);
nenhum token real do Notion ou acesso à rede é necessário.

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
