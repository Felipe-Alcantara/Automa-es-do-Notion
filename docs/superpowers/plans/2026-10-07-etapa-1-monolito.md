# Etapa 1 — Monolito Felixo Notion MCP: plano de implementação

> **Para agentes:** SUB-SKILL OBRIGATÓRIA: use superpowers:subagent-driven-development
> (recomendado) ou superpowers:executing-plans para executar este plano tarefa por
> tarefa. Os passos usam caixas (`- [ ]`) para acompanhamento.

**Objetivo:** juntar o hub e os módulos `notion-starter`, `notion-tasks-cli` e
`notion-workspace-app` num único repositório e num único pacote `felixo-notion-mcp`,
organizado por camadas, **sem mudar nenhum comportamento observável**: toda linha de
comando aceita hoje continua aceita, todos os testes continuam verdes.

**Arquitetura:** o histórico de cada módulo é importado com `git filter-repo` para
`_importado/<módulo>/` e depois redistribuído por `git mv` para `src/felixo_notion_mcp/`
(`domain/`, `services/`, `repositories/`, `integrations/`, `api/{cli,mcp,http}`, `core/`).
Os imports são reescritos por um script reutilizável e testado, alimentado pela mesma
tabela de movimentos. Um retrato do parser da CLI, gravado **antes** de qualquer
movimento, é o contrato que prova que nada mudou para quem usa.

**Tecnologias:** Python ≥ 3.10, hatchling, uv (lockfile), pytest, ruff, Django ≥ 5.0,
SDK `mcp` ≥ 1.28 < 2, React/Vite (front), PyInstaller ≥ 6 < 7, GitHub Actions.

**Spec:** [`docs/superpowers/specs/2026-10-07-monolito-felixo-notion-mcp-design.md`](../specs/2026-10-07-monolito-felixo-notion-mcp-design.md)
— seções 2 (repositório e layout), 6.5 (renomeações locais), 7 (testes) e 8 (etapa 1).

## Restrições globais

- Python `>=3.10`; CI em `ubuntu-latest`, `windows-latest`, `macos-latest` × `3.10`, `3.11`, `3.12`, `3.13`.
- Distribuição `felixo-notion-mcp`, import `felixo_notion_mcp`, versão **`0.6.0.dev0`** nesta etapa (a `0.6.0` é publicada só na etapa 4).
- Executáveis: `felixo-notion-mcp` (principal), `notion-tasks` (apelido permanente), `notion-automacoes`, `notion-automacoes-app`, `notion-automacoes-mcp` (apelidos de transição).
- Pastas por camada em inglês (`domain`, `services`, `repositories`, `integrations`, `api`, `core`); código, docstrings, mensagens e commits em português.
- **Nada muda para quem usa:** mesmas linhas de comando (retrato), mesmo caminho padrão de perfis (`notion-tasks/.notion-workspaces.json` dentro da pasta de configuração do usuário), mesmos rótulos de app Django (`operations`, `api`) e nomes de tabela.
- **Não mudam nesta etapa:** `REPOSITORIO_GITHUB` do atualizador nativo, nomes de asset `notion-automacoes-<alvo>`, nenhum workflow de release/publicação é criado.
- Linha de base a preservar (medida em 07/10/2026): starter `678 passed` @ `42da753`; CLI `370 passed` @ `73ffcd9`; app `256 passed, 2 skipped` @ `0e958ba`. Os 3 testes do `check-dev.py` saem junto com ele.
- Git: tudo na branch `refactor/monolito`; Conventional Commits; nunca misturar interno (`IA.md`), público (README, guias) e API no mesmo commit; branch apagada (local e remota) após o merge.
- Dependências pinadas em `uv.lock`; `pip-audit` e `npm audit` sem vulnerabilidade alta antes do merge.
- Multiplataforma: `pathlib`, `sys.executable`, nada de separador fixo.
- Refinamento da spec 2.2: os scripts de build nativo vão para `scripts/empacotamento/`, não para `packaging/`. Uma pasta `packaging/` na raiz do `sys.path` esconderia a biblioteca `packaging`, da qual pip, hatch e pytest dependem. O Dockerfile do modo hospedado (etapa 3) fica na raiz, como o guia do Railway pede.
- `modules/` (ignorado pelo git) **não é tocado**: `modules/notion-tasks-cli` e `modules/notion-workspace-app` são clones reais, não links (medido em 07/10/2026).
- Sem segredo, token ou caminho local em código, commit ou documento.

## Foco de revisão

Cinco situações que a spec implica e que nenhum teste existente exercita; cada uma
ganha teste na tarefa dona:

1. **Wheel instalado sem arquivos de dados** (migrações, templates, SPA, arquivo de versão): `pip install felixo-notion-mcp` funcionaria em dev e quebraria instalado. → Tarefa 8, `conferir_wheel`.
2. **Banco SQLite operacional já existente** na máquina: mudar o rótulo do app Django renomearia tabelas e quebraria migrações. → Tarefa 6, `test_rotulos_django_preservados`.
3. **Perfis salvos na máquina:** se o caminho padrão do store mudar, a pessoa "perde" os workspaces. → Tarefa 5, contrato `perfis.relativo` do retrato.
4. **`python start_app.py` rodado do checkout sem nada instalado** (inclusive Windows): é a porta de entrada obrigatória do padrão. → Tarefa 7, `test_start_app_raiz_acha_src_sem_instalacao`.
5. **Configurações MCP existentes** que chamam `notion-automacoes-mcp` ou `notion-tasks`: o apelido precisa continuar existindo. → Tarefa 5, `test_executaveis_de_transicao_declarados`.

---

## Estrutura de arquivos (destino)

| Caminho | Responsabilidade |
| --- | --- |
| `pyproject.toml` · `uv.lock` | pacote único, extras `app`, `planilha`, `native`, `dev`; ruff; pytest |
| `src/felixo_notion_mcp/__init__.py` | API pública da biblioteca (o antigo `notion_starter/__init__.py`) |
| `src/felixo_notion_mcp/domain/` | `properties`, `readers`, `content`, `schema`, `tasks`, `valores_br`, `git_historico` |
| `src/felixo_notion_mcp/services/` | serviços do starter + `inventory`, `propriedades`, `preflight` |
| `src/felixo_notion_mcp/integrations/` | `notion_client` (ex-`client`), `github`, `openrouter`, `notion` (adaptador) |
| `src/felixo_notion_mcp/core/` | `constants`, `exceptions`, `logging`, `utils`, `config`, `workspaces` |
| `src/felixo_notion_mcp/repositories/operations/` | app Django `operations` (rótulo preservado) |
| `src/felixo_notion_mcp/api/cli/` | `notion_tasks`, `unificada`, `atualizacao_nativa`, `versao`, `retrato` (novo) |
| `src/felixo_notion_mcp/api/mcp/server.py` | ex-`server/mcp_server.py` |
| `src/felixo_notion_mcp/api/http/` | `config/` (settings, urls, asgi, wsgi), `rest/` (ex-`server/api`, rótulo `api`), `templates/`, `static/`, `manage.py` |
| `src/felixo_notion_mcp/api/launcher.py` | ex-`start_app.py` do app (menu completo) |
| `start_app.py` | porta de entrada fina: acha `src/` e chama o launcher |
| `front/` | SPA React; build em `src/felixo_notion_mcp/api/http/static/frontend/` |
| `examples/` | exemplos do starter (usados pelo menu Iniciar) |
| `scripts/migracao/` | `mapa_modulos.py`, `reescrever_imports.py`, `mover_para_camadas.py`, `gravar_retrato_cli.py` |
| `scripts/empacotamento/` | `build_native.py`, `native_entrypoint.py`, `smoke_native.py` (build nativo) e `conferir_wheel.py` |
| `scripts/notion/` | scripts de dados do Notion hoje soltos na raiz |
| `tests/{domain,services,integrations,core,repositories,api/cli,api/mcp,api/http,contrato,scripts}/` | suítes por camada |
| `.github/workflows/ci.yml` | matriz de testes, front e auditoria |
| `docs/ARQUITETURA.md` | camadas e mapa de origem → destino (novo) |
| `docs/ia-archive/IA-<módulo>.md` | `IA.md` de cada módulo, na íntegra |

