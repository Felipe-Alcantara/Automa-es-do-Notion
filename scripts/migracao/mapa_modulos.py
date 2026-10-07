"""Tabela de movimentos da migração para o monólito e o mapa de nomes antigo → novo.

Os três repositórios importados em `_importado/` viram um único pacote, `felixo_notion_mcp`,
organizado em camadas. Este módulo é a **fonte única** dessa reorganização:

- `TABELA_MOVIMENTOS` diz, arquivo por arquivo, para onde cada origem vai (ou que ela é
  removida);
- `montar_mapa` deriva dela o mapa de nomes pontuados antigo → novo, que
  `reescrever_imports` usa para corrigir os imports e `mover_para_camadas` aplica com
  `git mv`/`git rm`.

Os caminhos de `Movimento.origem` e `Movimento.destino` são relativos à raiz do repositório
e sempre com `/`. Uma origem que é diretório (`front`, `examples`, `.github`, `server/static`)
vale para todos os arquivos que contém.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from fnmatch import fnmatchcase

STARTER = "notion-starter"
CLI = "notion-tasks-cli"
APP = "notion-workspace-app"
MODULOS = (STARTER, CLI, APP)

RAIZ_IMPORTADO = "_importado"
PACOTE_NOVO = "felixo_notion_mcp"
RAIZ_NOVA = f"src/{PACOTE_NOVO}"


@dataclass(frozen=True)
class Movimento:
    """Um arquivo (ou diretório) importado e o que acontece com ele.

    `destino` vazio significa remover. Com `apenas_mapear=True` a origem é um *shim* ou uma
    duplicata: o arquivo é removido, mas seus nomes antigos entram no mapa apontando para
    `destino`, que é o módulo real e já tem de existir.
    """

    origem: str
    destino: str
    modulo: str
    apenas_mapear: bool = False

    def __post_init__(self) -> None:
        if self.apenas_mapear and not self.destino:
            raise ValueError(f"'apenas_mapear' exige um destino: {self.origem}")


@dataclass(frozen=True)
class RaizPython:
    """Uma pasta que o Python enxergava como raiz de importação no repositório antigo.

    O nome pontuado de um arquivo é o caminho dele a partir de `diretorio`, com `/` virando
    `.`, precedido por `prefixo` (também pontuado) quando houver.
    """

    diretorio: str
    prefixo: str


#: Raízes de importação dos três repositórios. O app tem duas: o repositório (`server.x`,
#: `start_app`) e a pasta `server` (`x`), porque o código dele importava dos dois jeitos.
RAIZES: tuple[RaizPython, ...] = (
    RaizPython(f"{RAIZ_IMPORTADO}/{STARTER}/src", ""),
    RaizPython(f"{RAIZ_IMPORTADO}/{CLI}", ""),
    RaizPython(f"{RAIZ_IMPORTADO}/{APP}", ""),
    RaizPython(f"{RAIZ_IMPORTADO}/{APP}/server", ""),
)

#: Destinos que dois módulos escrevem (o app repete `core/config.py` e `integrations/notion.py`
#: da CLI). Na tabela, o do app é `apenas_mapear`; a Tarefa 6 confere o diff antes de aplicar.
UNIFICADOS = frozenset(
    {
        f"{RAIZ_NOVA}/core/config.py",
        f"{RAIZ_NOVA}/integrations/notion.py",
    }
)

#: Destinos cujo conteúdo não se importa por nome pontuado: não entram no mapa.
DESTINOS_NAO_IMPORTAVEIS = ("tests/", "examples/", "docs/", "front/", ".github/")

#: Pastas de destino em que todo diretório com código Python vira pacote (`__init__.py`).
PASTAS_COM_PACOTES = (f"{RAIZ_NOVA}/", "scripts/")


class ConflitoDeNome(ValueError):
    """Dois movimentos com destinos diferentes gerariam o mesmo nome antigo no mapa."""


# --------------------------------------------------------------------------------------
# Nomes pontuados e mapa
# --------------------------------------------------------------------------------------


def _nome_pontuado(caminho: str, prefixo: str = "") -> str | None:
    """`a/b/c.py` → `a.b.c`; `a/b/__init__.py` → `a.b`; `None` se não for módulo Python."""
    if not caminho.endswith(".py"):
        return None
    partes = caminho[: -len(".py")].split("/")
    if partes[-1] == "__init__":
        partes = partes[:-1]
    if prefixo:
        partes = [*prefixo.split("."), *partes]
    return ".".join(partes) or None


def nome_antigo(origem: str, raiz: RaizPython) -> str | None:
    """Nome pontuado da origem visto desta raiz, ou `None` se ela não está sob a raiz."""
    base = raiz.diretorio.rstrip("/") + "/"
    if not origem.startswith(base):
        return None
    return _nome_pontuado(origem[len(base) :], raiz.prefixo)


def nome_novo(destino: str) -> str | None:
    """Nome pontuado do destino: sob `src/` conta a partir dele, fora conta da raiz do repo."""
    caminho = destino.removeprefix("src/")
    return _nome_pontuado(caminho)


def montar_mapa(movimentos: Sequence[Movimento], raizes: Sequence[RaizPython]) -> dict[str, str]:
    """Mapa nome pontuado antigo → novo, incluindo pacotes.

    Só entram arquivos `.py` com destino importável. Pacotes entram pelo `__init__.py`, de modo
    que `scripts`, que não tem `__init__.py` na origem e é nome de pacote nos dois lados, nunca
    é mapeado inteiro. Origens removidas (`destino` vazio) não geram nome. Levanta
    `ConflitoDeNome` se o mesmo nome antigo apontar para dois destinos diferentes.
    """
    mapa: dict[str, str] = {}
    fonte: dict[str, str] = {}
    for mov in movimentos:
        if not mov.destino or mov.destino.startswith(DESTINOS_NAO_IMPORTAVEIS):
            continue
        novo = nome_novo(mov.destino)
        if novo is None:
            continue
        for raiz in raizes:
            antigo = nome_antigo(mov.origem, raiz)
            if antigo is None or antigo == novo:
                continue
            if mapa.setdefault(antigo, novo) != novo:
                raise ConflitoDeNome(
                    f"O nome antigo '{antigo}' aponta para dois destinos: "
                    f"'{mapa[antigo]}' (de {fonte[antigo]}) e '{novo}' (de {mov.origem}). "
                    "Remova uma das origens da tabela ou marque-a como removida."
                )
            fonte.setdefault(antigo, mov.origem)
    return mapa


# --------------------------------------------------------------------------------------
# Regra de pasta dos testes
# --------------------------------------------------------------------------------------

#: Sufixo de origem para nomes de teste repetidos entre módulos.
SUFIXOS_DE_ORIGEM = {STARTER: "starter", CLI: "cli", APP: "app"}

#: (padrão do nome sem `.py`, pasta). A primeira regra que casar vence.
REGRAS_PASTA_DE_TESTE: tuple[tuple[str, str], ...] = (
    ("test_client*", "tests/integrations"),
    ("test_integrations_*", "tests/integrations"),
    ("test_services_*", "tests/services"),
    ("test_importacao", "tests/services"),
    ("test_ingestao_*", "tests/services"),
    ("test_inventory", "tests/services"),
    ("test_fonte_planilha", "tests/services"),
    ("test_anexos", "tests/services"),
    ("test_relatorios_docx_*", "tests/services"),
    ("test_content*", "tests/domain"),
    ("test_properties", "tests/domain"),
    ("test_readers", "tests/domain"),
    ("test_schema*", "tests/domain"),
    ("test_tasks", "tests/domain"),
    ("test_valores_br", "tests/domain"),
    ("test_git_historico", "tests/domain"),
    ("test_hierarquia_excecoes", "tests/core"),
    ("test_utils_ids", "tests/core"),
    ("test_workspaces", "tests/core"),
    ("test_prevencao_json_surrogate", "tests/core"),
    ("test_mcp_server", "tests/api/mcp"),
    ("test_api_*", "tests/api/http"),
    ("test_front", "tests/api/http"),
    ("test_start_app", "tests/api"),
)

#: Pasta dos testes que nenhuma regra acima pega: os "demais testes da CLI" ficam em
#: `tests/api/cli/`; os que sobrarem do starter (a versão do pacote) ficam em `tests/core/`.
PASTA_PADRAO_DE_TESTE = {STARTER: "tests/core", CLI: "tests/api/cli", APP: "tests/api"}

#: Testes de cada repositório importado (sem o `conftest.py`, que é removido).
TESTES_POR_MODULO: dict[str, tuple[str, ...]] = {
    STARTER: (
        "test_anexos.py", "test_client.py", "test_client_blocos.py",
        "test_client_movimento.py", "test_client_resiliencia.py",
        "test_client_retry_orientacao.py", "test_content.py",
        "test_content_aninhamento.py", "test_content_limites.py",
        "test_content_marcacao.py", "test_fonte_planilha.py", "test_git_historico.py",
        "test_hierarquia_excecoes.py", "test_importacao.py", "test_ingestao_chave.py",
        "test_inventory.py", "test_properties.py", "test_readers.py",
        "test_relatorios_docx_import_preguicoso.py", "test_schema.py",
        "test_schema_descricao.py", "test_services_backups.py",
        "test_services_classificacao.py", "test_services_conteudo_edicao.py",
        "test_services_conteudo_escrita.py", "test_services_conteudo_leitura_blocos.py",
        "test_services_conteudo_listar_linhas.py", "test_services_conteudo_seguranca.py",
        "test_services_copia_corpo.py", "test_services_estrutura_projeto.py",
        "test_services_historico_repositorios.py",
        "test_services_inventario_corpos_busca.py", "test_services_inventario_github.py",
        "test_services_modelos.py", "test_services_movimentacao.py",
        "test_services_relacoes.py", "test_services_relatorios_diarios.py",
        "test_services_relatorios_docx.py", "test_services_reordenacao.py",
        "test_services_schema.py", "test_tasks.py", "test_utils_ids.py",
        "test_valores_br.py", "test_versao.py",
    ),
    CLI: (
        "test_atualizacao_nativa.py", "test_build_native.py", "test_cli_acervo.py",
        "test_cli_copiar_corpo.py", "test_cli_criar_database.py", "test_cli_modelos.py",
        "test_cli_mover_pagina.py", "test_cli_notion_tasks.py", "test_cli_preflight.py",
        "test_cli_remover_coluna.py", "test_cli_schema_e_relacoes.py",
        "test_cli_status_validation.py", "test_cli_unificada.py",
        "test_integration_status_validation.py", "test_integrations_github.py",
        "test_prevencao_json_surrogate.py", "test_pyproject.py",
        "test_services_conteudo.py", "test_services_inventario_github.py",
        "test_services_preflight.py", "test_services_propriedades.py", "test_versao.py",
        "test_workspaces.py",
    ),
    APP: (
        "test_api_tarefas.py", "test_front.py", "test_integrations_github.py",
        "test_integrations_openrouter.py", "test_mcp_server.py",
        "test_services_clonagem.py", "test_services_conteudo.py",
        "test_services_exploracao.py", "test_services_ia.py", "test_services_ingestao.py",
        "test_services_inventario_github.py", "test_services_normalizacao.py",
        "test_services_projetos.py", "test_services_sincronizar.py",
        "test_services_tarefas.py", "test_start_app.py",
    ),
}  # fmt: skip

#: Nomes de teste que aparecem em mais de um módulo e por isso ganham sufixo de origem.
NOMES_DE_TESTE_REPETIDOS = frozenset(
    nome
    for nome, vezes in Counter(
        nome for nomes in TESTES_POR_MODULO.values() for nome in nomes
    ).items()
    if vezes > 1
)


def pasta_do_teste(nome: str, modulo: str) -> str:
    """Pasta de destino de um teste (`test_x.py`), pelas regras de camada."""
    base = nome.removesuffix(".py")
    for padrao, pasta in REGRAS_PASTA_DE_TESTE:
        if fnmatchcase(base, padrao):
            return pasta
    return PASTA_PADRAO_DE_TESTE[modulo]


def destino_do_teste(modulo: str, nome: str) -> str:
    """Caminho de destino de um teste; nome repetido entre módulos recebe sufixo de origem."""
    pasta = pasta_do_teste(nome, modulo)
    if nome in NOMES_DE_TESTE_REPETIDOS:
        nome = f"{nome.removesuffix('.py')}_{SUFIXOS_DE_ORIGEM[modulo]}.py"
    return f"{pasta}/{nome}"


# --------------------------------------------------------------------------------------
# Tabela de movimentos
# --------------------------------------------------------------------------------------


def _origem(modulo: str, relativo: str) -> str:
    return f"{RAIZ_IMPORTADO}/{modulo}/{relativo}"


def _arquivos(
    modulo: str,
    pasta_origem: str,
    nomes: Sequence[str],
    pasta_destino: str,
    *,
    apenas_mapear: bool = False,
) -> list[Movimento]:
    """Um movimento por nome: `pasta_origem/nome` → `pasta_destino/nome` (ou removido)."""
    prefixo = f"{pasta_origem}/" if pasta_origem else ""
    return [
        Movimento(
            _origem(modulo, f"{prefixo}{nome}"),
            f"{pasta_destino}/{nome}" if pasta_destino else "",
            modulo,
            apenas_mapear,
        )
        for nome in nomes
    ]


def _um(modulo: str, relativo: str, destino: str, *, apenas_mapear: bool = False) -> Movimento:
    return Movimento(_origem(modulo, relativo), destino, modulo, apenas_mapear)


def _removidos(modulo: str, relativos: Sequence[str]) -> list[Movimento]:
    return [_um(modulo, relativo, "") for relativo in relativos]


def _testes(modulo: str) -> list[Movimento]:
    return [
        _um(modulo, f"tests/{nome}", destino_do_teste(modulo, nome))
        for nome in TESTES_POR_MODULO[modulo]
    ]


def _ia(modulo: str) -> Movimento:
    return _um(modulo, "IA.md", f"docs/ia-archive/IA-{modulo}.md")


#: Arquivos de projeto que cada repositório importado tem e que a raiz do monólito substitui.
_ARQUIVOS_DE_PROJETO = (
    ".editorconfig",
    ".env.example",
    ".github",
    ".gitignore",
    "AGENTS.md",
    "CONTRIBUTING.md",
    "LICENSE",
    "QUALIDADE.md",
    "README.md",
    "pyproject.toml",
    "tests/conftest.py",
)

_SERVICOS_DO_STARTER = (
    "__init__.py", "anexos.py", "backups.py", "busca_conteudo.py", "classificacao.py",
    "clonagem.py", "conteudo.py", "copia_corpo.py", "corpos.py", "estrutura_projeto.py",
    "exploracao.py", "historico_repositorios.py", "ia.py", "importacao.py", "ingestao.py",
    "inventario_github.py", "inventario_workspace.py", "modelos.py", "movimentacao.py",
    "normalizacao.py", "projetos.py", "relacoes.py", "relatorios_diarios.py",
    "relatorios_docx.py", "reordenacao.py", "schema.py", "sincronizar_github.py",
    "tarefas.py",
)  # fmt: skip

#: Serviços da CLI que são só um reexport (21 linhas) do serviço de mesmo nome do starter.
_SHIMS_DE_SERVICO_DA_CLI = (
    "clonagem.py", "conteudo.py", "estrutura_projeto.py", "exploracao.py", "ia.py",
    "ingestao.py", "inventario_github.py", "normalizacao.py", "projetos.py",
    "reordenacao.py", "schema.py", "sincronizar_github.py", "tarefas.py",
)  # fmt: skip

#: Idem para o app.
_SHIMS_DE_SERVICO_DO_APP = (
    "clonagem.py", "conteudo.py", "exploracao.py", "ia.py", "ingestao.py",
    "inventario_github.py", "normalizacao.py", "projetos.py", "sincronizar_github.py",
    "tarefas.py",
)  # fmt: skip


def _movimentos_do_starter() -> list[Movimento]:
    src = "src/notion_starter"
    novo = RAIZ_NOVA
    return [
        _um(STARTER, f"{src}/__init__.py", f"{novo}/__init__.py"),
        _um(STARTER, f"{src}/client.py", f"{novo}/integrations/notion_client.py"),
        *_arquivos(STARTER, src, ("github.py", "openrouter.py"), f"{novo}/integrations"),
        *_arquivos(
            STARTER,
            src,
            (
                "properties.py",
                "readers.py",
                "content.py",
                "schema.py",
                "tasks.py",
                "valores_br.py",
                "git_historico.py",
            ),
            f"{novo}/domain",
        ),
        _um(STARTER, f"{src}/inventory.py", f"{novo}/services/inventory.py"),
        *_arquivos(STARTER, f"{src}/services", _SERVICOS_DO_STARTER, f"{novo}/services"),
        *_arquivos(
            STARTER,
            src,
            ("constants.py", "exceptions.py", "logging.py", "utils.py"),
            f"{novo}/core",
        ),
        _um(STARTER, "examples", "examples"),
        *_testes(STARTER),
        _ia(STARTER),
        *_removidos(STARTER, _ARQUIVOS_DE_PROJETO),
    ]


def _movimentos_da_cli() -> list[Movimento]:
    novo = RAIZ_NOVA
    return [
        *_arquivos(
            CLI,
            "cli",
            (
                "__init__.py",
                "__main__.py",
                "atualizacao_nativa.py",
                "erros.py",
                "notion_tasks.py",
                "unificada.py",
                "versao.py",
            ),
            f"{novo}/api/cli",
        ),
        *_arquivos(CLI, "core", ("config.py", "workspaces.py"), f"{novo}/core"),
        _um(CLI, "core/__init__.py", f"{novo}/core/__init__.py", apenas_mapear=True),
        _um(CLI, "integrations/notion.py", f"{novo}/integrations/notion.py"),
        *_arquivos(
            CLI,
            "integrations",
            ("__init__.py", "github.py", "openrouter.py"),
            f"{novo}/integrations",
            apenas_mapear=True,
        ),
        *_arquivos(CLI, "services", ("preflight.py", "propriedades.py"), f"{novo}/services"),
        *_arquivos(
            CLI,
            "services",
            ("__init__.py", *_SHIMS_DE_SERVICO_DA_CLI),
            f"{novo}/services",
            apenas_mapear=True,
        ),
        *_arquivos(
            CLI,
            "scripts",
            ("build_native.py", "native_entrypoint.py", "smoke_native.py"),
            "scripts/empacotamento",
        ),
        _um(CLI, "start_app.py", ""),
        *_testes(CLI),
        _ia(CLI),
        *_removidos(CLI, _ARQUIVOS_DE_PROJETO),
    ]


def _movimentos_do_app() -> list[Movimento]:
    novo = RAIZ_NOVA
    return [
        _um(APP, "server/__init__.py", f"{novo}/api/http/__init__.py", apenas_mapear=True),
        _um(APP, "server/mcp_server.py", f"{novo}/api/mcp/server.py"),
        *_arquivos(
            APP,
            "server/config",
            ("__init__.py", "asgi.py", "settings.py", "urls.py", "wsgi.py"),
            f"{novo}/api/http/config",
        ),
        *_arquivos(
            APP,
            "server/api",
            ("__init__.py", "apps.py", "serializers.py", "urls.py", "views.py"),
            f"{novo}/api/http/rest",
        ),
        _um(APP, "server/manage.py", f"{novo}/api/http/manage.py"),
        _um(APP, "server/templates", f"{novo}/api/http/templates"),
        _um(APP, "server/static", f"{novo}/api/http/static"),
        *_arquivos(
            APP,
            "server/operations",
            (
                "__init__.py",
                "apps.py",
                "models.py",
                "migrations/__init__.py",
                "migrations/0001_initial.py",
            ),
            f"{novo}/repositories/operations",
        ),
        # Duplicatas do que a CLI já escreve (Tarefa 6 confere o diff antes de aplicar).
        _um(APP, "server/core/config.py", f"{novo}/core/config.py", apenas_mapear=True),
        _um(
            APP,
            "server/integrations/notion.py",
            f"{novo}/integrations/notion.py",
            apenas_mapear=True,
        ),
        # Shims e pacotes que só reexportam.
        _um(APP, "server/core/__init__.py", f"{novo}/core/__init__.py", apenas_mapear=True),
        *_arquivos(
            APP,
            "server/integrations",
            ("__init__.py", "github.py", "openrouter.py"),
            f"{novo}/integrations",
            apenas_mapear=True,
        ),
        *_arquivos(
            APP,
            "server/services",
            ("__init__.py", *_SHIMS_DE_SERVICO_DO_APP),
            f"{novo}/services",
            apenas_mapear=True,
        ),
        _um(APP, "start_app.py", f"{novo}/api/launcher.py"),
        _um(APP, "front", "front"),
        *_testes(APP),
        _ia(APP),
        *_removidos(APP, (*_ARQUIVOS_DE_PROJETO, "requirements.txt")),
    ]


TABELA_MOVIMENTOS: tuple[Movimento, ...] = (
    *_movimentos_do_starter(),
    *_movimentos_da_cli(),
    *_movimentos_do_app(),
)


def movimentos_do_modulo(
    modulo: str, movimentos: Sequence[Movimento] = TABELA_MOVIMENTOS
) -> list[Movimento]:
    """Movimentos de um dos repositórios importados, na ordem da tabela."""
    return [mov for mov in movimentos if mov.modulo == modulo]


# --------------------------------------------------------------------------------------
# Pacotes novos
# --------------------------------------------------------------------------------------


def pacotes_a_criar(movimentos: Sequence[Movimento]) -> list[str]:
    """`__init__.py` que as pastas de destino dos movimentos reais precisam e ninguém traz.

    Cada pasta que recebe um `.py` (e as pastas acima, até a raiz do pacote) vira pacote. Pastas
    só de dados (`templates`, `static`) não entram. O que um movimento real já escreve como
    `__init__.py` não é repetido; se o arquivo já existe em disco, quem aplica o ignora.
    """
    trazidos = {mov.destino for mov in movimentos if mov.destino and not mov.apenas_mapear}
    pastas: set[str] = set()
    for destino in trazidos:
        if not destino.endswith(".py") or not destino.startswith(PASTAS_COM_PACOTES):
            continue
        pasta = destino.rpartition("/")[0]
        while pasta and pasta != "src":
            pastas.add(pasta)
            pasta = pasta.rpartition("/")[0]
    inits = {f"{pasta}/__init__.py" for pasta in pastas}
    return sorted(inits - trazidos)


def destinos_conhecidos(movimentos: Sequence[Movimento] = TABELA_MOVIMENTOS) -> frozenset[str]:
    """Todo destino que algum movimento real ou algum pacote novo passa a ter."""
    reais = {mov.destino for mov in movimentos if mov.destino and not mov.apenas_mapear}
    return frozenset(reais | set(pacotes_a_criar(movimentos)))


def cobre(mov: Movimento, arquivo: str) -> bool:
    """Diz se o movimento vale para o arquivo: é a própria origem ou um diretório que o contém."""
    return arquivo == mov.origem or arquivo.startswith(f"{mov.origem}/")


def mapa_da_tabela() -> dict[str, str]:
    """Mapa antigo → novo da tabela real (atalho usado pelos scripts de linha de comando)."""
    return montar_mapa(TABELA_MOVIMENTOS, RAIZES)
