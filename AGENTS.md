# AGENTS.md — Roteiro Operacional

Este arquivo orienta agentes de IA e mantenedores que trabalham neste repositório.
Ele complementa o `IA.md`; não substitui a leitura do código.

## Leitura Inicial

Antes de alterar código:

- Leia [`README.md`](README.md) para entender a superfície pública.
- Leia [`docs/QUALIDADE.md`](docs/QUALIDADE.md) para saber o gate obrigatório.
- Leia [`IA.md`](IA.md) para contexto operacional, decisões e riscos conhecidos.
- Se a pasta local `Padrão de qualidade - Felixo System Design/` existir, leia o
  `AGENTS.md` dela e o `core/GUIA_MINIMO_QUALIDADE.md` antes de atualizar padrões.
- Para mudanças de API/serviços, leia [`docs/CONTRATOS.md`](docs/CONTRATOS.md).
- Para MCP, leia [`docs/MCP.md`](docs/MCP.md).
- Para front, leia [`front/README.md`](front/README.md).

## Regras de Trabalho

- Preserve as fronteiras: `api/` valida HTTP, `services/` orquestra casos de uso,
  `integrations/` encapsula provedores externos e `notion_starter` mantém o core.
- Não chame APIs reais em testes. Use doubles, mocks ou `responses`.
- Não versione `.env`, tokens, IDs reais, `mapa.json`, `mapa.html`, SQLite local ou
  builds gerados.
- Prefira estender comandos/scripts existentes antes de criar fluxo manual novo. Se a
  edição manual for mais pragmática, registre o motivo no fechamento ou no `IA.md`.
- Atualize documentação viva no mesmo passo quando mudar contrato, comando ou UX.
- Preserve o `IA.md` como linha do tempo: não apague decisões antigas quando uma
  decisão mudar; adicione uma nova entrada datada com contexto, motivo e validação.
- Trabalhe direto no `main` por padrão. Crie branch só para feature grande,
  refatoração significativa ou alto risco, conforme o guia de git.

## Gate Obrigatório

Antes de entregar, rode:

```bash
python3 scripts/quality_check.py
```

Se precisar isolar:

```bash
python3 scripts/quality_check.py --python-only
python3 scripts/quality_check.py --front-only
```

Registre no fechamento quais checks foram executados e qualquer risco residual.
