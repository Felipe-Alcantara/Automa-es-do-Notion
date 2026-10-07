"""Testes da versão embutida no bundle PyInstaller."""

from __future__ import annotations

from pathlib import Path

from felixo_notion_mcp.api.cli import versao


def test_versao_embutida_so_e_lida_em_binario(monkeypatch, tmp_path):
    """O arquivo de build não deve alterar a versão durante o desenvolvimento."""

    arquivo_cli = tmp_path / "cli"
    arquivo_cli.mkdir()
    (arquivo_cli / versao.NOME_ARQUIVO_VERSAO_NATIVA).write_text("0.4.0\n", encoding="utf-8")
    monkeypatch.setattr(versao, "__file__", str(arquivo_cli / "versao.py"))
    monkeypatch.setattr(versao.sys, "frozen", False, raising=False)
    assert versao.ler_versao_embutida() is None

    monkeypatch.setattr(versao.sys, "frozen", True, raising=False)
    assert versao.ler_versao_embutida() == "0.4.0"


def test_versao_embutida_tolera_arquivo_ausente(monkeypatch, tmp_path):
    """Bundles antigos continuam usando o fallback de metadata."""

    monkeypatch.setattr(versao, "__file__", str(Path(tmp_path) / "versao.py"))
    monkeypatch.setattr(versao.sys, "frozen", True, raising=False)
    monkeypatch.setattr(versao.sys, "_MEIPASS", str(tmp_path), raising=False)
    assert versao.ler_versao_embutida() is None


def test_versao_embutida_no_layout_do_pacote_dentro_do_bundle(monkeypatch, tmp_path):
    """No bundle o builder grava em ``<_MEIPASS>/felixo_notion_mcp/api/cli/``.

    O ``--add-data`` do PyInstaller usa esse destino; ler de outro lugar devolveria ``None``
    e o binário passaria a se anunciar com a versão de desenvolvimento.
    """

    pasta_do_bundle = tmp_path / "felixo_notion_mcp" / "api" / "cli"
    pasta_do_bundle.mkdir(parents=True)
    (pasta_do_bundle / versao.NOME_ARQUIVO_VERSAO_NATIVA).write_text("0.6.0\n", encoding="utf-8")
    # ``__file__`` fora do bundle: só o caminho via ``_MEIPASS`` pode achar o arquivo.
    monkeypatch.setattr(versao, "__file__", str(tmp_path / "fora" / "versao.py"))
    monkeypatch.setattr(versao.sys, "frozen", True, raising=False)
    monkeypatch.setattr(versao.sys, "_MEIPASS", str(tmp_path), raising=False)

    assert versao.ler_versao_embutida() == "0.6.0"


def test_versao_embutida_ignora_o_layout_antigo_cli_na_raiz_do_bundle(monkeypatch, tmp_path):
    """``<_MEIPASS>/cli/`` era o destino do repositório antigo; o novo builder não o usa."""

    antigo = tmp_path / "cli"
    antigo.mkdir()
    (antigo / versao.NOME_ARQUIVO_VERSAO_NATIVA).write_text("9.9.9\n", encoding="utf-8")
    monkeypatch.setattr(versao, "__file__", str(tmp_path / "fora" / "versao.py"))
    monkeypatch.setattr(versao.sys, "frozen", True, raising=False)
    monkeypatch.setattr(versao.sys, "_MEIPASS", str(tmp_path), raising=False)

    assert versao.ler_versao_embutida() is None
