"""Texto de instalação e de atualização enquanto a distribuição não está no PyPI."""

from __future__ import annotations

import re

from felixo_notion_mcp.core.instalacao import (
    instrucao_de_atualizacao,
    instrucao_de_instalacao,
    raiz_e_checkout,
)

#: Qualquer pip/pipx/uv que instale ou atualize o nome da distribuição a partir de um índice.
INSTALA_PELO_NOME = re.compile(
    r"(?:pip3?|pipx|uv)\b[^\n]*\b(?:install|upgrade)\b[^\n]*felixo-notion-mcp"
)


def test_so_e_checkout_a_raiz_com_pyproject(tmp_path):
    assert raiz_e_checkout(tmp_path) is False
    (tmp_path / "pyproject.toml").write_text("[project]\n", encoding="utf-8")
    assert raiz_e_checkout(tmp_path) is True


def test_atualizacao_no_checkout_manda_git_pull_e_uv_sync():
    texto = instrucao_de_atualizacao(em_checkout=True)

    assert "git pull" in texto
    assert "uv sync --all-extras" in texto
    assert 'pip install -e ".[app]"' in texto
    assert "PyPI" in texto
    assert INSTALA_PELO_NOME.search(texto) is None


def test_atualizacao_fora_do_checkout_diz_que_nao_ha_distribuicao_publicada():
    texto = instrucao_de_atualizacao(em_checkout=False)

    assert "ainda não está publicada" in texto
    assert "checkout do código-fonte" in texto
    # Reaproveita a orientação de instalação, em vez de repetir o texto.
    assert instrucao_de_instalacao("app") in texto
    assert INSTALA_PELO_NOME.search(texto) is None
