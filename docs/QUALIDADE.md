# ✅ Qualidade

Este documento é o contrato executável de qualidade deste repositório. Ele traduz o
Felixo System Design para os checks reais do projeto, sem depender de memória de
conversa ou comandos espalhados.

## Gate Local

Use o comando único antes de encerrar mudanças:

```bash
python3 scripts/quality_check.py
```

Se o seu ambiente tiver o alias `python` apontando para Python 3, ele também pode ser
usado. Neste repositório, `python3` é o comando portátil para Linux/macOS.

Ele roda:

- `ruff check .` para estilo, imports e problemas estáticos de Python.
- `pytest -q` para a suíte Python/Django/MCP/CLI com HTTP mockado.
- `npm run lint` em `front/` para lint da SPA React.
- `npm run build` em `front/` para validar o build Vite.

Para depuração pontual:

```bash
python3 scripts/quality_check.py --python-only
python3 scripts/quality_check.py --front-only
```

Pré-requisitos:

```bash
pip install -e ".[dev]"
cd front && npm install
```

## Gate de CI

O GitHub Actions valida duas frentes:

- Python 3.10, 3.11, 3.12 e 3.13: instala `.[dev]`, roda Ruff e Pytest.
- Front: instala dependências com `npm ci`, roda Oxlint e build Vite.

Nenhum check exige token real do Notion, OpenRouter ou GitHub. Integrações externas
devem continuar mockadas em teste.

## Critério de Pronto

Uma mudança só deve ser tratada como pronta quando:

- O comando `python3 scripts/quality_check.py` passa localmente, ou a impossibilidade
  de executar algum trecho foi registrada com motivo objetivo.
- Comportamento novo ou bug corrigido tem teste quando aplicável.
- Documentação viva foi atualizada quando comandos, contratos, arquitetura ou UX mudam.
- O `IA.md` preserva o histórico: decisões novas entram como registros datados, sem
  apagar a linha de raciocínio anterior.
- Scripts, comandos e ferramentas reutilizáveis foram priorizados antes de edição
  manual; exceções foram registradas objetivamente.
- Segredos, IDs reais e artefatos locais continuam fora do Git.
- A borda HTTP/UI/CLI/MCP continua fina, delegando regra de negócio para `services/`
  ou para o core `notion_starter`.

## Git

Quando o usuário pedir para seguir o guia de git, use a política do padrão local:

- Trabalhe direto no `main` por padrão.
- Crie branch apenas para feature grande, refatoração significativa ou alto risco.
- Faça commits pequenos e coesos no formato `tipo: descricao`.
- Atualize documentação viva no mesmo commit da mudança.

## Referências

- [`AGENTS.md`](../AGENTS.md) — roteiro operacional para agentes e mantenedores.
- [`IA.md`](../IA.md) — memória técnica e decisões do projeto.
- [`CONTRIBUTING.md`](../CONTRIBUTING.md) — contribuição externa e padrão de PR.
- `Padrão de qualidade - Felixo System Design/` — referência local ignorada pelo Git.
