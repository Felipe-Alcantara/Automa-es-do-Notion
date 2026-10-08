#!/usr/bin/env python3
"""Abre, sem duplicar, as pendências da etapa 1 do monolito Felixo Notion MCP.

Uso:
    python3 scripts/notion/criar_pendencias_monolito_etapa_1.py --origem ID_DA_TASK_DA_ETAPA_1

O script cria no To Do List da HOME uma task por pendência que a etapa 1 deixou:
as etapas 2, 3 e 4 da spec, as ações que só o mantenedor pode fazer e os achados
das revisões que ficaram para depois. Cada título é procurado antes de criar, então
pode rodar de novo depois de uma falha de rede. Propriedades e corpo nascem na mesma
chamada ``notion-tasks criar``; as relações usam ``notion-tasks relacionar``, que é
idempotente, e o motivo de cada ligação vai para uma seção "Tarefas relacionadas" no
corpo das duas pontas, escrita uma vez só.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Any

PERFIL = "home-pessoal"
DATABASE_ID = "30296e2d-cd39-4cf3-8bbd-3fb2f53c0195"
PROJETO_AUTOMACOES = "38e91f95-497e-8165-a222-d9a5c1bf6467"  # Felipe-Alcantara/Felixo-Notion-MCP
AREA_PROJETOS = "1fe91f95-497e-802d-b069-dfc0f91d0634"
REPOSITORIO = "Felixo-Notion-MCP"

REPO_URL = "https://github.com/Felipe-Alcantara/Felixo-Notion-MCP"
SPEC_URL = (
    f"{REPO_URL}/blob/main/docs/superpowers/specs/2026-10-07-monolito-felixo-notion-mcp-design.md"
)
PLANO_URL = f"{REPO_URL}/blob/main/docs/superpowers/plans/2026-10-07-etapa-1-monolito.md"
ARQUITETURA_URL = f"{REPO_URL}/blob/main/docs/ARQUITETURA.md"
IA_URL = f"{REPO_URL}/blob/main/IA.md"
PR_URL = f"{REPO_URL}/pull/4"

# Tasks que já existiam antes da etapa 1 e que as novas destravam ou dependem.
TASK_RELEASE_PONTE = "3ed91f95-497e-816b-b138-c4853b31771d"
TASK_VALIDAR_4_SOS = "3db91f95-497e-81de-9e4c-f149754dfd1f"
TASK_CERTIFICADO = "3d191f95-497e-8124-bad4-ca675fc206e7"
TASK_DECISAO_STARTER = "3e991f95-497e-8193-a6dc-ecd37f8d5eec"

AGENTE = "Tasks do Notion"
MODELO = "Claude Code, Opus 5.5"
TITULO_ORIGEM = (
    "Felixo Notion MCP/Etapa 1 — juntar o hub e os três módulos num monolito por camadas"
)
SECAO_RELACOES = "## Tarefas relacionadas (etapa 1 do monolito)"


@dataclass(frozen=True)
class Tarefa:
    chave: str
    titulo: str
    etapa: str
    esforco: str
    prioridade: str
    tipos: str
    referencia: str
    corpo: str


@dataclass(frozen=True)
class Ligacao:
    a: str
    b: str
    coluna: str
    motivo: str


def executar(*argumentos: str) -> dict[str, Any]:
    """Roda ``notion-tasks --json`` no perfil da HOME e devolve o envelope."""

    resultado = subprocess.run(
        ["notion-tasks", "--json", "--perfil", PERFIL, *argumentos],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    try:
        resposta = json.loads(resultado.stdout)
    except json.JSONDecodeError as erro:
        detalhe = resultado.stderr.strip() or resultado.stdout.strip()
        raise RuntimeError(f"Saída não JSON de {argumentos[0]}: {detalhe}") from erro
    if resultado.returncode != 0 or not resposta.get("ok"):
        raise RuntimeError(json.dumps(resposta.get("erro", resposta), ensure_ascii=False))
    return resposta


def url_da_pagina(identificador: str) -> str:
    return f"https://app.notion.com/p/{identificador.replace('-', '')}"


def ids_por_titulo() -> dict[str, str]:
    dados = executar("linhas", DATABASE_ID).get("dados", {})
    linhas = dados.get("linhas", []) if isinstance(dados, dict) else []
    return {
        linha["titulo"]: linha["id"]
        for linha in linhas
        if isinstance(linha, dict)
        and isinstance(linha.get("titulo"), str)
        and isinstance(linha.get("id"), str)
    }


def cartao(origem: str) -> str:
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")
    fontes = (
        f"[spec]({SPEC_URL}) · [plano da etapa 1]({PLANO_URL}) · "
        f"[PR #4]({PR_URL}) · [IA.md]({IA_URL})"
    )
    return f"""---

