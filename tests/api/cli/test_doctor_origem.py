"""O ``doctor`` diz de onde o pacote ``felixo_notion_mcp`` está sendo carregado.

Isto substitui o antigo ``check-dev.py``: o modo de falha que ele guardava (editar o
código e a CLI continuar executando uma cópia antiga instalada) só existia porque o
código vivia em três pacotes. No pacote único a pergunta que sobra é a mesma, numa
frase: "estou rodando o checkout ou uma instalação?".
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import felixo_notion_mcp
from felixo_notion_mcp.api.cli import unificada
from felixo_notion_mcp.api.cli.unificada import diagnosticar


def _check() -> dict:
    return {c["nome"]: c for c in diagnosticar()["checks"]}["felixo-notion-mcp"]


def test_doctor_mostra_de_onde_o_pacote_vem():
    checks = {c["nome"]: c for c in diagnosticar()["checks"]}
    detalhe = checks["felixo-notion-mcp"]["detalhe"]
    assert str(Path(felixo_notion_mcp.__file__).resolve().parent) in detalhe
    assert "checkout editável" in detalhe


def test_doctor_mostra_a_versao_junto_da_origem():
    assert unificada.versao_distribuicao() in _check()["detalhe"]


def test_doctor_nao_tem_mais_o_check_do_notion_starter():
    nomes = [c["nome"] for c in diagnosticar()["checks"]]
    assert "notion-starter" not in nomes
    assert nomes.count("felixo-notion-mcp") == 1


def test_doctor_origem_ok_quando_o_pacote_esta_no_checkout():
    check = _check()
    assert check["estado"] == "ok"
    assert check["opcional"] is False


def _fingir_pacote(monkeypatch, pasta: Path) -> None:
    spec = SimpleNamespace(origin=str(pasta / "__init__.py"))
    monkeypatch.setattr(unificada.importlib.util, "find_spec", lambda nome: spec)


def test_doctor_de_instalacao_nao_diz_checkout_editavel(monkeypatch, tmp_path):
    """Em ``site-packages`` não há ``pyproject.toml`` dois níveis acima."""

    pasta = tmp_path / "lib" / "python3.12" / "site-packages" / "felixo_notion_mcp"
    pasta.mkdir(parents=True)
    _fingir_pacote(monkeypatch, pasta)

    check = _check()

    assert check["estado"] == "ok"
    assert str(pasta.resolve()) in check["detalhe"]
    assert "checkout editável" not in check["detalhe"]


def test_doctor_reconhece_checkout_pelo_pyproject_dois_niveis_acima(monkeypatch, tmp_path):
    (tmp_path / "pyproject.toml").write_text("[project]\n", encoding="utf-8")
    pasta = tmp_path / "src" / "felixo_notion_mcp"
    pasta.mkdir(parents=True)
    _fingir_pacote(monkeypatch, pasta)

    check = _check()

    assert check["estado"] == "ok"
    assert str(pasta.resolve()) in check["detalhe"]
    assert "checkout editável" in check["detalhe"]


def test_doctor_binario_nativo_nao_se_diz_checkout(monkeypatch, tmp_path):
    """No binário congelado o pacote vive numa pasta temporária de extração."""

    (tmp_path / "pyproject.toml").write_text("[project]\n", encoding="utf-8")
    pasta = tmp_path / "src" / "felixo_notion_mcp"
    pasta.mkdir(parents=True)
    _fingir_pacote(monkeypatch, pasta)
    monkeypatch.setattr(unificada.sys, "frozen", True, raising=False)

    check = _check()

    assert check["estado"] == "ok"
    assert "checkout editável" not in check["detalhe"]
    assert "binário nativo" in check["detalhe"]


def test_doctor_erro_quando_o_pacote_nao_esta_instalado(monkeypatch):
    monkeypatch.setattr(unificada.importlib.util, "find_spec", lambda nome: None)

    check = _check()

    assert check["estado"] == "erro"
    assert "reinstale" in check["detalhe"]