---

### Tarefa 1: Preparar a branch, afastar as sobras locais e gravar o retrato da CLI

**Arquivos:**
- Criar: `pyproject.toml` (esqueleto), `src/felixo_notion_mcp/__init__.py` (vazio por ora), `src/felixo_notion_mcp/api/__init__.py`, `src/felixo_notion_mcp/api/cli/__init__.py`, `src/felixo_notion_mcp/api/cli/retrato.py`, `scripts/migracao/gravar_retrato_cli.py`, `tests/contrato/retrato_cli.json`
- Teste: `tests/api/cli/test_retrato.py`

**Interfaces:**
- Produz: `retratar_parser(parser: argparse.ArgumentParser) -> dict[str, Any]`; arquivo `tests/contrato/retrato_cli.json` com as chaves `notion_tasks`, `unificada` e `perfis` (`{"relativo": str}`).

- [ ] **Passo 1: Criar a branch e afastar as sobras ignoradas que colidem com o layout**

```bash
git switch main && git pull --ff-only
git switch -c refactor/monolito
SOBRAS="../Automa-es-do-Notion-sobras-2026-10-07"; mkdir -p "$SOBRAS"
for d in cli front server src; do [ -e "$d" ] && git check-ignore -q "$d" && mv "$d" "$SOBRAS/"; done
```

Esperado: `git status --short` vazio; `ls "$SOBRAS"` lista as pastas movidas.
`operacional.sqlite3`, `.notion-backups/` e `Arquivos/` **ficam** onde estão:
continuam ignorados e não colidem com nada (refinamento da spec 2.3.7, registrado no
`IA.md` na Tarefa 10).

- [ ] **Passo 2: Escrever o teste do retrato**

```python
# tests/api/cli/test_retrato.py
import argparse, json
from felixo_notion_mcp.api.cli.retrato import retratar_parser

def _parser():
    p = argparse.ArgumentParser(prog="x")
    sub = p.add_subparsers(dest="comando")
    el = sub.add_parser("editar-linha", aliases=["el"])
    el.add_argument("pagina_id")
    el.add_argument("--set", action="append", dest="valores")
    el.add_argument("--sim", action="store_true")
    return p

def test_retrato_registra_subcomandos_aliases_e_argumentos():
    r = retratar_parser(_parser())
    assert set(r["subcomandos"]) == {"editar-linha", "el"}
    args = {a["destino"]: a for a in r["subcomandos"]["editar-linha"]["argumentos"]}
    assert args["pagina_id"]["opcoes"] == []
    assert args["valores"]["opcoes"] == ["--set"]
    assert args["valores"]["acao"] == "_AppendAction"
    assert args["sim"]["padrao"] == "False"

def test_retrato_e_deterministico_e_serializavel():
    a = json.dumps(retratar_parser(_parser()), sort_keys=True)
    b = json.dumps(retratar_parser(_parser()), sort_keys=True)
    assert a == b
```

- [ ] **Passo 3: Rodar e ver falhar**

Run: `python -m pytest tests/api/cli/test_retrato.py -q` → FAIL com `ModuleNotFoundError: felixo_notion_mcp`.

- [ ] **Passo 4: Esqueleto do `pyproject.toml` e `retratar_parser`**

`pyproject.toml` mínimo: `[build-system]` hatchling; `[project] name = "felixo-notion-mcp"`,
`version = "0.6.0.dev0"`, `requires-python = ">=3.10"`;
`[tool.hatch.build.targets.wheel] packages = ["src/felixo_notion_mcp"]`;
`[tool.pytest.ini_options] testpaths = ["tests"]`, `pythonpath = ["src", "."]` (a raiz deixa `scripts.*` importável),
`addopts = "--import-mode=importlib"`; `[tool.ruff] line-length = 100`,
`target-version = "py310"`, `src = ["src", "tests"]`, `extend-exclude = ["_importado"]`,
`[tool.ruff.lint] select = ["E", "F", "I", "UP", "B"]`.

`retratar_parser` percorre `parser._actions` recursivamente. Para cada ação: `opcoes`
(ordenadas), `destino`, `acao` (`type(acao).__name__`), `nargs` (`str`), `obrigatorio`,
`escolhas` (lista ordenada de `str` ou `None`) e `padrao` (`repr` ou `None` quando
`SUPPRESS`). Para `_SubParsersAction`, devolve `{"subcomandos": {nome: retrato}}`,
incluindo apelidos. **Não** inclui textos de ajuda: o contrato é o que a linha de
comando aceita.

- [ ] **Passo 5: Rodar e ver passar**

Run: `python -m pytest tests/api/cli/test_retrato.py -q` → `2 passed`.

- [ ] **Passo 6: Gravar o retrato a partir do código ANTIGO**

`scripts/migracao/gravar_retrato_cli.py --cli <clone notion-tasks-cli> --starter <clone notion-starter> --saida tests/contrato/retrato_cli.json`
(crie também `scripts/__init__.py` e `scripts/migracao/__init__.py`):
põe os dois caminhos no `sys.path`, carrega `retrato.py` pelo caminho do arquivo
(`importlib.util.spec_from_file_location`), fixa `XDG_CONFIG_HOME` e `APPDATA` numa pasta
falsa, importa `cli.notion_tasks.construir_parser`, `cli.unificada.construir_parser` e
`core.workspaces.caminho_padrao`, e grava JSON (`sort_keys=True`, `ensure_ascii=False`)
com `perfis.relativo` = `caminho_padrao()` relativo à pasta falsa, em formato POSIX.

```bash
ANTIGOS=$(mktemp -d)
git clone -q https://github.com/Felipe-Alcantara/notion-tasks-cli.git "$ANTIGOS/cli" && git -C "$ANTIGOS/cli" checkout -q 73ffcd9
git clone -q https://github.com/Felipe-Alcantara/notion-starter.git "$ANTIGOS/starter" && git -C "$ANTIGOS/starter" checkout -q 42da753
python scripts/migracao/gravar_retrato_cli.py \
  --cli "$ANTIGOS/cli" --starter "$ANTIGOS/starter" --saida tests/contrato/retrato_cli.json
python -c "import json;d=json.load(open('tests/contrato/retrato_cli.json'));print(len(d['notion_tasks']['subcomandos']), d['perfis'])"
```

