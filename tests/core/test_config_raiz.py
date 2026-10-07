"""A raiz do checkout é calculada a partir de ``__file__``: a profundidade precisa acertar.

``core/config.py`` e ``core/workspaces.py`` derivam caminhos do lugar onde o arquivo mora.
Quando um arquivo muda de pasta, o ``parents[n]`` que servia antes passa a apontar para
outro lugar sem nenhum erro, então estes testes prendem o resultado, não a expressão.
"""

from __future__ import annotations

from pathlib import Path

import felixo_notion_mcp
from felixo_notion_mcp.api.cli import notion_tasks
from felixo_notion_mcp.core import config, workspaces

RAIZ_ESPERADA = Path(__file__).resolve().parents[2]


def test_repo_raiz_e_a_raiz_do_checkout():
    assert config.REPO_RAIZ == RAIZ_ESPERADA
    assert (config.REPO_RAIZ / "pyproject.toml").is_file()
    assert (config.REPO_RAIZ / "src" / "felixo_notion_mcp").is_dir()


def test_env_file_fica_na_raiz_do_checkout():
    assert config.ENV_FILE == RAIZ_ESPERADA / ".env"


def test_cli_grava_o_env_na_mesma_raiz_que_a_configuracao_le():
    assert notion_tasks.RAIZ == config.REPO_RAIZ


def test_store_legado_fica_ao_lado_do_pacote_de_topo():
    pasta_do_pacote = Path(felixo_notion_mcp.__file__).resolve().parent

    assert workspaces.ARQUIVO_LEGADO == pasta_do_pacote.parent / workspaces.ARQUIVO_NOME
