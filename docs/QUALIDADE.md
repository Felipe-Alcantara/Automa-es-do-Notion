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

## Gate local do hub

Antes de encerrar uma mudança no hub, rode somente os testes próprios do hub e a
verificação do workspace:

```bash
python3 -m pytest tests  # evita coletar as suítes dos módulos em modules/
python3 check-dev.py    # valida Python, módulos clonados, .env e deps
```

- `start_app.py` é o menu interativo de entrada: instala a CLI de desenvolvimento,
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
python -m ruff check .
python -m pytest
```

No `notion-workspace-app`, acrescente:

```bash
cd front
npm ci
npm run lint
npm run build
```

Aplique a correção nos dois consumidores quando mexer na camada duplicada
(`core/`, `integrations/`, `services/` existem em `notion-tasks-cli` e em
`notion-workspace-app/server/` — ver "Dívida conhecida" no `AGENTS.md`).

## Critério de Pronto

Uma mudança só está pronta quando:

- O gate aplicável passou: `pytest` do hub e `check-dev.py` para mudanças no hub;
  `ruff` + `pytest` do módulo e, no app, lint/build do front — ou a
  impossibilidade foi registrada com motivo objetivo.
- Comportamento novo ou bug corrigido tem teste quando aplicável (no módulo).
- Documentação viva foi atualizada quando comandos, contratos, arquitetura, UX ou
  o **roteamento** mudam (`README.md`, `AGENTS.md`, `docs/`).
- O `IA.md` preserva o histórico: decisões novas entram como registros datados, sem
  apagar a linha de raciocínio anterior.
- Scripts e ferramentas reutilizáveis foram priorizados antes de edição manual;
  exceções foram registradas objetivamente.
- Documentação pública não promete estado futuro já resolvido: instalação,
  versão, links, entry points e limitações conferem com o pacote publicado.
- Links relativos apontam para arquivos existentes; referências a outro módulo
  usam o repositório correspondente, nunca um caminho fantasma do antigo monorepo.
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
- [Guia de distribuição](DISTRIBUICAO.md) — contrato público e evidências da release `0.3.0`.