Esperado: a saída mostra a contagem de subcomandos, apelidos incluídos, e `{'relativo': 'notion-tasks/.notion-workspaces.json'}`. Os SHAs fixos tornam o retrato reproduzível.

- [ ] **Passo 7: Commit**

```bash
git add pyproject.toml src tests scripts
git commit -m "test: gravar o retrato da CLI antes de juntar os módulos"
```

---

### Tarefa 2: Importar o histórico dos três módulos

**Arquivos:** cria `_importado/notion-starter/`, `_importado/notion-tasks-cli/`, `_importado/notion-workspace-app/` (temporários; somem até a Tarefa 6).

- [ ] **Passo 1: Contar as tags antes**

Run: `git tag | wc -l` → anote N.

- [ ] **Passo 2: Importar cada módulo sem tags**

```bash
TMP=$(mktemp -d)
for m in notion-starter notion-tasks-cli notion-workspace-app; do
  git clone -q "https://github.com/Felipe-Alcantara/$m.git" "$TMP/$m"
  git -C "$TMP/$m" log -1 --format="%h %s"           # anote o SHA importado
  git -C "$TMP/$m" filter-repo --to-subdirectory-filter "_importado/$m"
  git fetch -q --no-tags "$TMP/$m" main
  git merge --no-ff --allow-unrelated-histories FETCH_HEAD -m "chore: importar o histórico do $m"
done
```

`--no-tags` é obrigatório: `notion-starter` e `notion-tasks-cli` têm tags `v0.x.y` que
colidiriam entre si.

- [ ] **Passo 3: Verificar o histórico preservado**

```bash
git tag | wc -l                                                      # igual a N
git log --oneline --follow -- _importado/notion-starter/src/notion_starter/client.py | wc -l   # > 1
git log --oneline -1 --format=%s -- _importado/notion-tasks-cli/cli/atualizacao_nativa.py      # commit antigo do módulo
```

Os merges já são os commits desta tarefa (um por módulo).

---

### Tarefa 3: Scripts de migração (mapa de módulos, reescrita de imports e movimentos)

**Arquivos:**
- Criar: `scripts/migracao/mapa_modulos.py`, `scripts/migracao/reescrever_imports.py`, `scripts/migracao/mover_para_camadas.py`
- Teste: `tests/scripts/test_migracao.py`

**Interfaces:**
- Produz:
  - `@dataclass(frozen=True) class Movimento: origem: str; destino: str; modulo: str` (`modulo` ∈ `notion-starter|notion-tasks-cli|notion-workspace-app`; `destino == ""` significa remover)
  - `@dataclass(frozen=True) class RaizPython: diretorio: str; prefixo: str`
  - `TABELA_MOVIMENTOS: tuple[Movimento, ...]` e `RAIZES: tuple[RaizPython, ...]`
  - `montar_mapa(movimentos: Sequence[Movimento], raizes: Sequence[RaizPython]) -> dict[str, str]`: nome pontuado antigo → novo, incluindo pacotes
  - `class ImportAmbiguo(Exception)` com `arquivo`, `linha` e `trecho`
  - `reescrever_codigo(texto: str, mapa: Mapping[str, str], *, em_migracao_django: bool) -> tuple[str, list[str]]`: texto novo e trocas feitas
  - CLIs: `python -m scripts.migracao.reescrever_imports (--simular|--aplicar) CAMINHO...` e `python -m scripts.migracao.mover_para_camadas --modulo NOME (--simular|--aplicar)`

- [ ] **Passo 1: Escrever os testes**

```python
# tests/scripts/test_migracao.py
import pytest
from scripts.migracao.mapa_modulos import Movimento, RAIZES, montar_mapa
from scripts.migracao.reescrever_imports import ImportAmbiguo, reescrever_codigo

MAPA = {
    "notion_starter": "felixo_notion_mcp",
    "notion_starter.client": "felixo_notion_mcp.integrations.notion_client",
    "cli": "felixo_notion_mcp.api.cli",
    "cli.notion_tasks": "felixo_notion_mcp.api.cli.notion_tasks",
    "core": "felixo_notion_mcp.core",
    "operations": "felixo_notion_mcp.repositories.operations",
}

def test_reescreve_from_import_e_import_com_alias():
    novo, _ = reescrever_codigo(
        "from notion_starter.client import NotionClient\nimport cli.notion_tasks as nt\n",
        MAPA, em_migracao_django=False)
    assert novo == ("from felixo_notion_mcp.integrations.notion_client import NotionClient\n"
                    "import felixo_notion_mcp.api.cli.notion_tasks as nt\n")

def test_reescreve_alvo_de_monkeypatch_em_string():
    novo, _ = reescrever_codigo('monkeypatch.setattr("cli.notion_tasks.main", f)\n',
                                MAPA, em_migracao_django=False)
    assert '"felixo_notion_mcp.api.cli.notion_tasks.main"' in novo

def test_from_pacote_import_submodulo_sem_renomear():
    novo, _ = reescrever_codigo("from core import workspaces\n", MAPA, em_migracao_django=False)
    assert novo == "from felixo_notion_mcp.core import workspaces\n"

def test_nao_toca_prefixo_parecido_nem_a_biblioteca_mcp():
    src = 'import client_x\nfrom mcp.server.fastmcp import FastMCP\nx = "clientes.cli"\n'
    assert reescrever_codigo(src, MAPA, em_migracao_django=False)[0] == src

def test_string_de_rotulo_django_nao_muda_dentro_de_migracao():
    src = 'dependencies = [("operations", "0001_initial")]\n'
    assert reescrever_codigo(src, MAPA, em_migracao_django=True)[0] == src

def test_import_de_modulo_renomeado_pelo_pacote_vira_pendencia():
    with pytest.raises(ImportAmbiguo):
        reescrever_codigo("from notion_starter import client\n", MAPA, em_migracao_django=False)

def test_from_pacote_fora_do_mapa_import_modulo_movido():
    mapa = {"scripts.build_native": "scripts.empacotamento.build_native"}
    novo, _ = reescrever_codigo("from scripts import build_native\n", mapa, em_migracao_django=False)
    assert novo == "from scripts.empacotamento import build_native\n"

def test_reescrita_e_idempotente():
    uma, _ = reescrever_codigo("from cli.notion_tasks import main\n", MAPA, em_migracao_django=False)
    assert reescrever_codigo(uma, MAPA, em_migracao_django=False)[0] == uma

def test_mapa_do_app_vale_com_e_sem_prefixo_server():
    mov = [Movimento("_importado/notion-workspace-app/server/mcp_server.py",
                     "src/felixo_notion_mcp/api/mcp/server.py", "notion-workspace-app")]
    mapa = montar_mapa(mov, RAIZES)
    assert mapa["mcp_server"] == mapa["server.mcp_server"] == "felixo_notion_mcp.api.mcp.server"

def test_tabela_sem_destinos_duplicados_fora_das_unificacoes():
    from scripts.migracao.mapa_modulos import TABELA_MOVIMENTOS, UNIFICADOS
    destinos = [m.destino for m in TABELA_MOVIMENTOS if m.destino]
    repetidos = {d for d in destinos if destinos.count(d) > 1}
    assert repetidos <= UNIFICADOS
```

