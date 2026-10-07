"""A raiz do checkout é calculada a partir de ``__file__``: a profundidade precisa acertar.

``core/config.py`` e ``core/workspaces.py`` derivam caminhos do lugar onde o arquivo mora.
Quando um arquivo muda de pasta, o ``parents[n]`` que servia antes passa a apontar para
outro lugar sem nenhum erro, então estes testes prendem o resultado, não a expressão.
"""

from __future__ import annotations

import importlib.util
import sys
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


# --- Binário nativo (PyInstaller onefile) -----------------------------------------
#
# No binário, ``__file__`` mora em ``<_MEIPASS>/felixo_notion_mcp/core/config.py``. Subir
# ``parents[3]`` dali sai da pasta privada de extração e cai na pasta que a contém (no Linux,
# a pasta temporária do sistema, que qualquer usuário local escreve). Como o ``.env`` é lido
# e gravado a partir de ``REPO_RAIZ``, um ``.env`` plantado ali seria carregado a cada
# execução. Antes da reorganização a raiz era a própria ``_MEIPASS``.


def _congelar(monkeypatch, meipass: Path | None) -> None:
    """Simula o PyInstaller: ``sys.frozen`` e, quando há, ``sys._MEIPASS``."""

    monkeypatch.setattr(sys, "frozen", True, raising=False)
    if meipass is None:
        monkeypatch.delattr(sys, "_MEIPASS", raising=False)
    else:
        monkeypatch.setattr(sys, "_MEIPASS", str(meipass), raising=False)


def _carregar_copia(monkeypatch, caminho: Path, nome: str):
    """Executa o arquivo de novo sob outro nome, para observar o que ele resolve no import.

    Uma cópia, e não ``importlib.reload``, para não mexer no módulo que o resto da suíte
    (e ``notion_tasks.RAIZ``) já importou.
    """

    spec = importlib.util.spec_from_file_location(nome, caminho)
    assert spec is not None and spec.loader is not None
    modulo = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, nome, modulo)
    spec.loader.exec_module(modulo)
    return modulo


def test_binario_usa_a_pasta_privada_de_extracao_como_raiz(monkeypatch, tmp_path):
    meipass = tmp_path / "_MEI123"
    meipass.mkdir()
    _congelar(monkeypatch, meipass)

    assert config._raiz_do_repositorio() == meipass


def test_binario_resolve_env_e_raiz_dentro_da_pasta_privada_no_import(monkeypatch, tmp_path):
    meipass = tmp_path / "_MEI123"
    meipass.mkdir()
    _congelar(monkeypatch, meipass)

    copia = _carregar_copia(monkeypatch, Path(config.__file__), "config_congelado")

    assert copia.REPO_RAIZ == meipass
    assert copia.ENV_FILE == meipass / ".env"
    # A pasta que contém a de extração (a temporária do sistema) nunca pode virar a raiz.
    assert copia.ENV_FILE.parent != tmp_path


def test_binario_sem_meipass_nao_sobe_alem_da_pasta_do_pacote(monkeypatch):
    _congelar(monkeypatch, None)

    pasta_do_pacote = Path(felixo_notion_mcp.__file__).resolve().parent

    assert config._raiz_do_repositorio() == pasta_do_pacote.parent


def test_fora_do_binario_meipass_perdido_no_ambiente_e_ignorado(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "frozen", False, raising=False)
    monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)

    assert config._raiz_do_repositorio() == RAIZ_ESPERADA


def test_store_legado_no_binario_tambem_fica_na_pasta_privada(monkeypatch, tmp_path):
    """O ``parents[2]`` do store legado já cai em ``_MEIPASS``: aqui só se confere."""

    meipass = tmp_path / "_MEI123"
    pasta_core = meipass / "felixo_notion_mcp" / "core"
    pasta_core.mkdir(parents=True)
    (pasta_core / "workspaces.py").write_text(
        Path(workspaces.__file__).read_text(encoding="utf-8"), encoding="utf-8"
    )

    copia = _carregar_copia(monkeypatch, pasta_core / "workspaces.py", "workspaces_congelado")

    assert copia.ARQUIVO_LEGADO == meipass / workspaces.ARQUIVO_NOME
