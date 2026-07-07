# ✅ Qualidade

Este documento é o contrato de qualidade **deste repositório hub**. Ele traduz o
Felixo System Design (`Padrão de qualidade - Felixo System Design/`, ignorado pelo
Git) para os checks reais do hub, sem depender de memória de conversa.

> **O hub não hospeda funcionalidade.** Aqui vivem documentação, roteamento
> (`AGENTS.md`) e os scripts de workspace (`bootstrap.py`, `check-dev.py`,
> `sync.py`, `start_app.py`). O código das ferramentas — e o gate de testes/lint
> dele — mora em cada módulo (`notion-starter`, `notion-tasks-cli`,
> `notion-workspace-app`), com o próprio `QUALIDADE`/`pytest` de cada repo. Veja o
> mapa de roteamento no [`AGENTS.md`](../AGENTS.md).

## Gate Local (hub)

Antes de encerrar uma mudança no hub, rode a porta de entrada e a verificação:

```bash
python start_app.py     # menu: Instalar/Setup, Configurar, Status, Usar, Desenvolver
python check-dev.py     # valida Python, módulos clonados, .env e deps
```

- `start_app.py` é o menu interativo obrigatório (contrato Felixo): instala a CLI,
  sincroniza os módulos, configura o `.env` e opera o Notion — sem decorar comando.
- `check-dev.py` confere o ambiente de desenvolvimento (Python 3.10+, `modules/`
  clonado, `.env`, `pytest`/`requests`).
- `sync.py` roda `bootstrap.py` + `check-dev.py` em sequência para atualizar tudo.

Nenhum check do hub exige token real do Notion, GitHub ou OpenRouter.

## Gate por módulo

Ao **desenvolver** (editar código de uma ferramenta), o gate é o do módulo, dentro
de `modules/<nome>/`:

```bash
cd modules/<nome>
python -m pytest
```

Aplique a correção nos dois repositórios quando mexer na camada duplicada
(`core/`, `integrations/`, `services/` existem em `notion-tasks-cli` e em
`notion-workspace-app/server/` — ver "Dívida conhecida" no `AGENTS.md`).

## Critério de Pronto

Uma mudança só está pronta quando:

- O gate aplicável passou: `check-dev.py` para mudanças no hub; `pytest` do módulo
  para mudanças de código — ou a impossibilidade foi registrada com motivo objetivo.
- Comportamento novo ou bug corrigido tem teste quando aplicável (no módulo).
- Documentação viva foi atualizada quando comandos, contratos, arquitetura, UX ou
  o **roteamento** mudam (`README.md`, `AGENTS.md`, `docs/`).
- O `IA.md` preserva o histórico: decisões novas entram como registros datados, sem
  apagar a linha de raciocínio anterior.
- Scripts e ferramentas reutilizáveis foram priorizados antes de edição manual;
  exceções foram registradas objetivamente.
- Segredos, IDs reais e artefatos locais continuam fora do Git.
- As fronteiras de camada seguem intactas: bordas (CLI/API/MCP) não têm regra de
  negócio; `services/` não conhece HTTP; só o `NotionClient` fala com a API.

## Git

- Trabalhe direto no `main` por padrão.
- Crie branch apenas para feature grande, refatoração significativa ou alto risco.
- Faça commits pequenos e coesos no formato `tipo: descricao` (`feat`/`fix`/`docs`/
  `refactor`/`chore`).
- Atualize a documentação viva no mesmo commit da mudança.
- Commits e push de código vão **no repositório do módulo**, não no hub.

## Referências

- [`AGENTS.md`](../AGENTS.md) — roteiro operacional para agentes e mantenedores.
- [`IA.md`](../IA.md) — memória técnica e decisões do projeto.
- `Padrão de qualidade - Felixo System Design/` — referência local ignorada pelo Git.