- [ ] **Passo 2: Rodar e ver falhar**

Run: `python -m pytest tests/scripts/test_migracao.py -q` → FAIL (`ModuleNotFoundError: scripts.migracao`).

- [ ] **Passo 3: Implementar `mapa_modulos.py`**

`RAIZES`: `("_importado/notion-starter/src", "")`, `("_importado/notion-tasks-cli", "")`,
`("_importado/notion-workspace-app", "")` e `("_importado/notion-workspace-app/server", "")`;
as duas últimas dão a cada arquivo do app os nomes com e sem `server.`. O nome novo sai
do caminho sob `src/` (`/` → `.`, sem `.py` e sem `__init__`). Destino fora de `src/` (ex.:
`scripts/empacotamento/build_native.py`) usa o caminho a partir da raiz do repositório.
Diretórios entram no mapa como pacotes, exceto `scripts`, que é nome de pacote nos dois
lados e não pode ser reescrito inteiro. Inclua o pacote raiz antigo de cada origem: `notion_starter`, `cli`,
`core`, `integrations`, `services`, `server`, `api`, `config`, `operations`, além de
`start_app` → `felixo_notion_mcp.api.launcher`.
`UNIFICADOS = {"src/felixo_notion_mcp/core/config.py", "src/felixo_notion_mcp/integrations/notion.py"}`.

`TABELA_MOVIMENTOS`, origem relativa a `_importado/<módulo>/` (um item por arquivo;
diretórios abaixo expandem para os arquivos que contêm):

| Módulo | Origem | Destino |
| --- | --- | --- |
| starter | `src/notion_starter/__init__.py`, `py.typed` (se existir) | `src/felixo_notion_mcp/` |
| starter | `src/notion_starter/client.py` | `src/felixo_notion_mcp/integrations/notion_client.py` |
| starter | `src/notion_starter/{github,openrouter}.py` | `src/felixo_notion_mcp/integrations/` |
| starter | `src/notion_starter/{properties,readers,content,schema,tasks,valores_br,git_historico}.py` | `src/felixo_notion_mcp/domain/` |
| starter | `src/notion_starter/inventory.py`, `src/notion_starter/services/*` | `src/felixo_notion_mcp/services/` |
| starter | `src/notion_starter/{constants,exceptions,logging,utils}.py` | `src/felixo_notion_mcp/core/` |
| starter | `examples/*` | `examples/` |
| starter | `tests/test_*.py` | `tests/<camada>/` (regra abaixo) |
| CLI | `cli/*` | `src/felixo_notion_mcp/api/cli/` |
| CLI | `core/{config,workspaces}.py` | `src/felixo_notion_mcp/core/` |
| CLI | `integrations/notion.py` | `src/felixo_notion_mcp/integrations/notion.py` |
| CLI | `services/{propriedades,preflight}.py` | `src/felixo_notion_mcp/services/` |
| CLI | `scripts/{build_native,native_entrypoint,smoke_native}.py` | `scripts/empacotamento/` |
| CLI | `tests/test_*.py` | `tests/<camada>/` |
| app | `server/mcp_server.py` | `src/felixo_notion_mcp/api/mcp/server.py` |
| app | `server/config/*` | `src/felixo_notion_mcp/api/http/config/` |
| app | `server/api/*` | `src/felixo_notion_mcp/api/http/rest/` |
| app | `server/manage.py` | `src/felixo_notion_mcp/api/http/manage.py` |
| app | `server/templates/*`, `server/static/*` | `src/felixo_notion_mcp/api/http/templates/`, `.../static/` |
| app | `server/operations/*` (com `migrations/`) | `src/felixo_notion_mcp/repositories/operations/` |
| app | `server/core/config.py`, `server/integrations/notion.py` | unificados (Tarefa 6, passo 2) |
| app | `start_app.py` | `src/felixo_notion_mcp/api/launcher.py` |
| app | `front/*` | `front/` |
| app | `tests/test_*.py` | `tests/<camada>/` |
| todos | `IA.md` | `docs/ia-archive/IA-<módulo>.md` |
| todos | shims (`services/*.py` e `integrations/{github,openrouter}.py` da CLI e do app), `core/__init__.py`, `server/__init__.py`, `tests/conftest.py`, `README.md`, `AGENTS.md`, `CONTRIBUTING.md`, `QUALIDADE.md`, `LICENSE`, `.editorconfig`, `.env.example`, `.gitignore`, `pyproject.toml`, `requirements.txt`, `.github/*`, `start_app.py` da CLI | removidos (destino vazio); conteúdo útil absorvido pela raiz na Tarefa 10 |

**Regra de pasta dos testes:** `test_client*` e `test_integrations_*` → `tests/integrations/`;
`test_services_*`, `test_importacao`, `test_ingestao_*`, `test_inventory`,
`test_fonte_planilha`, `test_anexos`, `test_relatorios_docx_*` → `tests/services/`;
`test_content*`, `test_properties`, `test_readers`, `test_schema*`, `test_tasks`,
`test_valores_br`, `test_git_historico` → `tests/domain/`; `test_hierarquia_excecoes`,
`test_utils_ids`, `test_workspaces`, `test_prevencao_json_surrogate` → `tests/core/`;
`test_mcp_server` → `tests/api/mcp/`; `test_api_*`, `test_front` → `tests/api/http/`;
`test_start_app` → `tests/api/`; os demais testes da CLI → `tests/api/cli/`. Nome repetido
entre módulos recebe sufixo de origem (`test_versao_starter.py`, `test_versao_cli.py`).

- [ ] **Passo 4: Implementar `reescrever_codigo`**

Regras, aplicadas com a chave mais longa primeiro:

1. linhas `import a.b[ as c]` e `from a.b import ...` (imports relativos não mudam);
2. literais de string cujo conteúdo é igual a um nome antigo ou começa com `nome_antigo.`; não se aplica quando `em_migracao_django=True`;
3. `from P import x`, quando `P.x` está no mapa: se o último nome de `mapa[P.x]` é `x`, vira `from <pai de mapa[P.x]> import x` (vale também quando `P` não está no mapa, como em `from scripts import build_native`); se o arquivo foi renomeado, ou se os nomes importados juntos vão para pais diferentes, levanta `ImportAmbiguo` para correção manual.

Fronteira de palavra dos dois lados (`(?<![\w.])` e `(?![\w])` antes do `.` seguinte).
`mover_para_camadas` usa `git mv` (criando as pastas), pula o item já movido e remove
com `git rm` quando o destino é vazio. A CLI de `reescrever_imports` imprime cada troca;
com pendências, sai com código 1 e lista `arquivo:linha`.

- [ ] **Passo 5: Rodar e ver passar**

Run: `python -m pytest tests/scripts/test_migracao.py -q` → `10 passed`.

