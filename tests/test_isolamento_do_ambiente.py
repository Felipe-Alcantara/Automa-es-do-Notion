"""A suíte nunca lê nem move arquivos reais de quem a executa.

Dois vazamentos reais, ambos invisíveis até alguém rodar a suíte numa máquina com
configuração de verdade:

- ``_migrar_legado`` usa ``shutil.move``. Com um store de perfis antigo (tokens incluídos) em
  um dos endereços de ``ARQUIVOS_LEGADOS``, qualquer teste que carregasse o store o moveria
  para uma pasta temporária do pytest, que some no fim da execução.
- ``notion_tasks`` e o servidor MCP chamam ``carregar_env_file()`` ao serem importados, e o
  checkout principal tem um ``.env`` com ``NOTION_TOKEN`` e ``NOTION_DATABASE_ID`` de verdade.
  Isso acontece na coleta, antes de qualquer fixture existir.

O ``conftest.py`` fecha os dois. Estes testes o prendem.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from felixo_notion_mcp.core import config, workspaces

SENTINELA = "FELIXO_TESTE_SENTINELA_ENV"


@pytest.fixture
def sentinela_limpa(monkeypatch):
    """Garante que a variável de teste não sobra no ``os.environ`` do processo depois."""

    monkeypatch.setenv(SENTINELA, "antes")
    monkeypatch.delenv(SENTINELA)
    return SENTINELA


def _escrever_env(pasta: Path, nome: str = ".env") -> Path:
    arquivo = pasta / nome
    arquivo.write_text(f"{SENTINELA}=veio-do-arquivo\n", encoding="utf-8")
    return arquivo


# --- Perfis legados ----------------------------------------------------------------


def test_nenhum_endereco_legado_de_perfis_vale_dentro_dos_testes():
    assert workspaces.ARQUIVOS_LEGADOS == ()


# --- .env do checkout --------------------------------------------------------------


def test_o_env_padrao_do_checkout_nao_chega_ao_ambiente(monkeypatch, tmp_path, sentinela_limpa):
    """Aponta o ``.env`` padrão para um checkout temporário e confere que ele é ignorado."""

    monkeypatch.setattr(config, "ENV_FILE", _escrever_env(tmp_path))

    config.carregar_env_file()
    config.carregar_config()

    assert SENTINELA not in os.environ


def test_o_env_padrao_tambem_e_ignorado_quando_passado_por_extenso(
    monkeypatch, tmp_path, sentinela_limpa
):
    env = _escrever_env(tmp_path)
    monkeypatch.setattr(config, "ENV_FILE", env)

    config.carregar_env_file(env)

    assert SENTINELA not in os.environ


def test_caminho_explicito_diferente_do_padrao_ainda_carrega(
    monkeypatch, tmp_path, sentinela_limpa
):
    padrao = tmp_path / "checkout"
    padrao.mkdir()
    monkeypatch.setattr(config, "ENV_FILE", padrao / ".env")
    explicito = _escrever_env(tmp_path, "outro.env")

    config.carregar_env_file(explicito)

    assert os.environ[SENTINELA] == "veio-do-arquivo"


def test_os_carregadores_de_import_usam_a_versao_protegida():
    """``notion_tasks`` e o servidor MCP carregam o ``.env`` ao serem importados (na coleta).

    ``from ... import carregar_env_file`` congela a função que existia naquele instante, então
    o ``conftest.py`` precisa instalar a proteção antes de qualquer teste ser importado.
    """

    from felixo_notion_mcp.api.cli import notion_tasks
    from felixo_notion_mcp.api.mcp import server

    assert getattr(config.carregar_env_file, "ignora_env_do_checkout", False) is True
    assert notion_tasks.carregar_env_file is config.carregar_env_file
    assert server.carregar_env_file is config.carregar_env_file