### [{agora[-5:]}] Agente: {AGENTE} · Repositório: {REPOSITORIO}

- **Agente:** {AGENTE} ({MODELO})
- **Repositório / diretório:** {REPOSITORIO} — `{REPO_URL}`
- **Task de origem:** [{TITULO_ORIGEM}]({url_da_pagina(origem)})
- **Aberta em:** {agora}
- **Fontes:** {fontes}

"""


def garantir_tarefa(tarefa: Tarefa, origem: str, existentes: dict[str, str]) -> str:
    existente = existentes.get(tarefa.titulo)
    if existente:
        print(f"[pula] {tarefa.titulo} ({existente})")
        return existente
    resposta = executar(
        "criar",
        tarefa.titulo,
        "--status",
        tarefa.etapa,
        "--duracao",
        tarefa.esforco,
        "--area",
        AREA_PROJETOS,
        "--set",
        f"Prioridade={tarefa.prioridade}",
        "--set",
        f"Tipo={tarefa.tipos}",
        "--set",
        f"Repositório={REPOSITORIO}",
        "--set",
        f"Projeto={PROJETO_AUTOMACOES}",
        "--set",
        f"URL de referência={tarefa.referencia}",
        "--conteudo",
        cartao(origem) + tarefa.corpo + "\n---\n",
    )
    dados = resposta.get("dados", {})
    identificador = dados.get("id") if isinstance(dados, dict) else None
    if not isinstance(identificador, str):
        raise RuntimeError(f"A criação não devolveu o id: {resposta}")
    existentes[tarefa.titulo] = identificador
    print(f"[cria] {tarefa.titulo} ({identificador})")
    return identificador


def corpo_atual(identificador: str) -> str:
    dados = executar("conteudo", identificador).get("dados", {})
    markdown = dados.get("markdown") if isinstance(dados, dict) else None
    return markdown if isinstance(markdown, str) else ""


def escrever_relacionadas(
    identificador: str, ligacoes: list[tuple[str, str]], titulos: dict[str, str]
) -> None:
    """Acrescenta a seção de relações com link e motivo, uma vez só por página."""

    if SECAO_RELACOES in corpo_atual(identificador):
        print(f"[pula seção] {identificador}")
        return
    linhas = [SECAO_RELACOES, ""]
    for outra, motivo in ligacoes:
        nome = titulos.get(outra, outra)
        linhas.append(f"- [{nome}]({url_da_pagina(outra)}) — {motivo}")
    executar("escrever", identificador, "\n".join(linhas) + "\n")
    print(f"[seção] {identificador}")


def tarefas(origem: str) -> tuple[Tarefa, ...]:
    origem_url = url_da_pagina(origem)
    return (
        Tarefa(
            chave="etapa2",
            titulo=(
                "Felixo Notion MCP/Etapa 2 — núcleo com contexto explícito e registro único "
                "gerando MCP, CLI e REST, com as funções do blog e do AI Core"
            ),
            etapa="Em breve",
            esforco="Dias",
            prioridade="Alta",
            tipos="Feature,Débito técnico/Refatoração",
            referencia=SPEC_URL,
            corpo=f"""## Contexto

A [etapa 1]({origem_url}) juntou o hub e os três módulos num pacote único por camadas sem mudar
comportamento. A etapa 2 é a da spec (seções 3 e 8): é ela que dá às IAs **tudo o que a CLI faz
pelo MCP** e prepara o multiusuário. O mantenedor pediu para parar e avaliar antes de começar.