- [ ] **Passo 6: Commit**

```bash
git add scripts/migracao tests/scripts
git commit -m "feat: scripts de migração dos módulos para as camadas do monolito"
```

---

### Tarefa 4: Pacote único e núcleo (ex-starter) nas camadas

**Arquivos:** modifica `pyproject.toml`; move os arquivos do starter conforme a tabela; testes em `tests/{domain,services,integrations,core}/`.

**Interfaces:**
- Consome: `TABELA_MOVIMENTOS`, `reescrever_imports`, `mover_para_camadas` (Tarefa 3).
- Produz: `felixo_notion_mcp` importável com a mesma API pública do `notion_starter`.

- [ ] **Passo 1: Completar o `pyproject.toml`**

`dependencies`: `python-docx>=1.1`, `requests>=2.25`, `mcp>=1.28,<2`,
`typing_extensions>=4.0; python_version < '3.11'`. `optional-dependencies`:
`app = ["Django>=5.0", "questionary>=2.0", "rich>=13.0"]`, `planilha = ["openpyxl>=3.1"]`,
`native = ["pyinstaller>=6,<7"]`, `dev = ["pytest>=7.0", "responses>=0.23", "ruff>=0.4", "openpyxl>=3.1", "pip-audit>=2.7"]`.
Metadados (`description`, `readme`, `license`, `authors = Felipe Alcantara`, `keywords`,
`classifiers`, `urls` → `https://github.com/Felipe-Alcantara/Felixo-Notion-MCP`).
Adicione `"**/migrations/*.py"` ao `extend-exclude` do ruff, como no app.

- [ ] **Passo 2: Mover o starter**

```bash
python -m scripts.migracao.mover_para_camadas --modulo notion-starter --simular   # revise a lista
python -m scripts.migracao.mover_para_camadas --modulo notion-starter --aplicar
```

- [ ] **Passo 3: Reescrever os imports**

```bash
python -m scripts.migracao.reescrever_imports --simular src tests examples
python -m scripts.migracao.reescrever_imports --aplicar src tests examples
```

Esperado: código de saída 0. Pendência `ImportAmbiguo` se resolve à mão no arquivo e
linha indicados, importando do caminho novo (ex.: `from felixo_notion_mcp.integrations import notion_client as client`).

- [ ] **Passo 4: Rodar a suíte do núcleo**

```bash
uv venv && uv pip install -e ".[dev,planilha]"
uv run ruff check --fix --select I src tests && uv run ruff check src tests
uv run python -m pytest tests/domain tests/services tests/integrations tests/core -q
```

Esperado: `678 passed` (a linha de base do starter).

- [ ] **Passo 5: Commit**

```bash
git add -A src tests examples pyproject.toml _importado
git commit -m "refactor: mover o núcleo do notion-starter para as camadas do monolito"
```

---

### Tarefa 5: CLI nas camadas, com os executáveis e o contrato do retrato

**Arquivos:**
- Move os arquivos da CLI conforme a tabela; modifica `pyproject.toml` (`[project.scripts]`), `src/felixo_notion_mcp/api/cli/notion_tasks.py` (remove o `LOCAL_STARTER`/`sys.path`, linhas 20–27 da origem) e `api/cli/unificada.py` (`DISTRIBUICAO`).
- Teste: `tests/contrato/test_retrato_cli.py`, `tests/api/cli/test_pyproject.py` (expectativas novas).

**Interfaces:**
- Consome: `retratar_parser` (Tarefa 1); `felixo_notion_mcp.core.workspaces.caminho_padrao() -> Path`.
- Produz: executáveis `felixo-notion-mcp = "felixo_notion_mcp.api.cli.unificada:main"`, `notion-tasks = "felixo_notion_mcp.api.cli.notion_tasks:main"`, `notion-automacoes = "felixo_notion_mcp.api.cli.unificada:main"`; `unificada.DISTRIBUICAO = "felixo-notion-mcp"`.

- [ ] **Passo 1: Escrever o teste de contrato e o de executáveis**

```python
# tests/contrato/test_retrato_cli.py
import json
from pathlib import Path
from felixo_notion_mcp.api.cli import notion_tasks, unificada
from felixo_notion_mcp.api.cli.retrato import retratar_parser
from felixo_notion_mcp.core import workspaces

RETRATO = json.loads((Path(__file__).parent / "retrato_cli.json").read_text(encoding="utf-8"))

def test_notion_tasks_aceita_exatamente_as_mesmas_linhas_de_comando():
    assert retratar_parser(notion_tasks.construir_parser()) == RETRATO["notion_tasks"]

def test_fachada_aceita_exatamente_as_mesmas_linhas_de_comando():
    assert retratar_parser(unificada.construir_parser()) == RETRATO["unificada"]

def test_perfis_continuam_no_mesmo_caminho(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path)); monkeypatch.setenv("APPDATA", str(tmp_path))
    rel = workspaces.caminho_padrao().relative_to(tmp_path).as_posix()
    assert rel == RETRATO["perfis"]["relativo"]
```

Em `tests/api/cli/test_pyproject.py` (vindo da CLI), troque as expectativas pelo
contrato novo e acrescente:

```python
def test_executaveis_de_transicao_declarados(pyproject):
    scripts = pyproject["project"]["scripts"]
    assert {"felixo-notion-mcp", "notion-tasks", "notion-automacoes",
            "notion-automacoes-app", "notion-automacoes-mcp"} <= set(scripts)
    assert pyproject["project"]["name"] == "felixo-notion-mcp"
```

(`notion-automacoes-app` e `notion-automacoes-mcp` só passam depois da Tarefa 6; marque
esse teste com `xfail(strict=True)` até lá e remova a marca na Tarefa 6.)

- [ ] **Passo 2: Mover, reescrever e ajustar**

Rode `mover_para_camadas --modulo notion-tasks-cli` e `reescrever_imports` (como na
Tarefa 4). Depois: remova o bloco `LOCAL_STARTER`; troque `DISTRIBUICAO` para
`"felixo-notion-mcp"` e as mensagens `pipx install/upgrade notion-automacoes` para
`felixo-notion-mcp`; declare os três executáveis; leve as fixtures autouse
`backups_isolados` e `perfis_isolados` do antigo `conftest.py` da CLI para
`tests/conftest.py`, válido para toda a suíte.

**Assertivas que mudam de propósito (e só estas):** `test_pyproject.py` (nome e
executáveis), `test_cli_unificada.py` (texto `pipx upgrade felixo-notion-mcp`) e
`test_versao_cli.py` (nome da distribuição). Qualquer outra assertiva que falhar é
regressão: corrija o código, não o teste.

- [ ] **Passo 3: Rodar**

```bash
uv pip install -e ".[dev,planilha]"
uv run ruff check --fix --select I src tests && uv run ruff check src tests
uv run python -m pytest tests -q
uv run notion-tasks --help >/dev/null && uv run felixo-notion-mcp doctor --json
```

Esperado: `≥ 1048 passed` (678 do starter + 370 da CLI + os testes novos das tarefas 1,
3 e 5) e `1 xfailed` (o teste de transição); `doctor` com `"ok": true`.

