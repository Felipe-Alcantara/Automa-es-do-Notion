"""Testes do guarda que diz de onde vem o ``notion_starter``.

O guarda existe porque o modo de falha é silencioso: a CLI continua
funcionando com o starter baixado do GitHub enquanto as edições em
``modules/notion-starter`` não têm efeito nenhum. Testar aqui é testar
comportamento — o que a função conclui a partir de um ``find_spec``.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType, SimpleNamespace

RAIZ = Path(__file__).resolve().parent.parent


def _carregar_check_dev() -> ModuleType:
    """Importa ``check-dev.py``, cujo nome com hífen impede o import normal."""

    spec = importlib.util.spec_from_file_location("check_dev", RAIZ / "check-dev.py")
    assert spec and spec.loader
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


check_dev = _carregar_check_dev()


def _fingir_spec(monkeypatch, origem: str | None) -> None:
    """Faz ``find_spec("notion_starter")`` devolver a origem pedida."""

    resultado = None if origem is None else SimpleNamespace(origin=origem)
    monkeypatch.setattr(
        check_dev.importlib.util, "find_spec", lambda nome: resultado
    )


def test_reconhece_o_starter_editavel_de_modules(monkeypatch, tmp_path):
    modulos = tmp_path / "modules"
    origem = modulos / "notion-starter" / "src" / "notion_starter" / "__init__.py"
    origem.parent.mkdir(parents=True)
    origem.touch()
    _fingir_spec(monkeypatch, str(origem))

    assert check_dev.origem_do_starter(modulos).startswith("[OK]")


def test_avisa_quando_o_starter_vem_de_site_packages(monkeypatch, tmp_path):
    modulos = tmp_path / "modules"
    _fingir_spec(monkeypatch, "/usr/lib/python3/site-packages/notion_starter/__init__.py")

    aviso = check_dev.origem_do_starter(modulos)

    assert aviso.startswith("[AVISO]")
    # O aviso tem que dizer ONDE está a cópia errada; sem isso não é acionável.
    assert "site-packages" in aviso


def test_informa_quando_o_starter_nao_esta_instalado(monkeypatch, tmp_path):
    _fingir_spec(monkeypatch, None)

    assert check_dev.origem_do_starter(tmp_path / "modules").startswith("[INFO]")
