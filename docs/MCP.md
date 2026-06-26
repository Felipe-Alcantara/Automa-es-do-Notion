# 🔗 MCP — Ponte com o Felixo-AI-Core

> **O que é este documento**: descreve a camada MCP (Model Context Protocol)
> deste projeto — como as capacidades de Notion são expostas como ferramentas
> que agentes do Felixo-AI-Core consomem.
>
> **MCP e CLI são irmãos.** Ambos são **bordas finas sobre os mesmos `services/`** —
> nenhum reimplementa regra de negócio. O **MCP** serve os agentes do Felixo-AI-Core;
> a **CLI** ([Ciclo 2](AGENTES.md#-ciclo-2--agentes-do-front-rico-cli-e-multi-tabela),
> pasta `cli/`) serve uso direto por linha de comando e uma IA local. Quem mexer numa
> operação deve garantir que a regra continue nos `services`, para as duas bordas
> herdarem o mesmo comportamento.

---

## Visão geral

O [Felixo-AI-Core](https://github.com/Felipe-Alcantara/Felixo-AI-Core) é o
orquestrador de agentes. Este projeto é a **camada de dados do Notion**. A
comunicação entre os dois acontece via **MCP**: este projeto oferece
ferramentas; o Felixo-AI-Core decide qual agente usa qual ferramenta.

```text
┌─────────────────────────────────┐
│  Felixo-AI-Core (orquestrador) │
│  Decide quem faz o que         │
└──────────┬──────────────────────┘
           │ MCP (stdio)
┌──────────▼──────────────────────┐
│  mcp_server.py (este projeto)   │
│  Ferramentas notion.*           │
│  Invólucros sobre services/     │
└──────────┬──────────────────────┘
           │ notion_starter
┌──────────▼──────────────────────┐
│  API do Notion                  │
└─────────────────────────────────┘
```

---

## Ferramentas expostas

| Ferramenta | Acesso | Confirmação | O que faz |
|---|---|---|---|
| `notion.list_tasks` | read | não | Lista tarefas, com filtro opcional por status |
| `notion.create_task` | write | sim | Cria uma nova tarefa |
| `notion.move_status` | write | sim | Move uma tarefa para outro status |
| `notion.conclude_task` | write | sim | Conclui uma tarefa com o status informado |
| `notion.update_project_page` | write | sim | Atualiza metadados de uma página de projeto |
| `notion.search` | read | não | Pesquisa páginas e databases visíveis à integração |
| `notion.read_page_content` | read | não | Lê o conteúdo (corpo) de uma página como Markdown |
| `notion.append_content` | write | sim | Anexa conteúdo (Markdown) ao final de uma página |
| `notion.edit_block` | write | sim | Substitui o texto de um bloco existente |
| `notion.delete_block` | **delete** | **sim** | Apaga (arquiva) um bloco — **destrutivo** |

As ferramentas de tarefas/projetos cobrem as **propriedades**; as de conteúdo
(`search`, `read_page_content`, `append_content`, `edit_block`, `delete_block`)
dão acesso ao **corpo** das páginas — qualquer página visível à integração, não
só os databases configurados. Assim a IA pesquisa, lê notas, escreve e edita
conteúdo, e — com confirmação — apaga blocos.

Cada ferramenta é um invólucro fino sobre os casos de uso de
`server/services/tarefas.py`, `server/services/projetos.py` e
`server/services/conteudo.py` — não reimplementa regra de negócio. Entradas
textuais obrigatórias são validadas na borda MCP e erros internos/upstream são
sanitizados.

### Anotações MCP

As ferramentas declaram anotações MCP:

- **read** (`notion.list_tasks`): `readOnlyHint=True`, `destructiveHint=False`,
  `openWorldHint=True`
- **create** (`notion.create_task`): `readOnlyHint=False`, `destructiveHint=False`,
  `idempotentHint=False`, `openWorldHint=True`
- **update** (`notion.move_status`, `notion.conclude_task`,
  `notion.update_project_page` e `notion.edit_block`):
  `readOnlyHint=False`, `destructiveHint=False`, `idempotentHint=True`,
  `openWorldHint=True`
- **read** (`notion.search`, `notion.read_page_content`): `readOnlyHint=True`,
  `destructiveHint=False`, `openWorldHint=True`
- **create** (`notion.append_content`): `readOnlyHint=False`,
  `destructiveHint=False`, `idempotentHint=False`, `openWorldHint=True`
- **delete** (`notion.delete_block`): `readOnlyHint=False`,
  **`destructiveHint=True`**, `idempotentHint=True`, `openWorldHint=True` — o
  host deve sempre confirmar antes de executar

Essas anotações são apenas **hints do protocolo**. A confirmação obrigatória é
responsabilidade do host: o catálogo do Felixo-AI-Core deve registrar toda ferramenta
`write` com `requiresConfirmation: true`.

---

## Como rodar

### CLI irmã

A CLI do Ciclo 2 fica em `cli/` e usa os mesmos casos de uso de
`server/services/tarefas.py`. Ela é útil quando uma IA local ou script quer uma
saída JSON estável sem subir servidor MCP:

```bash
python -m cli --json listar
python -m cli --json criar "Nova tarefa" --status "Entrada"
python -m cli --json editar <task_id> --status "Assim que possível"
python -m cli --json opcoes
python -m cli --json mapear
```

Contrato de saída:

```json
{ "ok": true, "dados": {} }
```

Em erro:

```json
{ "ok": false, "erro": { "mensagem": "..." } }
```

### Pré-requisitos

```bash
pip install -e ".[mcp]"    # instala MCP Python SDK 1.x + notion_starter
```

### Variáveis de ambiente

O servidor MCP lê do ambiente (ou do `.env` na raiz):

| Variável | Obrigatória | Descrição |
|---|---|---|
| `NOTION_TOKEN` | sim | Token de integração do Notion |
| `NOTION_DATABASE_ID` | sim | ID do database de tarefas |

### Execução

```bash
# stdio (padrão — o Felixo-AI-Core spawna assim)
python server/mcp_server.py

# Streamable HTTP para debug local (endpoint http://127.0.0.1:8000/mcp)
python server/mcp_server.py --transport streamable-http
```

Ou pelo menu interativo:

```bash
python start_app.py
# → "Subir servidor MCP"
```

O menu abre o MCP em um terminal dedicado; o menu principal permanece livre para
subir a API web ou iniciar outras ações em paralelo.

---

## Configuração no Felixo-AI-Core

A configuração abaixo representa o contrato esperado para o cliente de servidores MCP
externos do Felixo-AI-Core:

```json
{
  "notion": {
    "command": "python",
    "args": ["server/mcp_server.py"],
    "cwd": "/caminho/para/Automa-es-do-Notion",
    "env": {
      "NOTION_TOKEN": "${NOTION_TOKEN}",
      "NOTION_DATABASE_ID": "${NOTION_DATABASE_ID}"
    }
  }
}
```

### Contrato do catálogo

Em 25 de junho de 2026, o catálogo real em
`app/electron/services/mcp/felixo-tool-catalog.cjs` incorporou a camada `notion`
no commit `75c8a12`. As entradas registradas são:

```javascript
{
  name: 'notion.list_tasks',
  layer: 'notion',
  access: 'read',
  status: 'planned',
  description: 'List Notion tasks, optionally filtered by status.',
},
{
  name: 'notion.create_task',
  layer: 'notion',
  access: 'write',
  status: 'planned',
  requiresConfirmation: true,
  description: 'Create a task in Notion after confirmation.',
},
{
  name: 'notion.move_status',
  layer: 'notion',
  access: 'write',
  status: 'planned',
  requiresConfirmation: true,
  description: 'Move a Notion task to another status after confirmation.',
},
{
  name: 'notion.conclude_task',
  layer: 'notion',
  access: 'write',
  status: 'planned',
  requiresConfirmation: true,
  description: 'Conclude a Notion task after confirmation.',
},
{
  name: 'notion.update_project_page',
  layer: 'notion',
  access: 'write',
  status: 'planned',
  requiresConfirmation: true,
  description: 'Update a Notion project page after confirmation.',
},
```

O catálogo já fixa a política de confirmação do host. A conexão e o ciclo de vida de
servidores MCP externos ainda dependem da implementação do cliente prevista no roadmap
do Felixo-AI-Core; até lá, o servidor deste projeto pode ser validado diretamente por
`stdio` ou Streamable HTTP.

---

## Arquitetura e decisões

1. **Sem Django**: o servidor MCP cria a `TaskList` diretamente do
   `notion_starter`, lendo token e database ID do ambiente. Não depende do
   Django — é um processo separado do servidor web.

2. **DI dos serviços**: as funções de `services.tarefas` aceitam um parâmetro
   `tasklist` injetável. O MCP server cria a `TaskList` e injeta, seguindo o
   mesmo padrão que os testes usam.

3. **Sem delete**: nenhuma ferramenta apaga dados. Mudanças de tarefa e atualização
   de página de projeto requerem confirmação no host.

4. **Transportes**: `stdio` é o padrão local para o Felixo-AI-Core. Streamable HTTP
   existe apenas para depuração local. SSE legado não é exposto.

5. **Página de projeto por caso de uso**: `notion.update_project_page` constrói um
   `RepoInfo` normalizado e delega a `services.projetos.atualizar_pagina_projeto`.
   O serviço reutiliza `CamposProjeto` e o mapeamento da sincronização GitHub; o MCP
   não monta payload cru do Notion.

---

## Testes

```bash
python -m pytest tests/test_mcp_server.py tests/test_services_projetos.py tests/test_cli_notion_tasks.py -v
```

Os testes cobrem:

- superfície pública com namespace `notion.*`;
- anotações MCP de leitura, criação e atualização;
- serialização de `Tarefa` sem expor `bruto`;
- validação de entradas e variáveis de ambiente;
- ferramentas com Notion mockado (`responses`);
- seleção real do transporte passado ao SDK;
- metadata do servidor.

Validação de 25 de junho de 2026: **32 testes focados** (`test_mcp_server.py` +
`test_services_projetos.py`) e handshake real por `stdio` listando as cinco
ferramentas `notion.*`.