- [ ] **Passo 4: Commit**

```bash
git add -A
git commit -m "refactor: mover a CLI para api/cli mantendo o contrato de linha de comando"
```

---

### Tarefa 6: App (MCP, HTTP, operações, launcher e front) nas camadas

**Arquivos:** move o app conforme a tabela; modifica `api/http/config/settings.py`, `repositories/operations/apps.py`, `api/http/rest/apps.py`, `api/http/manage.py`, `front/vite.config.*`, `pyproject.toml`, `.gitignore`.
- Teste: `tests/repositories/test_rotulos_django.py`.

**Interfaces:**
- Produz: `DJANGO_SETTINGS_MODULE = "felixo_notion_mcp.api.http.config.settings"`; `felixo_notion_mcp.api.mcp.server:main`; `felixo_notion_mcp.api.launcher:main(argv: list[str] | None = None) -> None`.

- [ ] **Passo 1: Escrever o teste dos rótulos**

```python
# tests/repositories/test_rotulos_django.py
import pytest
pytest.importorskip("django")
import django
from django.conf import settings

def test_rotulos_django_preservados(monkeypatch):
    monkeypatch.setenv("DJANGO_SETTINGS_MODULE", "felixo_notion_mcp.api.http.config.settings")
    django.setup()
    from django.apps import apps
    from felixo_notion_mcp.repositories.operations.models import Job, Lock
    assert apps.get_app_config("operations").name == "felixo_notion_mcp.repositories.operations"
    assert apps.get_app_config("api").name == "felixo_notion_mcp.api.http.rest"
    assert (Job._meta.db_table, Lock._meta.db_table) == ("operations_job", "operations_lock")
```

Rode e veja falhar (módulo ausente).

- [ ] **Passo 2: Mover, unificar e reescrever**

1. Confira que os duplicados diferem só na exceção de configuração:
   `diff _importado/notion-workspace-app/server/core/config.py src/felixo_notion_mcp/core/config.py`
   e o mesmo para `integrations/notion.py`. Esperado: só as linhas de `ImproperlyConfigured`.
   Fica a versão da CLI, sem Django; a do app vai para `git rm`.
2. `mover_para_camadas --modulo notion-workspace-app --aplicar`; em seguida
   `reescrever_imports --aplicar src tests`. As `migrations/` ficam protegidas pela regra
   `em_migracao_django`.
3. `OperationsConfig` e `ApiConfig` ganham `label = "operations"` e `label = "api"`.
4. Apague os `sys.path.insert` de `api/mcp/server.py`, `api/http/manage.py` e do launcher.
5. `api/http/manage.py` usa `"felixo_notion_mcp.api.http.config.settings"`.
6. `front/vite.config`: `outDir: '../src/felixo_notion_mcp/api/http/static/frontend'`.
7. `pyproject.toml`: `artifacts = ["src/felixo_notion_mcp/api/http/static/frontend/**"]`;
   executáveis `notion-automacoes-app = "felixo_notion_mcp.api.launcher:main"` e
   `notion-automacoes-mcp = "felixo_notion_mcp.api.mcp.server:main"`. Retire o
   `xfail` da Tarefa 5.
8. Launcher: a raiz do checkout é `Path(__file__).resolve().parents[3]`, válida só se
   houver `pyproject.toml` lá; sem isso, é o modo instalado (mesmos ramos do
   `start_app.py` antigo). O Instalar/Setup passa a rodar `pip install -e ".[app,dev]"`
   na raiz.
9. `.gitignore`: troque `server/staticfiles/` por `src/felixo_notion_mcp/api/http/staticfiles/`
   e acrescente `src/felixo_notion_mcp/api/http/static/frontend/`.
10. Remova `extend-exclude = ["_importado"]` do ruff e confirme que `_importado/` ficou
    vazio: `git ls-files _importado | wc -l` → `0`.

**Assertivas que mudam de propósito:** `test_front.py` (caminho do build) e
`test_start_app.py` (módulo `felixo_notion_mcp.api.launcher`).

- [ ] **Passo 3: Rodar Python e front**

```bash
uv pip install -e ".[app,dev,planilha]"
uv run ruff check --fix --select I src tests && uv run ruff check .
uv run python -m pytest tests -q
(cd front && npm ci && npm run lint && npm run build)
ls src/felixo_notion_mcp/api/http/static/frontend/index.html
uv run python -m felixo_notion_mcp.api.http.manage migrate --check
```

Esperado: `≥ 1304 passed` (678 + 370 + 256), sem `skipped` de Django; `index.html`
presente; `migrate --check` sem migração pendente.

- [ ] **Passo 4: Commit**

```bash
git add -A
git commit -m "refactor: mover MCP, API Django, operações, launcher e SPA para as camadas"
```

---

### Tarefa 7: Porta de entrada única, `doctor` com a origem do pacote e aposentadoria das ferramentas do hub

**Arquivos:**
- Criar: `start_app.py` (substitui o do hub), `scripts/notion/criar_tarefas_investigadas_2026_08_18.py` (`git mv` da raiz).
- Remover: `bootstrap.py`, `check-dev.py`, `sync.py`, `SYNC.md`, `tests/test_check_dev.py`.
- Modificar: `src/felixo_notion_mcp/api/cli/unificada.py` (`diagnosticar`).
- Teste: `tests/test_start_app_raiz.py`, `tests/api/cli/test_doctor_origem.py`.

**Interfaces:**
- Produz: `start_app._garantir_src_no_path(raiz: Path) -> bool` (devolve `True` quando inseriu `raiz / "src"`); em `diagnosticar()["checks"]`, item `{"nome": "felixo-notion-mcp", ...}` cujo detalhe traz versão e pasta de origem do pacote, além de `"checkout editável"` quando `pyproject.toml` existe dois níveis acima da pasta do pacote.

- [ ] **Passo 1: Escrever os testes**

```python
# tests/test_start_app_raiz.py
import importlib.util, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]

def _carregar():
    spec = importlib.util.spec_from_file_location("start_app_raiz", RAIZ / "start_app.py")
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod

def test_start_app_raiz_acha_src_sem_instalacao(monkeypatch):
    mod = _carregar()
    monkeypatch.setattr(sys, "path", [p for p in sys.path if not p.endswith("src")])
    monkeypatch.setattr(mod.importlib.util, "find_spec", lambda nome: None)
    assert mod._garantir_src_no_path(RAIZ) is True
    assert str(RAIZ / "src") in sys.path

def test_start_app_raiz_nao_mexe_no_path_quando_instalado():
    assert _carregar()._garantir_src_no_path(RAIZ) is False
```

```python
# tests/api/cli/test_doctor_origem.py
from pathlib import Path
import felixo_notion_mcp
from felixo_notion_mcp.api.cli.unificada import diagnosticar

def test_doctor_mostra_de_onde_o_pacote_vem():
    checks = {c["nome"]: c for c in diagnosticar()["checks"]}
    detalhe = checks["felixo-notion-mcp"]["detalhe"]
    assert str(Path(felixo_notion_mcp.__file__).resolve().parent) in detalhe
    assert "checkout editável" in detalhe
```