## O que a investigação mediu

- O MCP atual expõe **18** ferramentas `notion.*`; a CLI tem 59 subcomandos (retrato em
  `tests/contrato/retrato_cli.json`).
- Os serviços ainda leem configuração global: `services/ingestao.py`,
  `services/sincronizar_github.py` e `services/backups.py` usam `os.environ`; cerca de 18
  chamadas a `integrations.notion.criar_cliente` montam o cliente a partir do perfil da máquina.
- `services/relatorios_docx.py` faz HTTP (`urlopen`) fora de `integrations/`; `domain/tasks.py`
  importa `integrations.notion_client` (exceção registrada em `docs/ARQUITETURA.md`).
- `_servico_do_starter` (`api/cli/notion_tasks.py`) só existia para o starter do PyPI que podia não
  ter um serviço; no monolito perdeu o propósito (decisão 8 da etapa 1).
- O retrato não registra `set_defaults`, `allow_abbrev` nem qual função cada subcomando chama.

## Por que importa

Sem `Contexto` explícito não há servidor hospedado (etapa 3), e sem registro único a paridade
MCP × CLI continua manual.

## O que fazer

1. Ampliar o retrato da CLI (handler por subcomando, `set_defaults`) e gravar um retrato da
   lista de ferramentas MCP **antes** de gerar qualquer borda.
2. Introduzir `Contexto` (cliente, mapeamento de colunas, logger) e passar a todo caso de uso;
   remover `os.environ` de `domain/` e `services/` e o `urlopen` de `relatorios_docx`.
3. Criar o teste de arquitetura das camadas (spec 3.1).
4. Criar o registro `api/operations/` e gerar MCP, CLI e REST a partir dele (spec 3.2), com
   nomes sem ponto e conjuntos `essencial`/`completo`.
5. Portar as funções do Felixo Editor (`importar_artigo`, `registrar_publicacao`) e do AI Core
   (detecção semântica de colunas, API de data sources 2025-09-03), unificando os conversores de
   Markdown por testes de caracterização (spec 3.3 e 3.4).
6. Simplificar `_servico_do_starter` e suas 8 chamadas.

## Critério de aceite

Teste de paridade verde; retratos da CLI e do MCP batem; teste de arquitetura verde; medição contra
o workspace real antes de trocar a versão da API.

## Ponto de atenção

Escrever o plano da etapa 2 a partir da spec antes de qualquer código.

## Evidência de origem

