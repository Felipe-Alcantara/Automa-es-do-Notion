# 🤖 AGENTES — Playbook de orquestração multi-agente

> **O que é**: o guia que o **orquestrador do [Felixo-AI-Core](https://github.com/Felipe-Alcantara/Felixo-AI-Core)**
> e cada **sub-agente** seguem para construir este projeto em paralelo. Define os papéis,
> o que cada agente lê, o que entrega, em que ordem e como os agentes evitam pisar uns
> nos outros.
>
> **Para o orquestrador**: este arquivo é o seu plano. Use-o para emitir `spawn_agent`
> com o prompt certo para cada papel, respeitando a ordem de dependências e os limites de
> segurança abaixo.
>
> **Para cada sub-agente**: você recebe um prompt que aponta para a sua seção aqui.
> **Leia primeiro [docs/README.md](README.md) e [docs/PLANO.md](PLANO.md)** para ter a
> visão do todo, depois a seção do seu papel.

---

> **Estado [2026-06-26]:** o **Ciclo 1** (Agentes 0–7 abaixo) está **concluído** — a base
> existe (cliente, robustez, API + front mínimo, ingestão, GitHub, IA, MCP). O trabalho
> ativo agora é o **[Ciclo 2](#-ciclo-2--agentes-do-front-rico-cli-e-multi-tabela)** (front
> React, CLI para IA, multi-tabela), no fim deste arquivo. As seções dos Agentes 0–7
> ficam como **referência histórica** do que cada papel entregou.

## 🔢 Resumo para configurar o canvas

**Total: 8 agentes** (8 nós de terminal no canvas). Cada um lê todo `docs/` via skills.
A CLI/modelo de cada agente você escolhe na hora de configurar o canvas.

| # | Agente | Onda |
|---|---|---|
| 0 | Contratos & Fundação | 1 (sozinho) |
| 1 | Infra | 2 |
| 2 | Backend | 2 |
| 3 | IA / OpenRouter | 2 |
| 4 | Front-end | 3 |
| 5 | Integrações (GitHub & Ingestão) | 3 |
| 6 | MCP (ponte com Felixo-AI-Core) | 4 |
| 7 | Otimização & Qualidade | 3 e 4 (transversal) |

> O **Agente 0 roda sozinho primeiro**; depois até **3 por onda** (limite do orquestrador).
> Por nó: terminal + scratchpad próprio + skills (`AGENTES.md` + `README.md` + o doc do
> papel) + ligação ao scratchpad compartilhado. Detalhes em
> [No canvas do Felixo-AI-Core](#no-canvas-do-felixo-ai-core).

---

## 📋 Índice

- [🧭 Como usar este playbook](#-como-usar-este-playbook)
- [📚 Leitura obrigatória (todos os agentes)](#-leitura-obrigatória-todos-os-agentes)
- [🗺️ Mapa de papéis e dependências](#️-mapa-de-papéis-e-dependências)
- [🤝 Regras de coordenação](#-regras-de-coordenação)
- [👷 Os agentes](#-os-agentes)
  - [Agente 0 — Contratos & Fundação](#agente-0--contratos--fundação)
  - [Agente Infra](#agente-infra)
  - [Agente Backend](#agente-backend)
  - [Agente Front-end](#agente-front-end)
  - [Agente IA / OpenRouter](#agente-ia--openrouter)
  - [Agente Integrações (GitHub & Ingestão)](#agente-integrações-github--ingestão)
  - [Agente MCP (ponte com o Felixo-AI-Core)](#agente-mcp-ponte-com-o-felixo-ai-core)
  - [Agente Otimização & Qualidade](#agente-otimização--qualidade)
- [🛡️ Limites de segurança do run](#️-limites-de-segurança-do-run)
- [🚦 Ondas de execução sugeridas](#-ondas-de-execução-sugeridas)

---

## 🧭 Como usar este playbook

O Felixo-AI-Core orquestra por **App-Owned Orchestration**: o orquestrador emite eventos
`spawn_agent` (cada um com `agentId`, `cliType` e um `prompt` completo); o app cria cada
sub-agente como sessão nativa, coleta resultados e re-invoca o orquestrador. Os
sub-agentes são **stateless** — todo o contexto que precisam vem no prompt.

Por isso, o prompt de cada `spawn_agent` deve:

1. apontar para **este arquivo** e para a **seção do papel** correspondente;
2. mandar **ler a leitura obrigatória** antes de agir;
3. declarar o **escopo de arquivos** que aquele agente pode tocar (ver a seção do papel);
4. lembrar das **regras de coordenação** e dos **guarda-corpos** do projeto.

> Modelo de prompt pronto está no fim de cada seção de agente, em **"Prompt sugerido"**.

### No canvas do Felixo-AI-Core

Se você está montando isto no **canvas** (grafo de nós) do Felixo-AI-Core, os papéis
abaixo mapeiam direto nos primitivos do canvas:

- **Nó de terminal = um agente.** Crie um nó de terminal por papel (Backend, Front, IA…).
  O `initialText` (instrução padrão digitada ao subir) é o **"Prompt sugerido"** da seção
  daquele papel.
- **Nó de arquivo (file node) = documento que o agente lê.** Use o modo:
  - **scratchpad** — um log vivo do papel (objetivo, estado, bloqueios, próximo passo)
    que o agente mantém atualizado em loop;
  - **plan** — peça a um terminal conectado para escrever um diagnóstico do repositório
    no arquivo.
- **Skill = ponteiro para um arquivo que o agente deve ler/aplicar.** Anexe **este
  `AGENTES.md`** e o [docs/README.md](README.md) como skills de **todos** os agentes, para
  cada um ter a visão do todo. Anexe o doc específico do papel (ex.: `OTIMIZACAO.md` para o
  agente de Otimização) como skill só dele.
- **Aresta (edge) = conexão.** Ligar um file node a um agente avisa aquele agente sobre o
  arquivo. Dê a cada agente **um scratchpad próprio** ligado a ele, e ligue todos a um
  **scratchpad compartilhado do run** (estado geral), para coordenarem sem colidir.

> Resumo: 1 papel = 1 nó de terminal + 1 scratchpad próprio + skills (`AGENTES.md` +
> `README.md` + o doc do papel) + ligação ao scratchpad compartilhado.

---

## 📚 Leitura obrigatória (todos os agentes)

Antes de qualquer código, **todo** sub-agente lê, nesta ordem:

1. [docs/README.md](README.md) — o índice; entende quais documentos existem e o papel de
   cada um.
2. [docs/PLANO.md](PLANO.md) — a visão final, a arquitetura-alvo e as 6 fases.
3. A **seção do seu papel** neste arquivo.
4. O documento de `docs/` mais ligado ao seu papel (indicado em cada seção).
5. O `IA.md` e o `README.md` da raiz, para o estado real atual do código.
6. O **guia de Git do padrão de qualidade** —
   [`docs/GIT-POLITICA-DE-VERSIONAMENTO.md` do Felixo-System-Design](https://github.com/Felipe-Alcantara/Felixo-System-Design/blob/main/docs/GIT-POLITICA-DE-VERSIONAMENTO.md):
   **todo agente segue essa política ao versionar** (quando criar branch, formato dos
   commits, doc viva no mesmo commit, sem segredos, apagar branches mescladas).

E respeita os **guarda-corpos do projeto** (resumidos em [PLANO.md](PLANO.md) →
*Princípios e guarda-corpos*): módulos coesos, integrações isoladas, contratos estáveis,
segredos fora do repositório, testes para comportamento crítico (HTTP mockado),
`start_app.py` como porta única, documentação viva, Conventional Commits, entregas
pequenas e rastreáveis.

---

## 🗺️ Mapa de papéis e dependências

```text
                    ┌────────────────────────────┐
                    │ Agente 0 — Contratos &      │  (primeiro, sozinho)
                    │ Fundação                    │
                    └─────────────┬──────────────┘
                                  │ define os contratos que os outros consomem
        ┌───────────────┬────────┼────────┬───────────────┐
        ▼               ▼        ▼        ▼               ▼
   ┌─────────┐    ┌─────────┐ ┌───────┐ ┌──────────┐ ┌──────────────┐
   │ Infra   │    │ Backend │ │  IA   │ │Integrações│ │  Front-end   │
   └────┬────┘    └────┬────┘ └───┬───┘ └────┬─────┘ └──────┬───────┘
        │              │          │          │              │
        └──────────────┴────┬─────┴──────────┘              │
                            ▼                               │
                     ┌─────────────┐                        │
                     │ Agente MCP  │◄───────────────────────┘
                     └──────┬──────┘
                            ▼
                ┌────────────────────────┐
                │ Otimização & Qualidade │  (último, transversal)
                └────────────────────────┘
```

- **Agente 0 vai sozinho primeiro**: ele fixa os contratos (objetos de domínio, formato
  das rotas, fronteiras de camada). Sem isso, os outros divergem.
- **Backend, IA, Integrações, Infra e Front podem rodar em paralelo** depois do Agente 0,
  cada um no seu escopo de arquivos.
- **MCP** depende do Backend (ele expõe via MCP o que o Backend implementa).
- **Otimização & Qualidade** é transversal e fecha cada onda.

---

## 🤝 Regras de coordenação

Para vários agentes trabalharem ao mesmo tempo sem se atrapalhar:

1. **Cada agente tem um escopo de arquivos próprio** (declarado na sua seção). Não edite
   arquivos fora do seu escopo; se precisar de algo de outro escopo, peça via contrato
   (Agente 0) em vez de mexer direto.
2. **Contratos antes de implementação**: nenhum agente inventa o formato de um objeto/rota
   que outro consome. Isso é trabalho do Agente 0; os demais seguem o que ele fixou.
3. **A fronteira de camadas é sagrada** (padrão do projeto): API não tem regra de negócio;
   regra de negócio não conhece HTTP; integração externa fica isolada. Ver
   [PLANO.md](PLANO.md) → arquitetura-alvo.
4. **Reusar o que já existe** antes de criar: o pacote `notion_starter` (cliente, helpers,
   schema, inventário, `TaskList`) é a base. Não reescreva o que já está pronto e testado.
5. **Commits pequenos por agente**, seguindo o
   [guia de Git do padrão de qualidade](https://github.com/Felipe-Alcantara/Felixo-System-Design/blob/main/docs/GIT-POLITICA-DE-VERSIONAMENTO.md):
   Conventional Commits (`tipo: descrição` no imperativo, dizendo o **quê** e o **porquê**),
   documentação viva atualizada no mesmo commit, commit direto no `main` por padrão
   (branch só para feature grande, refatoração ampla ou alto risco — e apagada após o merge).
   Um agente = uma unidade coesa por vez.
6. **Sem segredos**: token via variável de ambiente / `.env` ignorado pelo git; nada de
   IDs, caminhos locais ou chaves hardcoded — nem no código, nem em log, nem em commit.
7. **Testes com HTTP mockado** (`responses`), sem token nem rede real.

---

## 👷 Os agentes

Cada seção é o briefing de um papel. A CLI/modelo de cada agente fica a seu critério na
hora de montar o canvas — o orquestrador também pode ajustar conforme custo/contexto.

---

### Agente 0 — Contratos & Fundação

- **Objetivo**: fixar os contratos que todos os outros consomem, para que o trabalho
  paralelo convirja. É o **primeiro** e roda **sozinho**.
- **Lê também**: [PLANO.md](PLANO.md) (Fases 0 e 2) e [PORTABILIDADE.md](PORTABILIDADE.md).
- **Entrega**:
  - Objetos de domínio simples e estáveis (ex.: o contrato de `Tarefa` já existe em
    `tasks.py`; padronizar o que faltar — ex.: objeto de projeto/repo).
  - O **contrato das rotas REST** (caminhos, formato de request/response, erros) que o
    Backend implementa e o Front consome — esboço em [PLANO.md](PLANO.md), Fase 2.
  - A **estrutura de pastas-alvo** do servidor (`api/`, `services/`, `integrations/`,
    `core/`) registrada em `docs/` para os demais seguirem.
  - Helpers de **leitura** de propriedade (Fase 0) — base barata que Integrações e Front
    vão precisar.
- **Escopo de arquivos**: `src/notion_starter/` (helpers de leitura), um doc novo de
  contratos em `docs/` se necessário, e esqueleto de pastas do servidor (vazias/com
  `__init__`).
- **Não faz**: implementação de rotas, front, IA — só o contorno.
- **Pronto quando**: os contratos estão escritos e os helpers de leitura têm teste.
- **Prompt sugerido**:
  > Você é o Agente 0 (Contratos & Fundação) do projeto Automa-es-do-Notion. Leia
  > `docs/README.md`, `docs/PLANO.md` e a seção "Agente 0" de `docs/AGENTES.md`. Sua
  > tarefa: fixar os contratos de domínio e de API que os outros agentes vão consumir, e
  > entregar os helpers de leitura de propriedade (Fase 0) com testes mockados. Respeite
  > os guarda-corpos e a fronteira de camadas. Não implemente rotas, front nem IA. Commit
  > pequeno em `tipo: descrição`, doc viva no mesmo passo.

---

### Agente Infra

- **Objetivo**: planejar e preparar a infraestrutura do servidor — como roda local e como
  é hospedado.
- **Lê também**: [ESCALA.md](ESCALA.md) e [SAAS.md](SAAS.md) (decisão de alcance:
  pessoal, porém hospedado) e [PLANO.md](PLANO.md) (stack: Django + SQLite).
- **Entrega**:
  - Esqueleto do projeto **Django** com a estrutura por camadas do Agente 0.
  - **SQLite** para estado operacional (jobs/locks), com migrações.
  - Configuração centralizada (variáveis de ambiente, sem segredo no repo).
  - Ação **"Subir servidor"** no `start_app.py`, mantendo o contrato do menu de entrada.
  - Notas de **deploy/hospedagem** registradas em `docs/` (sem fixar provedor à força).
- **Escopo de arquivos**: configuração do servidor, `start_app.py` (a nova ação),
  `pyproject.toml`/dependências de servidor, `docs/` (notas de infra).
- **Pronto quando**: o servidor sobe local, lê config do ambiente e o menu tem a ação.
- **Prompt sugerido**:
  > Você é o Agente Infra do projeto Automa-es-do-Notion. Leia `docs/README.md`,
  > `docs/PLANO.md`, `docs/ESCALA.md`, `docs/SAAS.md` e a seção "Agente Infra" de
  > `docs/AGENTES.md`. Stack fixada: Django + SQLite. Entregue o esqueleto do servidor
  > com a estrutura por camadas, SQLite para estado operacional, configuração por
  > variável de ambiente (sem segredo no repo) e a ação "Subir servidor" no
  > `start_app.py`. Siga os contratos do Agente 0. Commit pequeno, doc viva no mesmo passo.

---

### Agente Backend

- **Objetivo**: implementar os casos de uso e as rotas REST sobre a `TaskList`.
- **Lê também**: [PLANO.md](PLANO.md) (Fase 2) e [MODELOS-DE-USO.md](MODELOS-DE-USO.md).
- **Entrega**:
  - `services/tarefas.py`: `listar_tarefas`, `criar_tarefa`, `mover_status`,
    `concluir_tarefa` — finos sobre a `TaskList` já existente.
  - Rotas REST conforme o contrato do Agente 0
    (`GET /api/tarefas`, `POST /api/tarefas`, `PATCH /api/tarefas/{id}`).
  - Controllers/views **finos**: parse, validação, delegação — nada de regra de negócio.
  - Testes dos casos de uso com o Notion mockado.
- **Escopo de arquivos**: `api/` e `services/` do servidor; testes correspondentes.
- **Não faz**: front, infra, IA. Não toca no formato cru do Notion (isso é do
  `notion_starter`).
- **Pronto quando**: as rotas respondem o contrato e os casos de uso têm teste.
- **Prompt sugerido**:
  > Você é o Agente Backend do projeto Automa-es-do-Notion. Leia `docs/README.md`,
  > `docs/PLANO.md` (Fase 2) e a seção "Agente Backend" de `docs/AGENTES.md`. Implemente
  > os casos de uso de tarefas (finos sobre a `TaskList` existente) e as rotas REST do
  > contrato do Agente 0, com controllers finos e testes mockados. Não invente formato de
  > rota — siga o contrato. Commit pequeno, doc viva no mesmo passo.

---

### Agente Front-end

> **Histórico (Ciclo 1).** Este agente entregou o front mínimo em templates/JS vanilla
> servido pelo Django. O front atual é reescrito como SPA React no
> **[Agente B do Ciclo 2](#agente-b--front-react--tailwind--vite)** — veja lá para o
> trabalho ativo.

- **Objetivo**: o "momento aha" — uma interface web que **lista e edita as tarefas reais**.
- **Lê também**: [MODELOS-DE-USO.md](MODELOS-DE-USO.md) e [PLANO.md](PLANO.md) (Fase 2).
  Segue os padrões visuais do design system de front do projeto, quando aplicável.
- **Entrega**:
  - Tela que lista tarefas (com filtro por status) e permite criar / mover status /
    concluir, **consumindo as rotas REST** do Backend (contrato do Agente 0).
  - Estados claros de carregando / vazio / erro.
- **Escopo de arquivos**: templates/estáticos do front servidos pelo Django (ou a pasta
  de front definida pela Infra); nada de regra de negócio no front.
- **Não faz**: lógica de Notion, rotas de servidor. Consome a API, não a reimplementa.
- **Pronto quando**: dá para ver e editar tarefas no navegador, contra o Backend.
- **Prompt sugerido**:
  > Você é o Agente Front-end do projeto Automa-es-do-Notion. Leia `docs/README.md`,
  > `docs/MODELOS-DE-USO.md`, `docs/PLANO.md` (Fase 2) e a seção "Agente Front-end" de
  > `docs/AGENTES.md`. Construa a tela que lista e edita as tarefas reais, consumindo as
  > rotas REST do contrato do Agente 0 (não invente endpoints). Trate carregando/vazio/erro.
  > Sem regra de negócio no front. Commit pequeno, doc viva no mesmo passo.

---

### Agente IA / OpenRouter

- **Objetivo**: a camada de IA plugável — **OpenRouter (pague por uso) e assinaturas**
  (Codex, Claude Code Pro, Cursor; futuramente Gemini CLI e Copilot CLI).
- **Lê também**: [PLANO.md](PLANO.md) (Fase 5), [OTIMIZACAO.md](OTIMIZACAO.md) e
  [IDEIAS-EXTRAS.md](IDEIAS-EXTRAS.md) (seção de provedores). Espelha o projeto **Openia**.
- **Entrega**:
  - Interface `ProvedorIA` única, com implementações para OpenRouter e para modo
    assinatura (registro declarativo, Open/Closed).
  - Catálogo de modelos do OpenRouter (cache, ordenação por preço), espelhando os padrões
    do Openia. Chaves fora do repositório.
  - Primeiro caso de uso: **linguagem natural → operação de tasklist**, no modo
    **copiloto que sugere e a pessoa confirma**.
- **Escopo de arquivos**: `integrations/openrouter.py` e a camada de provedor; testes com
  o provedor mockado.
- **Não faz**: escrever direto no Notion sem confirmação; orquestrar agentes (isso é do
  Felixo-AI-Core).
- **Pronto quando**: um caso de uso funciona com provedor mockado e o modo
  confirmar-antes-de-escrever está garantido por teste.
- **Prompt sugerido**:
  > Você é o Agente IA do projeto Automa-es-do-Notion. Leia `docs/README.md`,
  > `docs/PLANO.md` (Fase 5), `docs/OTIMIZACAO.md` e a seção "Agente IA / OpenRouter" de
  > `docs/AGENTES.md`. Construa a camada de IA plugável (OpenRouter + assinaturas),
  > espelhando o projeto Openia, com chaves fora do repo. Entregue um caso de uso
  > linguagem-natural → tasklist no modo copiloto (sugere, a pessoa confirma), com testes
  > mockados. Commit pequeno, doc viva no mesmo passo.

---

### Agente Integrações (GitHub & Ingestão)

- **Objetivo**: trazer dados de fora para o Notion — repositórios do GitHub e arquivos
  locais.
- **Lê também**: [PLANO.md](PLANO.md) (Fases 3 e 4) e [PORTABILIDADE.md](PORTABILIDADE.md)
  (fonte como ponto de extensão).
- **Entrega**:
  - `integrations/github.py`: `listar_repos`, `detalhar_repo`, seguindo o padrão de
    cliente resiliente (token, retry/backoff, rate limit).
  - `services/sincronizar_github.py`: cada repo → uma página no Notion + um tópico no
    todolist.
  - `services/ingestao.py`: varre uma pasta local e cria/atualiza páginas; **tipo de
    fonte como estratégia** (`FonteArquivos`, `FonteGitHub`).
- **Escopo de arquivos**: `integrations/` (github) e `services/` de ingestão/sincronização;
  testes mockados.
- **Reusa**: os helpers de leitura do Agente 0 e os helpers de propriedade existentes.
- **Pronto quando**: um repo de exemplo vira página + tarefa, e uma pasta de exemplo é
  ingerida, com o mapeamento testado.
- **Prompt sugerido**:
  > Você é o Agente Integrações do projeto Automa-es-do-Notion. Leia `docs/README.md`,
  > `docs/PLANO.md` (Fases 3 e 4), `docs/PORTABILIDADE.md` e a seção "Agente Integrações"
  > de `docs/AGENTES.md`. Implemente o conector GitHub (cliente resiliente) e a ingestão
  > de arquivos locais, com o tipo de fonte como ponto de extensão. Mapeie repo → página +
  > tarefa. Reuse os helpers existentes. Testes mockados. Commit pequeno, doc viva.

---

### Agente MCP (ponte com o Felixo-AI-Core)

- **Objetivo**: expor as capacidades deste projeto como **ferramentas MCP** que os agentes
  do Felixo-AI-Core consomem.
- **Lê também**: [PLANO.md](PLANO.md) (Fase 6) e o catálogo MCP do Felixo-AI-Core
  (`app/electron/services/mcp/felixo-tool-catalog.cjs`).
- **Entrega**:
  - Uma camada de ferramentas `notion`: `notion.list_tasks` (read),
    `notion.create_task` (write+confirm), `notion.move_status` (write+confirm),
    `notion.update_project_page` (write+confirm), respeitando `access` e
    `requiresConfirmation` do catálogo.
  - Cada ferramenta é um invólucro fino sobre os **casos de uso do Backend** — não
    reimplementa regra.
- **Escopo de arquivos**: a camada MCP/servidor deste projeto; integração documentada em
  `docs/`. (A edição do catálogo no repositório do Felixo-AI-Core é coordenada à parte.)
- **Depende de**: Backend (os casos de uso que as ferramentas chamam).
- **Pronto quando**: as ferramentas `notion` respondem pelo seam MCP e escritas pedem
  confirmação.
- **Prompt sugerido**:
  > Você é o Agente MCP do projeto Automa-es-do-Notion. Leia `docs/README.md`,
  > `docs/PLANO.md` (Fase 6) e a seção "Agente MCP" de `docs/AGENTES.md`. Exponha as
  > capacidades de Notion como ferramentas MCP (`notion.*`), invólucros finos sobre os
  > casos de uso do Backend, respeitando read/write e requiresConfirmation. Não
  > reimplemente regra de negócio. Commit pequeno, doc viva no mesmo passo.

---

### Agente Otimização & Qualidade

- **Objetivo**: papel **transversal** — fecha cada onda garantindo desempenho, custo e
  qualidade.
- **Lê também**: [OTIMIZACAO.md](OTIMIZACAO.md) e o guia mínimo de qualidade do padrão.
- **Entrega**:
  - Robustez do cliente Notion (retry/backoff, rate limit, idempotência — Fase 1).
  - Cache em camadas onde fizer sentido (schema, catálogo de modelos, listas).
  - Revisão de fronteiras de camada e de cobertura de testes do que foi entregue na onda.
  - Verifica os guarda-corpos: segredos fora do repo, docs vivas, contratos preservados.
- **Escopo de arquivos**: transversal, mas **preferencialmente em PRs/commits próprios**
  de melhoria, sem reabrir o escopo de outro agente sem necessidade.
- **Pronto quando**: a onda passa nos testes, sem regressão, e os guarda-corpos estão de pé.
- **Prompt sugerido**:
  > Você é o Agente Otimização & Qualidade do projeto Automa-es-do-Notion. Leia
  > `docs/README.md`, `docs/OTIMIZACAO.md` e a seção "Agente Otimização & Qualidade" de
  > `docs/AGENTES.md`. Meça antes de otimizar; foque no passo dominante (Notion e IA).
  > Adicione retry/backoff e idempotência ao cliente, cache onde compensar, e revise
  > fronteiras e testes da onda. Não reabra o escopo de outro agente sem necessidade.
  > Commit pequeno, doc viva no mesmo passo.

---

## 🛡️ Limites de segurança do run

Alinhados com os limites de orquestração do Felixo-AI-Core, para o orquestrador não criar
agentes sem fim:

```json
{
  "maxAgentsPerTurn": 3,
  "maxTotalAgents": 10,
  "maxTurns": 5,
  "maxRuntimeMinutes": 20
}
```

Como **no máximo 3 agentes por turno**, agrupe os papéis em ondas (abaixo) em vez de
disparar todos de uma vez.

---

## 🚦 Ondas de execução sugeridas

Uma forma de respeitar as dependências e o limite de 3 por turno:

```text
Onda 1 (sozinho)   →  Agente 0 — Contratos & Fundação
Onda 2 (até 3)     →  Infra · Backend · IA          (paralelo, escopos distintos)
Onda 3 (até 3)     →  Front-end · Integrações · Otimização & Qualidade
Onda 4 (até 2)     →  MCP · Otimização & Qualidade  (fecha o ciclo)
```

A cada onda, o orquestrador coleta os resultados, re-injeta no contexto e decide a
próxima — exatamente o loop App-Owned do Felixo-AI-Core. Entre ondas, vale rodar o
**Agente Otimização & Qualidade** para não acumular dívida.

---

## 🔄 Ciclo 2 — agentes do front rico, CLI e multi-tabela

> Estes são os agentes **ativos**. Diferente do Ciclo 1, eles **não têm ondas com
> dependências bloqueantes**: cada um toca uma **pasta distinta** e lê o mesmo contrato já
> fixado em [CONTRATOS.md](CONTRATOS.md) — então andam em paralelo sem parar um para fazer
> o outro. O **núcleo** (`src/notion_starter/`) é leitura comum; quem precisar estendê-lo
> faz pela Frente A (núcleo) para os demais não brigarem pelo mesmo arquivo.
>
> Visão geral das frentes em [PLANO.md](PLANO.md) → *Ciclo 2*. Todos seguem o **padrão de
> qualidade** (documentação viva no mesmo commit, Conventional Commits, segredos fora do
> repo, testes com HTTP mockado, linguagem open source) e as **regras de coordenação**
> acima.

| Agente | Pasta (escopo) | Lê também |
|---|---|---|
| A — Núcleo & API v2 | `src/notion_starter/`, `server/api/`, `server/services/` | [CONTRATOS.md](CONTRATOS.md) §1–2 |
| B — Front React | `front/` (SPA nova) | design system de front do padrão de qualidade |
| C — CLI para IA | `cli/` | [MODELOS-DE-USO.md](MODELOS-DE-USO.md), [MCP.md](MCP.md) |
| D — Qualidade | transversal (commits próprios) | guia mínimo de qualidade |

> Por que A pode andar com B/C: o **contrato já está escrito** (campos `duracao`/`areas`,
> `GET /api/opcoes`, `PATCH` amplo). B e C programam contra esse contrato; se A ainda não
> entregou a API, B mocka as respostas e C injeta uma `TaskList` de teste — ninguém fica
> parado. A integração final é só apontar para a API real.

### Agente A — Núcleo & API v2 (colunas reais + multi-tabela)

- **Objetivo**: mapear as colunas que se usam de verdade e abrir a edição ampla.
- **Entrega**:
  - Núcleo: `properties.relation(ids)` (writer que faltava); `Tarefa`/`CamposTarefa` com
    `duracao` e `areas`; `tarefa_de_pagina` lê os novos campos; `TaskList` resolve nomes de
    áreas (cache em memória), aceita `duracao`/`areas` em criar/editar e expõe as opções.
  - API: `PATCH /api/tarefas/{id}` vira edição ampla (retrocompat com `{status}`);
    `POST` aceita `duracao`/`areas`; nova rota `GET /api/opcoes`; serializer com os campos
    novos. Tudo conforme [CONTRATOS.md](CONTRATOS.md) §1–2.
- **Escopo de arquivos**: `src/notion_starter/{properties,tasks}.py`, `server/api/`,
  `server/services/tarefas.py` + testes correspondentes.
- **Reusa**: `readers.ler_relation`/`ler_status`, o padrão de `extrair_perfil_database`.
- **Pronto quando**: contrato v2 implementado, suíte verde (HTTP mockado), `ruff` limpo.
- **Prompt sugerido**:
  > Você é o Agente A (Núcleo & API v2) do projeto Automa-es-do-Notion. Leia `docs/README.md`,
  > `docs/CONTRATOS.md` (§1–2) e a seção "Agente A" de `docs/AGENTES.md`. Implemente os
  > campos `duracao`/`areas` em `Tarefa`/`CamposTarefa`, o writer `properties.relation`, a
  > edição ampla no `PATCH` e a rota `GET /api/opcoes`, com testes mockados. Não invente
  > formato — siga o contrato. Commit pequeno, doc viva no mesmo passo.

### Agente B — Front React + Tailwind + Vite

- **Objetivo**: a SPA rica que lista/edita tarefas com várias visualizações e filtros.
- **Entrega**:
  - App React (Vite) em `front/`, seguindo o **design system de front do padrão de
    qualidade** (paleta/tipografia adaptáveis por projeto).
  - Visualizações **grade / lista / kanban** (por status), **busca**, **filtros
    persistentes** (status, duração, área) e ordenação — estado de filtro/visão guardado
    localmente. Modais de criar/editar consumindo `POST`/`PATCH` e `GET /api/opcoes`.
  - Estados de carregando / vazio / erro; acessibilidade (foco, aria).
- **Escopo de arquivos**: `front/` (novo). Consome a API REST — **sem regra de negócio**.
- **Pronto quando**: dá para ver/filtrar/editar tarefas reais no navegador, contra a API
  (ou mock enquanto a Frente A não fecha).
- **Prompt sugerido**:
  > Você é o Agente B (Front React) do projeto Automa-es-do-Notion. Leia `docs/README.md`,
  > `docs/CONTRATOS.md` (§2) e a seção "Agente B" de `docs/AGENTES.md`, além do design
  > system de front do padrão de qualidade. Construa a SPA React+Tailwind+Vite em `front/`
  > com grade/lista/kanban, busca e filtros persistentes, consumindo a API REST. Sem regra
  > de negócio no front. Commit pequeno, doc viva no mesmo passo.

### Agente C — CLI completa para IA

- **Objetivo**: uma CLI com todas as operações de tasklist, fina sobre os `services`.
- **Entrega**:
  - CLI em `cli/` cobrindo: listar (com filtros), ler uma tarefa, criar, editar, mover,
    concluir, mapear workspace, escolher/trocar database. Saída legível e também
    **estruturada (JSON)** para uma IA consumir.
  - **Borda fina**: cada comando chama `server/services/...` — não reimplementa regra nem
    fala direto com o Notion. Documentar a relação **CLI ↔ MCP** (duas cascas dos mesmos
    services) em [MCP.md](MCP.md)/[MODELOS-DE-USO.md](MODELOS-DE-USO.md).
- **Escopo de arquivos**: `cli/` (novo) + testes; pode ganhar uma ação no `start_app.py`.
- **Pronto quando**: todas as operações disponíveis por linha de comando, com testes
  (services injetados/mockados) e saída JSON estável.
- **Prompt sugerido**:
  > Você é o Agente C (CLI para IA) do projeto Automa-es-do-Notion. Leia `docs/README.md`,
  > `docs/MODELOS-DE-USO.md`, `docs/MCP.md` e a seção "Agente C" de `docs/AGENTES.md`.
  > Construa uma CLI em `cli/` com todas as operações de tasklist como borda fina sobre os
  > `services` (sem reimplementar regra), com saída JSON para IA e testes mockados. Commit
  > pequeno, doc viva no mesmo passo.

### Agente D — Qualidade (transversal)

- **Objetivo**: fechar o ciclo sem dívida — testes, fronteiras, desempenho e guarda-corpos.
- **Entrega**: revisão de cobertura e de fronteiras de camada das três frentes; cache onde
  compensar; checagem dos guarda-corpos (segredos fora do repo, docs vivas, contrato
  preservado, `ruff`/`format`/`manage.py check` limpos).
- **Escopo de arquivos**: transversal, **em commits próprios** de melhoria, sem reabrir o
  escopo de A/B/C sem necessidade.
- **Prompt sugerido**:
  > Você é o Agente D (Qualidade) do projeto Automa-es-do-Notion. Leia `docs/README.md`,
  > `docs/OTIMIZACAO.md` e a seção "Agente D" de `docs/AGENTES.md`. Revise cobertura,
  > fronteiras e guarda-corpos das frentes A/B/C; otimize só o que medir; mantenha a suíte
  > verde. Não reabra o escopo de outro agente sem necessidade. Commit pequeno, doc viva.

---

> Lembrete final para todos: o **Notion é a fonte da verdade do conteúdo**; este projeto
> é a camada de dados + front; o **Felixo-AI-Core é o cérebro**. Mantenha essa fronteira —
> é o que faz o trabalho de muitos agentes somar em vez de colidir.