Antes de escrever o teste do doctor, confirme os nomes das chaves que `_status`
devolve (`nome`/`detalhe`) e ajuste se forem outros. Rode e veja os dois arquivos falharem.

- [ ] **Passo 2: Implementar**

`start_app.py` na raiz fica só com stdlib: `_garantir_src_no_path` usa
`importlib.util.find_spec("felixo_notion_mcp")` e `pathlib`; `main()` chama
`felixo_notion_mcp.api.launcher.main(sys.argv[1:])`. O docstring descreve o menu
(Iniciar/Rodar, Instalar/Setup, Configurar, Status/Sair). No `diagnosticar`, o check
`notion-starter` dá lugar ao check `felixo-notion-mcp` (versão via
`versao_distribuicao()`). Depois: `git rm bootstrap.py check-dev.py sync.py SYNC.md tests/test_check_dev.py`
e `git mv criar_tarefas_investigadas_2026_08_18.py scripts/notion/`.

- [ ] **Passo 3: Rodar**

```bash
uv run python -m pytest tests -q
uv run felixo-notion-mcp doctor
python start_app.py   # menu abre; escolha Status e confira o check "felixo-notion-mcp"; saia
```

Esperado: suíte verde; o `doctor` mostra a origem em `src/felixo_notion_mcp`; o menu abre.

- [ ] **Passo 4: Commit**

```bash
git add -A
git commit -m "refactor: start_app único na raiz e doctor no lugar de bootstrap e check-dev"
```

---

### Tarefa 8: Lockfile, CI em matriz, auditoria e conferência do wheel

**Arquivos:**
- Criar: `uv.lock`, `.github/workflows/ci.yml`, `scripts/empacotamento/__init__.py`, `scripts/empacotamento/conferir_wheel.py`
- Teste: `tests/scripts/test_conferir_wheel.py`

**Interfaces:**
- Produz: `ARQUIVOS_OBRIGATORIOS: tuple[str, ...]`; `faltando_no_wheel(caminho_wheel: Path) -> list[str]`; CLI `python -m scripts.empacotamento.conferir_wheel dist/*.whl` (sai com 1 e lista o que falta).

- [ ] **Passo 1: Escrever o teste**

```python
# tests/scripts/test_conferir_wheel.py
import zipfile
from scripts.empacotamento.conferir_wheel import ARQUIVOS_OBRIGATORIOS, faltando_no_wheel

def test_aponta_arquivos_de_dados_ausentes(tmp_path):
    whl = tmp_path / "x.whl"
    with zipfile.ZipFile(whl, "w") as z:
        z.writestr("felixo_notion_mcp/__init__.py", "")
    assert faltando_no_wheel(whl) == list(ARQUIVOS_OBRIGATORIOS)

def test_wheel_completo_nao_falta_nada(tmp_path):
    whl = tmp_path / "x.whl"
    with zipfile.ZipFile(whl, "w") as z:
        for nome in ARQUIVOS_OBRIGATORIOS:
            z.writestr(nome, "")
    assert faltando_no_wheel(whl) == []
```

`ARQUIVOS_OBRIGATORIOS = ("felixo_notion_mcp/repositories/operations/migrations/0001_initial.py",
"felixo_notion_mcp/api/http/templates/tarefas.html", "felixo_notion_mcp/api/http/static/frontend/index.html",
"felixo_notion_mcp/api/http/static/css/app.css")`. Rode e veja falhar; implemente;
rode e veja passar (`2 passed`).

- [ ] **Passo 2: Lockfile e auditoria local**

```bash
uv lock && uv sync --locked --all-extras
uv export --frozen --all-extras --no-emit-project --no-hashes -o "$TMPDIR/requisitos-auditoria.txt"
uvx pip-audit -r "$TMPDIR/requisitos-auditoria.txt"
(cd front && npm audit --audit-level=high)
(cd front && npm run build) && uv build && uv run python -m scripts.empacotamento.conferir_wheel dist/*.whl
```

Esperado: `No known vulnerabilities found` e `found 0 vulnerabilities` no nível alto; o
conferidor sai com 0. Se `uv export` não aceitar alguma flag nesta versão do uv
(0.12.13 medida), confira com `uv export --help` e ajuste o comando aqui e no CI.
Vulnerabilidade encontrada: suba a versão mínima, refaça o lock e registre no `IA.md`
(Tarefa 10).

- [ ] **Passo 3: Workflow de CI**

```yaml
# .github/workflows/ci.yml
name: CI
on:
  push:
    branches: [main]
  pull_request:
jobs:
  python:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ["3.10", "3.11", "3.12", "3.13"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: python -m pip install uv==0.12.13
      - run: uv sync --locked --all-extras --python ${{ matrix.python-version }}
      - run: uv run ruff check .
      - run: uv run python -m pytest -q
  front:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: front
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "22"
          cache: npm
          cache-dependency-path: front/package-lock.json
      - run: npm ci
      - run: npm run lint
      - run: npm run build
      - run: npm audit --audit-level=high
  pacote:
    needs: front
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.13"
      - uses: actions/setup-node@v4
        with:
          node-version: "22"
      - run: python -m pip install uv==0.12.13
      - run: cd front && npm ci && npm run build
      - run: uv build
      - run: uv run --with-editable . python -m scripts.empacotamento.conferir_wheel dist/*.whl
      - run: uv export --frozen --all-extras --no-emit-project --no-hashes -o requisitos-auditoria.txt
      - run: uvx pip-audit -r requisitos-auditoria.txt
```

Não há workflow de release nem de deploy nesta etapa (Restrições globais).

- [ ] **Passo 4: Commit**

```bash
git add uv.lock .github scripts/empacotamento tests/scripts/test_conferir_wheel.py
git commit -m "chore: lockfile, CI em matriz de sistemas e conferência do wheel"
```

---

### Tarefa 9: Empacotamento nativo apontando para o pacote novo

**Arquivos:** modifica `scripts/empacotamento/build_native.py`, `scripts/empacotamento/native_entrypoint.py`, `src/felixo_notion_mcp/api/cli/versao.py`; teste `tests/api/cli/test_build_native.py`.

**Interfaces:**
- Produz: `versao.NOME_ARQUIVO_VERSAO_NATIVA = "felixo-notion-mcp-version.txt"`; dentro do executável, o arquivo de versão fica em `<_MEIPASS>/felixo_notion_mcp/api/cli/`.

- [ ] **Passo 1: Ajustar as expectativas do teste de build**

Em `test_build_native.py`, o comando montado por `construir_comando` precisa conter
`--copy-metadata felixo-notion-mcp`, `--collect-submodules felixo_notion_mcp` e
`--add-data <arquivo>{os.pathsep}felixo_notion_mcp/api/cli`. Os nomes de asset
(`notion-automacoes-<alvo>`) **não** mudam. Rode e veja falhar.

- [ ] **Passo 2: Implementar**

Troque os três argumentos do PyInstaller; `native_entrypoint.py` importa
`felixo_notion_mcp.api.cli.unificada.main`; `versao.ler_versao_embutida` procura em
`Path(_MEIPASS) / "felixo_notion_mcp" / "api" / "cli" / NOME_ARQUIVO_VERSAO_NATIVA`. Rode o teste e veja passar.

