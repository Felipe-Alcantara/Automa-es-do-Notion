# 🧩 Modularização — Automações do Notion

> **Estado em 2026-09-04:** a separação do antigo monorepo foi concluída. O hub
> permanece como documentação e roteamento; o código vive em três repositórios
> independentes, com releases Python publicados em `0.3.0`.

Este documento substitui a proposta antiga de separar core, servidor, frontend e
CLI. A proposta continua registrada no histórico do projeto, mas os nomes e
caminhos abaixo são a referência operacional atual.

## Arquitetura implementada

```text
Automa-es-do-Notion (hub)
├── documentação, roteamento e bootstrap
├── notion-starter
│   └── biblioteca base + serviços compartilhados
├── notion-tasks-cli
│   └── borda CLI publicada como notion-automacoes
└── notion-workspace-app
    └── API Django + SPA React + MCP + launcher
```

O `notion-starter` é a base de domínio. CLI e app são consumidores com bordas
finas: adaptam entrada/saída, mas não duplicam a regra de negócio. O frontend
continua dentro do app porque API, SPA, MCP e launcher formam um único produto
local e são empacotados juntos quando a opção `app` é instalada.

## Responsabilidade de cada repositório

| Repositório | Pacote público | Responsabilidade | Fonte |
| --- | --- | --- | --- |
| [`notion-starter`](https://github.com/Felipe-Alcantara/notion-starter) | `notion-starter==0.3.0` | `NotionClient`, schema, propriedades, conteúdo, tarefas, inventário, adaptadores e services compartilhados | [PyPI](https://pypi.org/project/notion-starter/) |
| [`notion-tasks-cli`](https://github.com/Felipe-Alcantara/notion-tasks-cli) | `notion-automacoes==0.3.0` | comandos de terminal, perfis, saída JSON, fachada `tasks`/`auth`, `doctor`, `app` e `mcp` | [PyPI](https://pypi.org/project/notion-automacoes/) |
| [`notion-workspace-app`](https://github.com/Felipe-Alcantara/notion-workspace-app) | `notion-workspace-app==0.3.0` | API REST Django, SPA React, servidor MCP, operações SQLite e launcher `start_app.py` | [PyPI](https://pypi.org/project/notion-workspace-app/) |
| `Automa-es-do-Notion` | — | bootstrap, sincronização, roteamento de agentes e documentação integrada | [GitHub](https://github.com/Felipe-Alcantara/Automa-es-do-Notion) |

## Dependências e fronteiras

```text
notion-automacoes ──────┐
                         ├── notion-starter (faixa >=0.3.0,<0.4.0)
notion-workspace-app ───┘
```

- Só `NotionClient` fala diretamente com a API do Notion.
- `notion_starter.services` concentra casos de uso compartilhados.
- A CLI mantém parsing, saída humana/JSON e compatibilidade do comando
  `notion-tasks`.
- O app mantém a borda REST, a borda MCP, o launcher e a SPA; seus services
  comuns são shims para o starter.
- O hub não recebe funcionalidade de produto. Mudanças de código vão para o
  módulo responsável e são testadas no próprio repositório.

## Distribuição

A fachada única é instalada com:

```bash
pipx install "notion-automacoes[app]"
```

O pacote base instala somente a CLI e o núcleo. O extra `app` acrescenta Django,
MCP e o app local; a SPA já vem compilada no wheel, portanto Node/npm só são
necessários para desenvolvimento. O alias `notion-tasks` permanece disponível
para compatibilidade.

Cada repositório possui seu próprio workflow de release. A release `v0.3.0`
constrói wheel e sdist, valida metadados com `twine check`, executa smoke em
Ubuntu, Windows e macOS com Python 3.10 e 3.13 e publica por Trusted Publishing.
O contrato completo está em [`DISTRIBUICAO.md`](DISTRIBUICAO.md).

## Desenvolvimento no workspace

O hub evita duplicar clones e expõe `modules/` como caminho canônico de trabalho:

```bash
python bootstrap.py
python check-dev.py
```

O `bootstrap.py` atualiza clones existentes ou cria links para clones encontrados
na pasta vizinha. Depois:

1. leia [`AGENTS.md`](../AGENTS.md) e o `AGENTS.md` do módulo;
2. edite somente o repositório responsável;
3. rode o gate do módulo;
4. atualize README/IA quando a mudança afetar comportamento, comandos ou arquitetura;
5. faça commit e push no módulo, nunca no hub para mudanças de código.

## Gatilhos de manutenção

| Mudança | Repositório correto |
| --- | --- |
| retry, rate limit, schema, conteúdo, tarefas ou service compartilhado | `notion-starter` |
| comando, parser, envelope JSON, perfis ou compatibilidade `notion-tasks` | `notion-tasks-cli` |
| rota REST, MCP, launcher, operação SQLite ou SPA | `notion-workspace-app` |
| roteamento, bootstrap, contratos entre módulos ou documentação transversal | hub |

Se a mudança atravessar a fronteira entre módulos, documente o contrato no hub e
atualize os consumidores afetados. Não copie uma implementação compartilhada para
resolver um problema local.

## Gates de qualidade

Cada módulo é autônomo:

```bash
# notion-starter ou notion-tasks-cli
python -m ruff check .
python -m pytest

# além disso, no notion-workspace-app
cd front
npm ci
npm run lint
npm run build
```

Os testes usam mocks e não exigem credenciais reais. O hub valida o workspace com
`python3 -m pytest` e `python3 check-dev.py`. O checklist completo está em
[`QUALIDADE.md`](QUALIDADE.md).

## O que permanece aberto

A arquitetura atual está entregue; futuras mudanças são contribuições isoladas,
por exemplo:

- paginação e novas operações de escrita na exploração;
- novas visualizações para a SPA;
- suporte a binários nativos, somente após definir assinatura, atualização,
  rollback e manutenção;
- novos adaptadores e fontes de ingestão no starter.

Esses itens não alteram a divisão atual nem são pré-requisitos para usar a
release publicada.