[Spec]({SPEC_URL}) · [ARQUITETURA]({ARQUITETURA_URL}) · [PR #4]({PR_URL}).
""",
        ),
        Tarefa(
            chave="etapa3",
            titulo=(
                "Felixo Notion MCP/Etapa 3 — servidor MCP hospedado para qualquer pessoa, "
                "com OAuth do Notion, chave de integração e Railway"
            ),
            etapa="Entrada",
            esforco="Dias",
            prioridade="Alta",
            tipos="Feature,Infra/Deploy,Segurança",
            referencia=SPEC_URL,
            corpo=f"""## Contexto

Seção 4 da spec: o servidor hospedado que substitui o MCP oficial no claude.ai e no celular, aberto
a qualquer pessoa, decidido em 07/10/2026. Depende da etapa 2 (`Contexto` explícito).

## O que a investigação mediu

- O claude.ai exige OAuth com DCR, PKCE S256, refresh rotativo, `401` com `resource_metadata` e
  callback `https://claude.ai/api/mcp/auth_callback`
  ([documentação](https://claude.com/docs/connectors/building/authentication)).
- O Notion só exige revisão da integração pública para o Marketplace; a autorização direta não
  ([documentação](https://developers.notion.com/docs/authorization)).
- O SDK `mcp` 1.28 tem `OAuthAuthorizationServerProvider` e `AuthSettings`.

## O que fazer

1. Escrever o plano da etapa 3 a partir da spec.
2. Contas sem senha, conexões `oauth` e `chave`, chaves pessoais (hash), repasse da `ntn_` sem
   gravar nada, tokens do Notion cifrados no Postgres.
3. ASGI único: `/mcp`, rotas OAuth, Django, `/saude`; deploy por push no Railway com staging e
   produção.
4. Testes de isolamento (IDOR), de conformidade OAuth e de logs sem segredo.

## Critério de aceite

O conector funciona no claude.ai web e no celular por OAuth e por chave; o Claude Code funciona
por header; os testes de isolamento passam.

## Ponto de atenção

Bloqueada pelas decisões do mantenedor (integração pública, domínio/DNS, privacidade e termos).

## Evidência de origem

[Spec, seção 4]({SPEC_URL}).
""",
        ),
        Tarefa(
            chave="etapa4",
            titulo=(
                "Felixo Notion MCP/Etapa 4 — AI Core e Felixo Editor usando o monolito, "
                "pacote felixo-notion-mcp e ponte dos binários"
            ),
            etapa="Entrada",
            esforco="Dias",
            prioridade="Média",
            tipos="Feature,Infra/Deploy",
            referencia=SPEC_URL,
            corpo=f"""## Contexto

Seções 5 e 6 da spec. A etapa 1 deixou os pacotes publicados (`notion-automacoes`,
`notion-starter`, `notion-workspace-app`) e os assets `notion-automacoes-[alvo]` intactos; a troca
de nome e a migração de quem usa ficam aqui. Os três repositórios legados seguem ativos até a
Release-ponte.

## O que a investigação mediu

- O binário nativo Linux 0.6.0 foi construído e passou no smoke na etapa 1; Windows e macOS não.
- `mcp start` no binário nativo usa `sys.executable -m`, que não funciona em PyInstaller onefile —
  é bloqueante para embutir o binário no AI Core (task própria).
- A marca "Automações do Notion" ficou no banner do menu, no template e na descrição do
  `pyproject.toml` (decisão 14).
- `Django>=5.0` aceita versões sem suporte; subir para `>=5.2` antes da release.
- A pasta local do clone ainda se chama `Automa-es-do-Notion` (a memória do Claude Code e o canvas
  do AI Core dependem do caminho).

## O que fazer

1. Publicar `felixo-notion-mcp` 0.6.0, os pacotes de transição e a Release-ponte `v0.5.1` do
   `notion-tasks-cli`, na ordem da spec 6.4, antes de arquivar os três repositórios.
2. Migrar o AI Core (binário embutido, IPC inalterado) e o Felixo Editor (via pipx) para o MCP.
3. Trocar a marca e o nome da pasta local, migrando a memória do Claude Code e o canvas.
4. Transferir issues e arquivar `notion-starter`, `notion-tasks-cli` e `notion-workspace-app`.

## Critério de aceite

AI Core e Editor operando via monolito nos 3 sistemas; `pipx upgrade notion-automacoes` e a ponte
0.5.0 → 0.5.1 → 0.6.0 validados; os três repositórios legados arquivados com aviso.

## Evidência de origem

[Spec, seções 5 e 6]({SPEC_URL}).
""",
        ),
        Tarefa(
            chave="pypi",
            titulo=(
                "Felixo Notion MCP/Distribuição — registrar o nome felixo-notion-mcp no PyPI "
                "antes que outra pessoa registre"
            ),
            etapa="Assim que possível",
            esforco="Muitos minutos",
            prioridade="Alta",
            tipos="Segurança,Infra/Deploy",
            referencia="https://pypi.org/project/felixo-notion-mcp/",
            corpo="""## Contexto

O pacote do monolito se chama `felixo-notion-mcp`, mas o nome **não está registrado** no PyPI
(`https://pypi.org/pypi/felixo-notion-mcp/json` devolve 404). Um publicador pendente do Trusted
Publishing **não reserva** o nome.

## O que a investigação mediu

A revisão final da etapa 1 achou o launcher instalando e a CLI recomendando
`pip install felixo-notion-mcp`; o código foi corrigido para não indicar o nome enquanto ele não
for publicado. O risco que sobra é alguém registrar o nome antes.

## Por que importa

Quem registrar o nome primeiro passa a ter execução de código em quem seguir uma receita antiga.

## O que fazer (só o mantenedor)

1. Decidir: publicar já uma versão de reserva (por exemplo `0.6.0.dev0`) ou antecipar a `0.6.0`.
2. Cadastrar o publicador do Trusted Publishing para o repositório `Felixo-Notion-MCP`.
3. Publicar e confirmar a página do projeto no PyPI.

## Critério de aceite

`https://pypi.org/project/felixo-notion-mcp/` existe e pertence ao mantenedor.
""",
        ),
        Tarefa(
            chave="integracao",
            titulo=(
                "Felixo Notion MCP/Hospedado — criar a integração pública do Notion para o "
                "servidor MCP hospedado"
            ),
            etapa="Entrada",
            esforco="Poucas horas",
            prioridade="Média",
            tipos="Infra/Deploy",
            referencia="https://developers.notion.com/docs/authorization",
            corpo="""## Contexto

O servidor hospedado (etapa 3) aceita "Conectar com o Notion" por OAuth, que exige uma integração
**pública** no Notion com o redirect do servidor.

## O que fazer (só o mantenedor)

1. Criar a integração pública e cadastrar o redirect do servidor (o caminho final sai do plano da
   etapa 3, no domínio escolhido).
2. Preencher os campos que o formulário exigir (a documentação não lista todos; conferir na tela).
3. Guardar `client_id` e `client_secret` só nas variáveis do Railway.

## Critério de aceite

Integração pública criada; credenciais no Railway; redirect apontando para o domínio escolhido.
""",
        ),
        Tarefa(
            chave="dominio",
            titulo=(
                "Felixo Notion MCP/Hospedado — escolher o domínio e configurar o DNS do servidor "
                "MCP hospedado"
            ),
            etapa="Entrada",
            esforco="Muitos minutos",
            prioridade="Média",
            tipos="Infra/Deploy,Pesquisa/Decisão",
            referencia=SPEC_URL,
            corpo="""## Contexto

A spec propõe um subdomínio de `felixo.com.br` (por exemplo `mcp.felixo.com.br`) para o servidor
hospedado. O DNS desse domínio não é acessível ao agente.

## O que fazer (só o mantenedor)

1. Decidir o domínio (recomendação: `mcp.felixo.com.br`).
2. Criar o registro apontando para o serviço do Railway e confirmar o HTTPS.

## Critério de aceite

A rota `/saude` do domínio escolhido responde pelo Railway com certificado válido.
""",
        ),
        Tarefa(
            chave="lgpd",
            titulo=(
                "Felixo Notion MCP/Jurídico — aprovar a política de privacidade e os termos de uso "
                "do servidor MCP hospedado"
            ),
            etapa="Entrada",
            esforco="Poucas horas",
            prioridade="Média",
            tipos="Pesquisa/Decisão,Segurança",
            referencia=SPEC_URL,
            corpo="""## Contexto

O servidor hospedado é aberto a qualquer pessoa e guarda tokens de integração cifrados (spec 4.4).
Isso pede política de privacidade e termos de uso (LGPD) antes de abrir para terceiros.

## O que fazer

1. O agente redige o rascunho a partir do que o servidor guarda (conta, conexões, tokens cifrados,
   hashes, logs sem conteúdo) e do repasse sem gravação.
2. O mantenedor revisa e aprova o texto jurídico.

## Critério de aceite

Páginas `/privacidade` e `/termos` aprovadas pelo mantenedor e publicadas junto com a etapa 3.
""",
        ),
        Tarefa(
            chave="mcp_nativo",
            titulo=(
                "Felixo Notion MCP/Binário — fazer o mcp start funcionar no binário nativo "
                "(hoje usa sys.executable -m)"
            ),
            etapa="Em breve",
            esforco="Poucas horas",
            prioridade="Alta",
            tipos="Bug",
            referencia=REPO_URL,
            corpo="""## Contexto

Achado da revisão da Tarefa 9 da etapa 1, confirmado na revisão final.

## O que a investigação mediu

`_iniciar_mcp` em `api/cli/unificada.py` roda
`subprocess.call([sys.executable, "-m", "felixo_notion_mcp.api.mcp.server", ...])`. Num binário
PyInstaller onefile, `sys.executable` é o próprio binário e `-m` não é uma opção dele. O padrão já
existia no código antigo e não foi verificado num build real.

## Por que importa

A etapa 4 embute o binário no AI Core e inicia o MCP por ele (spec 5.1).

## O que fazer

1. Reproduzir num build Linux (`scripts/empacotamento/build_native.py`).
2. No binário congelado, iniciar o servidor no mesmo processo (ou por um subcomando interno), sem
   `-m`.
3. Acrescentar `mcp start` ao smoke do binário (`scripts/empacotamento/smoke_native.py`), com
   timeout e encerramento.

## Critério de aceite

O binário nativo responde `initialize` e `tools/list` por stdio no smoke.
""",
        ),
        Tarefa(
            chave="update_windows",
            titulo=(
                "Felixo Notion MCP/Binário — update nativo no Windows sem --json quebra com "
                "KeyError ao imprimir a troca agendada"
            ),
            etapa="Em breve",
            esforco="Muitos minutos",
            prioridade="Média",
            tipos="Bug",
            referencia=REPO_URL,
            corpo="""## Contexto

Achado na correção final da etapa 1 (pré-existente).

## O que a investigação mediu

No Windows, o resultado da troca agendada tem a chave `comando` mas não tem `versao_atual`; o ramo
de texto de `_imprimir` (`api/cli/unificada.py`) lê `versao_atual` e levanta `KeyError`. Com
`--json` funciona.

## O que fazer

1. Teste que simula o resultado `agendado` no ramo de texto e falha hoje.
2. Ajustar `_imprimir` para o formato do resultado nativo.

## Critério de aceite

O update sem `--json` imprime a troca agendada no Windows sem erro.
""",
        ),
        Tarefa(
            chave="guia_modelos",
            titulo=(
                "Felixo Notion MCP/CLI — tirar os exemplos de inventario, baixar-corpos e "
                "buscar-conteudo de dentro do retorno do comando modelos"
            ),
            etapa="Em breve",
            esforco="Muitos minutos",
            prioridade="Média",
            tipos="Bug",
            referencia=REPO_URL,
            corpo="""## Contexto

Achado da revisão da Tarefa 5 da etapa 1 (pré-existente no código da CLI).

## O que a investigação mediu

Em `api/cli/notion_tasks.py` (perto de `cmd_modelos`), os exemplos do guia de `inventario`,
`baixar-corpos` e `buscar-conteudo` estão dentro do dicionário que `cmd_modelos` devolve. Por isso
`modelos listar` devolve três chaves espúrias e `EXEMPLOS_GUIA` não tem esses três comandos.

## O que fazer

1. Teste que falha hoje: `modelos listar` não traz chaves de exemplos; `guia` mostra os três.
2. Mover os exemplos para `EXEMPLOS_GUIA`.

## Critério de aceite

Os dois testes passam e o retrato da CLI continua igual.
""",
        ),
        Tarefa(
            chave="testes_hermeticos",
            titulo=(
                "Felixo Notion MCP/Testes — tornar herméticos os testes do doctor e do start_app "
                "(rede, find_spec, .env em subprocessos)"
            ),
            etapa="Algum dia",
            esforco="Poucas horas",
            prioridade="Média",
            tipos="Testes",
            referencia=REPO_URL,
            corpo="""## Contexto

Achados das revisões das Tarefas 6, 7, da revisão final e das correções de Windows da etapa 1.

## O que a investigação mediu

- `tests/api/cli/test_doctor_origem.py` chama `diagnosticar()` sem isolar a rede
  (`api.notion.com:443`, portas 8000 e 5173) e o patch de `find_spec` vaza para outros checks.
- Subprocessos dos testes não herdam a guarda do `.env` do `tests/conftest.py`.
- O teste de subprocesso do `start_app` depende de instalação editável ou ausente.
- `tests/api/test_start_app.py` importa `rich` sem `importorskip`.
- Condições de skip de "notion-starter instalado" já não disparam.
- A guarda de subprocesso UTF-8 não vê `from subprocess import run`, apelidos nem `**kwargs`.

## O que fazer

1. Fixture autouse que isola `create_connection` e as portas no arquivo do doctor.
2. Repassar a guarda do `.env` aos subprocessos (variável de ambiente lida pelo carregador).
3. `importorskip` onde falta; remover os skips mortos; ampliar a guarda de subprocesso.

## Critério de aceite

A suíte passa sem rede e sem `.env` real, também com só `.[dev]` instalado.
""",
        ),
        Tarefa(
            chave="ci",
            titulo=(
                "Felixo Notion MCP/CI — endurecer o pipeline com cache, concurrency, actions por "
                "SHA e conferência do wheel mais estrita"
            ),
            etapa="Algum dia",
            esforco="Poucas horas",
            prioridade="Baixa",
            tipos="Infra/Deploy,Segurança",
            referencia=f"{REPO_URL}/blob/main/.github/workflows/ci.yml",
            corpo="""## Contexto

Achados das revisões das Tarefas 8 e final da etapa 1; nenhum bloqueia hoje.

## O que fazer

1. Cache do uv e do npm na matriz; `concurrency` cancelando execuções superadas.
2. Fixar as actions por SHA e a versão do `pip-audit` usada pelo `uvx`.
3. `conferir_wheel`: falhar quando o `index.html` não citar nenhum asset (mudança de `base` do
   Vite), conferir chunks de `import()` e tratar diretório/sdist sem traceback.
4. A varredura AST de receitas de instalação: pegar concatenação, `format`, atributo,
   `uv add`/`pipx run`.

## Critério de aceite

CI verde com os itens acima e tempo total menor que o atual.
""",
        ),
        Tarefa(
            chave="docs_antigos",
            titulo=(
                "Felixo Notion MCP/Docs — atualizar os guias antigos de docs/ que ainda citam "
                "server/, cli/ e notion_starter"
            ),
            etapa="Algum dia",
            esforco="Poucas horas",
            prioridade="Baixa",
            tipos="Documentação",
            referencia=ARQUITETURA_URL,
            corpo="""## Contexto

A etapa 1 reescreveu README, AGENTS, CLAUDE, ARQUITETURA, DISTRIBUICAO, QUALIDADE, INFRA e MCP.
Outros guias de `docs/` (`CONTRATOS.md`, `PLANO.md` e semelhantes) ainda descrevem os caminhos do
monorepo antigo.

## O que fazer

1. Procurar com `rg -n "server/|notion_starter|cli/notion_tasks" docs`, ignorando
   `docs/ia-archive/` e `docs/superpowers/`.
2. Atualizar cada guia para `src/felixo_notion_mcp/[camada]/` ou marcar como histórico.

## Critério de aceite

A busca acima só encontra menções históricas.
""",
        ),
        Tarefa(
            chave="launcher",
            titulo=(
                "Felixo Notion MCP/Launcher — unificar o teste de checkout e pedir confirmação "
                "antes de instalar dependências do front"
            ),
            etapa="Algum dia",
            esforco="Poucas horas",
            prioridade="Baixa",
            tipos="Melhoria",
            referencia=REPO_URL,
            corpo="""## Contexto

Achados das revisões da Tarefa 6 e final da etapa 1.

## O que a investigação mediu

- `api/launcher.py` e `core/config.py` decidem "é checkout?" olhando pastas diferentes; um
  `pyproject.toml` perdido em `site-packages` poria o launcher em modo checkout.
- `acao_iniciar_tudo` roda `npm install` sem perguntar (só no checkout).
- A sonda do `.venv` descarta o stderr; um `.venv` recusado faz o Instalar/Setup cair no Python do
  sistema.
- O launcher inicia o MCP por caminho de arquivo enquanto o resto usa `-m`; a docstring de
  `api/http/manage.py` contradiz o uso por caminho.

## O que fazer

1. Expor um predicado único de checkout em `core.config` e usá-lo no launcher.
2. Perguntar antes do `npm install`; mostrar a última linha do stderr da sonda.
3. Alinhar o modo de iniciar o MCP e a docstring do `manage.py`.

## Critério de aceite

Testes cobrindo os quatro pontos.
""",
        ),
    )


def ligacoes(ids: dict[str, str], origem: str) -> list[Ligacao]:
    filhas = (
        "etapa2", "etapa3", "etapa4", "pypi", "mcp_nativo", "update_windows",
        "guia_modelos", "testes_hermeticos", "ci", "docs_antigos", "launcher",
    )
    return [
        Ligacao(ids["etapa3"], ids["etapa2"], "Bloqueada por",
                "a etapa 3 precisa do Contexto explícito e do registro da etapa 2"),
        Ligacao(ids["etapa4"], ids["etapa3"], "Bloqueada por",
                "a etapa 4 publica e migra para o produto que a etapa 3 completa"),
        Ligacao(ids["etapa3"], ids["integracao"], "Bloqueada por",
                "o login com o Notion do servidor hospedado depende da integração pública"),
        Ligacao(ids["etapa3"], ids["dominio"], "Bloqueada por",
                "o servidor hospedado precisa do domínio e do HTTPS para o OAuth do claude.ai"),
        Ligacao(ids["etapa3"], ids["lgpd"], "Bloqueada por",
                "abrir o servidor a terceiros exige privacidade e termos aprovados"),
        Ligacao(ids["etapa4"], ids["pypi"], "Bloqueada por",
                "a etapa 4 publica felixo-notion-mcp, que precisa do nome registrado"),
        Ligacao(ids["etapa4"], ids["mcp_nativo"], "Bloqueada por",
                "o AI Core embute o binário e inicia o MCP por ele"),
        Ligacao(ids["etapa4"], TASK_RELEASE_PONTE, "Subtarefas relacionadas",
                "a Release-ponte v0.5.1 é o passo 4 da ordem de corte da etapa 4"),
        Ligacao(ids["etapa4"], TASK_VALIDAR_4_SOS, "Subtarefas relacionadas",
                "os binários de Windows e macOS da etapa 4 passam por essa validação"),
        Ligacao(ids["etapa4"], TASK_CERTIFICADO, "Subtarefas relacionadas",
                "o binário embutido no AI Core precisa estar assinado"),
        Ligacao(ids["etapa4"], TASK_DECISAO_STARTER, "Subtarefas relacionadas",
                "a última versão do notion-starter faz parte da transição da etapa 4"),
        Ligacao(ids["update_windows"], TASK_VALIDAR_4_SOS, "Subtarefas relacionadas",
                "mesmo caminho de update nativo no Windows; corrigir antes de validar"),
        *(
            Ligacao(origem, ids[chave], "Subtarefas relacionadas",
                    "aberta a partir dos registros e revisões da etapa 1 do monolito")
            for chave in filhas
        ),
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--origem", required=True, help="ID da task da etapa 1 do monolito")
    args = parser.parse_args(argv)
    origem = args.origem

    existentes = ids_por_titulo()
    ids = {tarefa.chave: garantir_tarefa(tarefa, origem, existentes) for tarefa in tarefas(origem)}
    titulos = {identificador: titulo for titulo, identificador in existentes.items()}

    por_pagina: dict[str, list[tuple[str, str]]] = {}
    for ligacao in ligacoes(ids, origem):
        executar("relacionar", ligacao.a, ligacao.b, "--coluna", ligacao.coluna)
        print(f"[relaciona] {ligacao.a} -{ligacao.coluna}-> {ligacao.b}")
        por_pagina.setdefault(ligacao.a, []).append((ligacao.b, ligacao.motivo))
        por_pagina.setdefault(ligacao.b, []).append((ligacao.a, ligacao.motivo))

    for identificador, lista_ligacoes in por_pagina.items():
        escrever_relacionadas(identificador, lista_ligacoes, titulos)

    print(json.dumps(ids, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as erro:
        print(f"Erro: {erro}", file=sys.stderr)
        raise SystemExit(1) from erro
