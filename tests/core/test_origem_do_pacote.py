"""De onde o pacote vem: a pergunta que o antigo ``check-dev.py`` fazia, agora no core.

``doctor`` e o Status do menu usam a mesma resposta. Aqui fica o comportamento dela, sem
depender de como o pacote foi instalado na máquina que roda a suíte.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import felixo_notion_mcp
from felixo_notion_mcp.core import origem
from felixo_notion_mcp.core.origem import origem_do_pacote


def _fingir_spec(monkeypatch, spec) -> None:
    monkeypatch.setattr(origem.importlib.util, "find_spec", lambda nome: spec)


def test_origem_aponta_para_a_pasta_do_pacote_carregado():
    atual = origem_do_pacote()

    assert atual is not None
    assert atual.pasta == Path(felixo_notion_mcp.__file__).resolve().parent
    assert str(atual.pasta) in atual.descricao()


def test_origem_do_checkout_tem_pyproject_dois_niveis_acima():
    atual = origem_do_pacote()

    assert atual is not None
    assert (atual.pasta.parents[1] / "pyproject.toml").is_file()
    assert atual.checkout_editavel is True
    assert atual.binario_nativo is False
    assert atual.descricao().endswith("checkout editável")


def test_origem_de_site_packages_nao_e_checkout(monkeypatch, tmp_path):
    pasta = tmp_path / "lib" / "site-packages" / "felixo_notion_mcp"
    pasta.mkdir(parents=True)
    _fingir_spec(monkeypatch, SimpleNamespace(origin=str(pasta / "__init__.py")))

    atual = origem_do_pacote()

    assert atual is not None
    assert atual.checkout_editavel is False
    assert atual.descricao() == str(pasta.resolve())


def test_origem_de_binario_nativo_nunca_se_diz_checkout(monkeypatch, tmp_path):
    (tmp_path / "pyproject.toml").write_text("[project]\n", encoding="utf-8")
    pasta = tmp_path / "src" / "felixo_notion_mcp"
    pasta.mkdir(parents=True)
    _fingir_spec(monkeypatch, SimpleNamespace(origin=str(pasta / "__init__.py")))
    monkeypatch.setattr(sys, "frozen", True, raising=False)

    atual = origem_do_pacote()

    assert atual is not None
    assert atual.checkout_editavel is False
    assert atual.binario_nativo is True
    assert atual.descricao().endswith("binário nativo")


def test_origem_numa_pasta_rasa_nao_quebra_a_busca_do_pyproject(monkeypatch):
    """``/felixo_notion_mcp`` não tem dois níveis acima; a resposta é "não é checkout"."""

    raiz = Path(Path.cwd().anchor)
    pacote = raiz / "felixo_notion_mcp" / "__init__.py"
    _fingir_spec(monkeypatch, SimpleNamespace(origin=str(pacote)))

    atual = origem_do_pacote()

    assert atual is not None
    assert atual.checkout_editavel is False


def test_origem_none_quando_o_pacote_nao_existe(monkeypatch):
    _fingir_spec(monkeypatch, None)

    assert origem_do_pacote() is None


def test_origem_none_quando_o_find_spec_falha(monkeypatch):
    def quebrado(nome):
        raise ValueError("felixo_notion_mcp.__spec__ is None")

    monkeypatch.setattr(origem.importlib.util, "find_spec", quebrado)

    assert origem_do_pacote() is None


def test_origem_usa_so_a_biblioteca_padrao():
    """Importar o módulo não pode puxar terceiros: o menu roda antes do Setup."""

    codigo = (
        "import sys\n"
        + "".join(
            f"sys.modules[{nome!r}] = None\n"
            for nome in ("requests", "docx", "django", "mcp", "rich", "questionary", "openpyxl")
        )
        + "from felixo_notion_mcp.core.origem import origem_do_pacote\n"
        + "print(origem_do_pacote().pasta.name)\n"
    )
    raiz = Path(__file__).resolve().parents[2]

    resultado = subprocess.run(
        [sys.executable, "-c", codigo],
        cwd=raiz,
        env={
            **os.environ,
            "PYTHONPATH": str(raiz / "src"),
            "PYTHONIOENCODING": "utf-8",
            "PYTHONUTF8": "1",
        },
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
        check=False,
    )

    assert resultado.returncode == 0, resultado.stderr
    assert resultado.stdout.strip() == "felixo_notion_mcp"