- [ ] **Passo 3: Build real e smoke (Linux nesta máquina)**

```bash
uv sync --locked --all-extras
uv run python -m scripts.empacotamento.build_native --target linux-x64 --version v0.6.0 --output "$TMPDIR/nativo"
uv run python -m scripts.empacotamento.smoke_native --executable "$TMPDIR/nativo/notion-automacoes-linux-x64" --version v0.6.0
"$TMPDIR/nativo/notion-automacoes-linux-x64" auth listar
```

Esperado: o smoke passa; `--version` responde `0.6.0`; `auth listar` responde sem traceback.
Windows e macOS ficam com a CI de release da etapa 4: registre isso como limite no `IA.md`.

- [ ] **Passo 4: Commit**

```bash
git add scripts/empacotamento src/felixo_notion_mcp/api/cli/versao.py tests/api/cli/test_build_native.py
git commit -m "fix: empacotamento nativo usa o pacote felixo_notion_mcp"
```

---

### Tarefa 10: Documentação viva

**Arquivos:** `docs/ia-archive/IA-*.md` (já movidos), `IA.md`, `README.md`, `CONTRIBUTING.md` (novo, a partir dos três), `.env.example` (união dos três, sem valores), `AGENTS.md`, `CLAUDE.md`, `docs/ARQUITETURA.md` (novo), `docs/MODULARIZACAO.md` (nota de substituição no topo), `docs/DISTRIBUICAO.md`, `docs/QUALIDADE.md`.

Cada passo abaixo é um commit separado, como manda a política de git.

- [ ] **Passo 1 (interno):** acrescente ao `IA.md` uma entrada datada "Etapa 1 do monolito": SHAs importados (Tarefa 2), contagens antes e depois, refinamentos sobre a spec (sobras não colidentes mantidas; `sync.py` aposentado em vez de movido, porque só sincronizava os módulos), assertivas que mudaram de propósito, limites (binário validado só em Linux). Atualize o "Estado atual". Commit: `docs: registrar a etapa 1 do monolito no IA.md`.
- [ ] **Passo 2 (interno, agentes):** reescreva `AGENTS.md` e `CLAUDE.md`. Saem `bootstrap.py`, `modules/`, `check-dev.py` e o roteamento por repositório; entra o roteamento por camada (tabela "o pedido mexe em… → `src/felixo_notion_mcp/<camada>/<arquivo>`", gerada a partir de `docs/ARQUITETURA.md`). O MODO USO fica igual. Commit: `docs: rotear agentes pelas camadas do monolito`.
- [ ] **Passo 3 (público):** `README.md` no Design System README (o que é, instalação pelo checkout com `python start_app.py`, comandos, mapa do repositório, contribuição como convite); `CONTRIBUTING.md` e `.env.example` unificados; `docs/ARQUITETURA.md` com as camadas e a tabela origem → destino da Tarefa 3. Commit: `docs: README e guia de arquitetura do monolito`.
- [ ] **Passo 4 (distribuição):** `docs/DISTRIBUICAO.md` explica que os pacotes publicados continuam `notion-automacoes`/`notion-starter`/`notion-workspace-app` até a etapa 4; `docs/MODULARIZACAO.md` ganha no topo a nota "substituído pela spec do monolito em 07/10/2026". Commit: `docs: registrar a transição de distribuição para o pacote único`.
- [ ] **Passo 5: verificação**

Run: `rg -n "bootstrap.py|check-dev.py|modules/notion-" README.md AGENTS.md CLAUDE.md docs/ARQUITETURA.md docs/DISTRIBUICAO.md` → nenhuma ocorrência fora de contexto histórico.

---

### Tarefa 11: Integrar no `main`, acompanhar a CI e renomear o repositório

- [ ] **Passo 1: Trazer o `main` e rodar o gate completo**

```bash
git fetch origin && git merge origin/main      # IA.md: conflito append-only → manter as duas entradas
uv sync --locked --all-extras && uv run ruff check . && uv run python -m pytest -q
(cd front && npm run lint && npm run build)
```

Esperado: tudo verde; contagem ≥ `1304 passed` mais os testes novos.

- [ ] **Passo 2: PR para a CI testar os três sistemas antes de entrar**

```bash
git push -u origin refactor/monolito
gh pr create --base main --title "refactor: monolito Felixo Notion MCP — etapa 1" --body-file <(printf "Implementa a etapa 1 da spec docs/superpowers/specs/2026-10-07-monolito-felixo-notion-mcp-design.md.\n")
gh pr checks --watch
```

Esperado: os 12 jobs `python`, `front` e `pacote` verdes. Falha: leia o log, corrija
na branch e repita. Falha só no Windows ou no macOS é bug desta etapa, não pendência.

- [ ] **Passo 3: Merge e limpeza da branch**

```bash
gh pr merge --merge --delete-branch
git switch main && git pull --ff-only && git branch -d refactor/monolito && git fetch --prune
gh run list --branch main --limit 1     # CI do main verde
```

- [ ] **Passo 4: Renomear o repositório (ação externa: confirmar com o mantenedor imediatamente antes)**

```bash
gh repo rename Felixo-Notion-MCP --repo Felipe-Alcantara/Automa-es-do-Notion --yes
git remote set-url origin https://github.com/Felipe-Alcantara/Felixo-Notion-MCP.git
gh api repos/Felipe-Alcantara/Automa-es-do-Notion --jq .full_name   # → Felipe-Alcantara/Felixo-Notion-MCP (redirecionamento)
git fetch origin && git status -sb
```

A pasta local **mantém** o nome `Automa-es-do-Notion` nesta etapa (spec 6.5): mudar
o nome quebraria a memória do Claude Code e o canvas "Tasks do Notion" no meio das
etapas seguintes. A troca da pasta fica para a etapa 4, junto com a migração de prompts.

---

## Autorrevisão

- **Cobertura da spec (etapa 1):**
  - histórico preservado → T2;
  - layout por camadas e tabela origem → destino → T3–T6;
  - pacote único, `0.6.0.dev0` e apelidos → T4–T6;
  - `start_app.py` único → T7;
  - scripts fora da raiz → T7;
  - `bootstrap`/`check-dev` aposentados e `doctor` → T7;
  - lockfile e auditoria → T8;
  - matriz multiplataforma → T8;
  - documentação viva e `ia-archive` → T10;
  - branch apagada e repositório renomeado → T11;
  - aceite (suítes verdes e retrato) → T5, T6, T11.
- **Fica para as etapas 2–4, de propósito:** `Contexto` explícito, registro de operações, modo hospedado, funções do blog e do AI Core, troca de `REPOSITORIO_GITHUB` e dos nomes de asset, workflows de release, pacotes de transição.
- **Consistência de nomes:** `retratar_parser`, `reescrever_codigo(..., em_migracao_django=)`, `montar_mapa`, `TABELA_MOVIMENTOS`, `UNIFICADOS`, `faltando_no_wheel` e `_garantir_src_no_path` são usados com a mesma assinatura em todas as tarefas.
