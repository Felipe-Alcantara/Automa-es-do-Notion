# 🗺️ PLANO — Roadmap e visão final do projeto

> **O que é este documento**: o plano de longo prazo do projeto — para onde ele caminha,
> como cada peça se encaixa e como fica no final. Cataloga o que já existe, as ideias
> levantadas e as fases previstas.
>
> **Documento vivo**: deve ser atualizado junto com [`README.md`](../README.md) e
> [`IA.md`](../IA.md) sempre que uma decisão ou fase mudar. Não é uma lista de tarefas
> fechada — o trabalho futuro está aberto a quem quiser contribuir.
>
> **Tom**: as fases abaixo são **próximos passos abertos à comunidade**, não obrigações
> internas. Cada uma pode ser pegada de forma independente.
>
> **Documentos irmãos** (em [`docs/`](README.md)): [MODELOS-DE-USO.md](MODELOS-DE-USO.md),
> [PORTABILIDADE.md](PORTABILIDADE.md), [SAAS.md](SAAS.md), [ESCALA.md](ESCALA.md),
> [OTIMIZACAO.md](OTIMIZACAO.md) e [IDEIAS-EXTRAS.md](IDEIAS-EXTRAS.md).

---

## 📋 Índice

- [🎯 Visão final — como o projeto fica no final](#-visão-final--como-o-projeto-fica-no-final)
- [🏛️ Arquitetura-alvo](#️-arquitetura-alvo)
- [✅ Estado atual — o que já está pronto](#-estado-atual--o-que-já-está-pronto)
- [🧭 Decisões fixadas](#-decisões-fixadas)
- [🚀 Roadmap em fases](#-roadmap-em-fases)
- [💡 Catálogo de ideias / brainstorm](#-catálogo-de-ideias--brainstorm)
- [🛡️ Princípios e guarda-corpos](#️-princípios-e-guarda-corpos)
- [📚 Glossário e projetos do ecossistema](#-glossário-e-projetos-do-ecossistema)

---

## 🎯 Visão final — como o projeto fica no final

No estado-alvo, **o Notion é o banco de dados**, um **front web próprio** é a interface,
e a **IA é o cérebro**. A pessoa lê e adiciona tarefas no todolist; a partir daí,
**agentes** pegam tarefas, executam o trabalho (código, artigos, roteiros, anotações,
estudos, pesquisas, resumos, ideias) e **registram o resultado de volta no Notion**.

O usuário não precisa operar os agentes na mão: ele **vê, lê e adiciona tarefas**, e os
agentes fazem e registram. Os modelos vêm de vários provedores via **OpenRouter**,
escolhidos por custo/objetivo.

### Exemplo concreto

```text
Tarefa:  Criar módulo em tal projeto
Tags:    GitHub, Programação
Fonte:   Página do Notion sobre aquele projeto — o que é, estado atual,
         como pode evoluir; a IA atualiza essa página enquanto trabalha
```

Cada projeto do GitHub vira uma **página no Notion** (explicando do que se trata, como
está e como pode evoluir) e um **tópico no todolist**. Conforme a IA trabalha, ela
atualiza essa página com o progresso.

### Separação de responsabilidades

A peça-chave da visão é **não concentrar tudo num lugar só**:

- **Este repositório** é a **camada de dados do Notion + tasklist + front web**.
- O **cérebro/orquestrador de agentes** é o projeto irmão
  **[Felixo-AI-Core](https://github.com/Felipe-Alcantara/Felixo-AI-Core)**.
- A conversa entre os dois acontece via **MCP** (Model Context Protocol): este projeto
  oferece ferramentas de Notion; o Felixo-AI-Core decide qual agente usa qual ferramenta.

---

## 🏛️ Arquitetura-alvo

```text
┌──────────────────────────────────────────────────────────────┐
│  Felixo-AI-Core (projeto irmão) — orquestra agentes, escolhe  │
│  modelos via OpenRouter, mantém memória. Fala via MCP.        │
└───────────────┬──────────────────────────────────────────────┘
                │ MCP (camada de ferramentas "notion")
┌───────────────▼──────────────────────────────────────────────┐
│  Servidor Django (este repositório)                           │
│   • api/           rotas REST + (futuro) servidor MCP         │
│   • services/      casos de uso (orquestra tasklist, ingestão)│
│   • integrations/  notion_starter (cliente), github, openrouter│
│   • core/          config, logging, token                     │
│   • SQLite         estado operacional (jobs, locks)           │
│  Front web (templates/HTMX ou estático servido pelo Django)   │
└───────────────┬──────────────────────────────────────────────┘
                │ API do Notion
┌───────────────▼──────────────────────────────────────────────┐
│  Notion — a fonte da verdade do conteúdo (tarefas, páginas)   │
└──────────────────────────────────────────────────────────────┘
```

**O que já existe vira a base, nada se descarta.** O pacote atual `notion_starter`
(cliente, helpers, schema, inventário, tasklist) passa a ser a camada
`integrations/notion` do servidor. É o princípio "ferramenta antes da solução
específica": primeiro a ferramenta reutilizável, depois a aplicação concreta por cima.

---

## ✅ Estado atual — o que já está pronto

| Peça | Onde | O que faz |
|---|---|---|
| **`NotionClient`** | [`client.py`](../src/notion_starter/client.py) | Cliente HTTP tipado: buscar, get/criar database, consultar (paginação), criar/atualizar/arquivar páginas |
| **Helpers de propriedade (escrita)** | [`properties.py`](../src/notion_starter/properties.py) | Montam os payloads de `title`, `email`, `select`, `status`, `date`… sem decorar o JSON do Notion |
| **Helpers de leitura** | [`readers.py`](../src/notion_starter/readers.py) | Par de leitura: `ler_title/ler_select/ler_status/ler_date/ler_relation…` e `extrair_valores(pagina)` → mapa coluna→valor simples (Fase 0) |
| **`comparar_schema`** | [`schema.py`](../src/notion_starter/schema.py) | Valida se um database tem as colunas/tipos esperados antes de escrever |
| **`construir_inventario` / `assinatura_perfil`** | [`inventory.py`](../src/notion_starter/inventory.py) | Lógica pura: árvore do workspace, duplicatas, órfãos e assinatura de perfil (colunas + opções) para distinguir databases parecidos |
| **`TaskList` / `Tarefa` / `CamposTarefa`** | [`tasks.py`](../src/notion_starter/tasks.py) | Camada de alto nível sobre um database de tarefas: listar/criar/atualizar_status/concluir |
| **Menu de entrada** | [`start_app.py`](../start_app.py) | Porta de entrada única: Iniciar/Rodar, Mapear, Instalar/Setup, Configurar, Status |
| **Exemplos executáveis** | [`examples/`](../examples/) | `export_rows`, `check_schema`, `sync_from_csv`, `gerenciar_tarefas`, `listar_paginas`, `coletar_mapa`, `gerar_arvore_html` |

Qualidade da base: **53 testes passando** (HTTP mockado via `responses`, sem token
real), `ruff` limpo e CI configurada.

---

## 🧭 Decisões fixadas

Decisões que orientam todo o roadmap (registradas para que o próximo a contribuir não
precise reler o histórico):

1. **Alcance** — uso pessoal (single-user, sem multiusuário ou autenticação complexa),
   porém **hospedado num servidor**, não só local. Inclui a capacidade de **analisar
   arquivos locais → enviar ao servidor → organizar no Notion**.
2. **Prioridade** — o primeiro "momento aha" é o **front web mostrando e editando as
   tarefas reais** do Notion.
3. **Papel da IA** — no estado final, **vários agentes** trabalham; a pessoa só lê e
   adiciona tarefas. Domínios além de programação: artigos, roteiros, anotações,
   estudos, pesquisas, resumos e ideias.
4. **Stack do servidor** — **Django + SQLite**, seguindo o padrão de qualidade adotado
   no projeto (Django como backend padrão; SQLite como banco inicial para sistemas
   locais/baixa concorrência).
5. **Orquestração de agentes** — **não** é reimplementada aqui. Integra-se ao
   [Felixo-AI-Core](https://github.com/Felipe-Alcantara/Felixo-AI-Core) via **MCP**:
   este projeto vira o backend de uma camada de ferramentas `notion`.
6. **Camada de IA** — **provedor plugável**, com dois mundos: **OpenRouter**
   (pague por uso) **e assinaturas** que a pessoa já paga (Codex, Claude Code Pro,
   Cursor; futuramente Gemini CLI e Copilot CLI). **Espelha/reaproveita** os padrões já
   validados no [Openia](https://github.com/Felipe-Alcantara/Openia) — que trata tanto a
   chave do OpenRouter quanto o modo assinatura — em vez de reinventar.

---

## 🚀 Roadmap em fases

Cada fase é independente e entregue em passos pequenos e rastreáveis (um módulo por vez,
com testes). As assinaturas abaixo são **esboços** para guiar a implementação, não
contratos finais.

### Fase 0 — Helpers de leitura ✅

> **Entregue** [2026-06-25] em [`src/notion_starter/readers.py`](../src/notion_starter/readers.py),
> com testes puros em [`tests/test_readers.py`](../tests/test_readers.py). O contrato está
> em [CONTRATOS.md](CONTRATOS.md) §5.

**Objetivo**: hoje há helpers de *escrita* de propriedade, mas ler valores de volta de
uma página ainda é manual. Esta fase fecha o par.

**Esboço** (em `properties.py` ou novo `readers.py`):

```python
ler_title(prop) -> str
ler_select(prop) -> str | None
ler_status(prop) -> str | None
ler_date(prop) -> str | None
ler_relation(prop) -> list[str]
extrair_valores(pagina) -> dict[str, Any]   # mapa nome_coluna → valor simples
```

**Reusar**: o padrão puro e testado de `tarefa_de_pagina` em
[`tasks.py`](../src/notion_starter/tasks.py).

**Pronto quando**: leitura coberta por testes (sem rede) para cada tipo, espelhando os
helpers de escrita.

---

### Fase 1 — Robustez do cliente

**Objetivo**: tornar o `NotionClient` resistente a rate limit e falhas temporárias.

**Esboço**: parâmetros `max_retries` e `backoff_base` no construtor; tratamento de
HTTP 429 respeitando `Retry-After`; idempotência em escritas sujeitas a reprocessamento.

**Reusar**: o padrão de cliente resiliente (retry com backoff, tratamento de rate limit)
já documentado no guia de integração com API do GitHub do padrão de qualidade.

**Pronto quando**: testes simulam 429/5xx e verificam o backoff sem rede real.

---

### Fase 2 — Servidor Django + front web (o momento aha) ✅

> **Entregue** [2026-06-25]: esqueleto Django (`server/`) com config por ambiente,
> SQLite operacional e ação "Subir servidor" no menu (Infra — `e68a6db`); casos de uso
> e rotas REST (`GET/POST /api/tarefas`, `PATCH /api/tarefas/{id}`) com envelope de
> erro padronizado e 14 testes (Backend — `d60d428`); **front web** servido em `/`
> (templates/estáticos Django, JS vanilla consumindo a API REST, acessibilidade e
> 4 testes de integração — Agente 4, Onda 3).

**Objetivo**: abrir o navegador e ver/editar as tarefas reais do Notion num front
próprio.

**Estrutura** (por camadas, conforme o padrão): `api/` (rotas/serialização),
`services/` (casos de uso), `integrations/` (o `notion_starter`), `core/` (config,
logging, token). SQLite para estado operacional.

**Esboço de casos de uso** (`services/tarefas.py`, finos sobre a `TaskList`):

```python
listar_tarefas(status: str | None = None) -> list[Tarefa]
criar_tarefa(nome: str, status: str | None, prazo: str | None) -> Tarefa
mover_status(task_id: str, status: str) -> Tarefa
concluir_tarefa(task_id: str) -> Tarefa
```

**Esboço de rotas REST**:

```text
GET    /api/tarefas            lista (filtro opcional por status)
POST   /api/tarefas            cria
PATCH  /api/tarefas/{id}       move status / conclui
```

**Menu**: `start_app.py` ganha a ação "Subir servidor", mantendo o contrato de porta de
entrada única.

**Pronto quando**: o front lista e edita tarefas reais; casos de uso cobertos por testes
(Notion mockado); controllers/views finos.

---

### Fase 3 — Ingestão de arquivos locais → Notion ✅

> **Entregue** [2026-06-25] em `server/services/ingestao.py`: contrato `Fonte`,
> estratégias `FonteArquivos`/`FonteGitHub`, prévia textual limitada, caminhos relativos
> e criação/atualização idempotente pela propriedade `Origem`.

**Objetivo**: analisar arquivos locais, enviá-los ao servidor e organizá-los no Notion.

**Esboço** (`services/ingestao.py`): varre uma pasta, extrai metadados/resumo, cria ou
atualiza páginas. O **tipo de fonte** é um ponto de extensão (estratégia), para crescer
sem reescrever o núcleo:

```python
class Fonte(Protocol):
    def coletar(self) -> Iterable[ItemColetado]: ...

FonteArquivos(...)   # uma pasta local
FonteGitHub(...)     # repositórios (ver Fase 4)
```

**Pronto quando**: ao menos uma fonte funcionando ponta a ponta, com a parte pura
(montar o item a partir do arquivo) testada sem rede. ✅

---

### Fase 4 — Conector GitHub ✅

> **Entregue** [2026-06-25] em `server/integrations/github.py` e
> `server/services/sincronizar_github.py`: públicos/privados do próprio usuário,
> paginação/deduplicação, retry seletivo, rate limit, linguagens/README e sincronização
> idempotente de página + tarefa. Guia: [INTEGRACOES.md](INTEGRACOES.md).

**Objetivo**: cada repositório vira uma **página no Notion** (o que é, estado atual,
como pode evoluir) e um **tópico no todolist**.

**Esboço**:

```python
# integrations/github.py
listar_repos(usuario: str) -> list[RepoInfo]
detalhar_repo(repo: str) -> RepoInfo      # linguagens, README, tópicos…

# services/sincronizar_github.py
sincronizar(usuario: str) -> ResumoSync   # mapeia repo → página + tarefa
```

**Reusar**: o padrão reutilizável de integração com a API do GitHub do padrão de
qualidade (token, cliente resiliente, descoberta de repos públicos/privados,
enriquecimento, orquestração, tratamento de erro/rate limit) e os helpers de leitura da
Fase 0.

**Pronto quando**: um repositório de exemplo vira página + tarefa, com o mapeamento
testado. ✅

---

### Fase 5 — Camada de IA: OpenRouter **e assinaturas** (provedor plugável)

**Objetivo**: a IA lê o estado, decide e atua — começando como copiloto, evoluindo para
autônoma com limites. A camada **não assume um único provedor**: suporta tanto
**pague-por-uso (OpenRouter)** quanto **assinaturas/ferramentas que a pessoa já paga**.

**Dois mundos de provedor:**

- **OpenRouter (pague por uso)** — multi-modelo, catálogo ao vivo com preço por modelo.
- **Assinaturas / CLIs com conta própria** — apontar para a conta da pessoa em vez de
  consumir tokens cobrados à parte. Alvos: **Codex** (OpenAI), **Claude Code Pro**
  (Anthropic), **Cursor**, e — futuramente — **Gemini CLI** (Google) e
  **Copilot CLI** (GitHub).

**Esboço** (interface `ProvedorIA` única, para trocar de provedor/modo num lugar só):

```python
class ProvedorIA(Protocol):
    def completar(self, prompt: str, modelo: str) -> str: ...

# Implementações: ProvedorOpenRouter(...) e ProvedorAssinatura(...)
listar_modelos() -> list[Modelo]   # OpenRouter: via /api/v1/models, cache local
```

Cada provedor/assinatura é registrado de forma declarativa (Open/Closed): adicionar
"Copilot CLI" ou "Gemini CLI" depois é registrar mais um, sem mexer no núcleo.

**Reusar / espelhar o [Openia](https://github.com/Felipe-Alcantara/Openia)**, que já
resolve **os dois mundos** (chave do OpenRouter *e* modo assinatura):

- **Catálogo de modelos** via `https://openrouter.ai/api/v1/models` (não exige chave
  para listar), com **cache de 24h** e ordenação por preço, escolha em dois passos
  (empresa → modelo) — referência: `openia/models.py`.
- **Chave fora do repositório** e **chaves nomeadas**, repassadas por variável de
  ambiente — referência: `openia/config.py`.
- **Modo assinatura** (rodar a ferramenta com o login da própria conta, sem OpenRouter)
  e **contrato declarativo em registry** (Open/Closed) com a flag de suporte a
  assinatura — referência: `openia/interfaces/base.py`.

Vale avaliar **depender do / extrair do Openia** em vez de duplicar. Detalhes de
economia em [OTIMIZACAO.md](OTIMIZACAO.md) e [SAAS.md](SAAS.md).

**Casos de uso**: linguagem natural → operações de tasklist; resumir/priorizar tarefas;
gerar rascunhos (artigos, roteiros, estudos, pesquisas).

**Guarda-corpos**: começa como **copiloto que sugere e a pessoa confirma**; só então
evolui para **autônomo com limites** (nunca apagar; só transições de status permitidas).
Os limites devem ficar registrados aqui e cobertos por teste.

**Pronto quando**: um caso de uso (ex.: "criar tarefa a partir de uma frase") funciona
com o provedor mockado em teste, e o modo confirmar-antes-de-escrever está garantido.

---

### Fase 6 — Integração com Felixo-AI-Core via MCP (o estado final)

**Objetivo**: vários agentes trabalhando; a pessoa só lê e adiciona tarefas.

O [Felixo-AI-Core](https://github.com/Felipe-Alcantara/Felixo-AI-Core) já mantém um
**catálogo de ferramentas MCP em camadas** (`project`, `git`, `memory`, `summary`,
`terminal`…), cada ferramenta com `access` (read/write) e, quando escreve,
`requiresConfirmation`. Esta fase adiciona uma **camada `notion`** a esse catálogo, com
este projeto como backend:

```text
notion.list_tasks            (read)
notion.create_task           (write, requiresConfirmation)
notion.move_status           (write, requiresConfirmation)
notion.update_project_page   (write, requiresConfirmation)
```

Este repositório **não** orquestra agentes — fornece as ferramentas e o estado; o
Felixo-AI-Core decide quem faz o quê. O resultado é a visão final: agentes executam e
registram no Notion, e a pessoa só lê e adiciona tarefas.

**Pronto quando**: as ferramentas `notion` respondem pelo seam MCP e escritas pedem
confirmação, mantendo a fronteira entre os dois projetos.

---

## 💡 Catálogo de ideias / brainstorm

Ideias levantadas ao longo do projeto, abertas a quem quiser contribuir:

- **Mais tipos de propriedade do Notion** — `relation`, `rollup`, `people`, `files`,
  `formula` (escrita e leitura).
- **Suporte a blocos** — manipular o conteúdo de páginas, não só as propriedades de
  database.
- **Sincronização bidirecional real** — hoje os fluxos são, em geral, de mão única.
- **Comando "renomear o pacote"** — automatizar a adaptação para quem usa o projeto como
  template.
- **Mais receitas de fonte de dados no menu** — banco, API, planilha, plugáveis.
- **Domínios além de programação** — artigos, roteiros, anotações, estudos, pesquisas,
  resumos e ideias, tudo registrado no Notion.

---

## 🛡️ Princípios e guarda-corpos

Valem para todas as fases:

- **Módulos coesos** — cada parte com uma responsabilidade clara; nada de arquivo
  "faz-tudo".
- **Integrações isoladas** — o core não depende do formato cru de nenhum provedor.
- **Contratos estáveis** — mudança quebradora é explícita, documentada e justificada.
- **Segredos fora do repositório** — token via variável de ambiente / `.env` ignorado
  pelo git; nada de IDs, caminhos ou chaves hardcoded.
- **Testar comportamento crítico** — HTTP mockado (`responses`), sem token nem rede real.
- **Porta de entrada única** — todo programa rodável passa pelo `start_app.py`.
- **Documentação viva** — `README.md` e `IA.md` atualizados junto com as mudanças.
- **Entregas pequenas e rastreáveis** — Conventional Commits, um passo coeso por vez.

---

## 📚 Glossário e projetos do ecossistema

- **`notion_starter`** — a biblioteca atual; a camada de dados do Notion deste
  repositório.
- **`TaskList` / assinatura de perfil** — abstrações já prontas em
  [`tasks.py`](../src/notion_starter/tasks.py) e
  [`inventory.py`](../src/notion_starter/inventory.py).
- **OpenRouter** — gateway que dá acesso a vários modelos de IA; lista modelos em
  `https://openrouter.ai/api/v1/models`.
- **[Openia](https://github.com/Felipe-Alcantara/Openia)** — launcher de CLIs de IA
  sobre o OpenRouter (chaves nomeadas, catálogo de modelos, registro de interfaces).
  Fonte dos padrões da Fase 5.
- **[Felixo-AI-Core](https://github.com/Felipe-Alcantara/Felixo-AI-Core)** — aplicativo
  orquestrador de agentes com camada MCP. Consome as ferramentas `notion` da Fase 6.
- **MCP (Model Context Protocol)** — o contrato pelo qual o Felixo-AI-Core chama as
  ferramentas expostas por este projeto.
