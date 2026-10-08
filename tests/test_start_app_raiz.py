"""Testes do ``start_app.py`` da raiz, a porta de entrada única do checkout.

O arquivo roda num Python sem nada instalado (nem ``requests``, nem ``rich``, nem
o próprio pacote). Por isso só a biblioteca padrão pode aparecer nele, e o que ele
faz é achar ``src/`` e chamar o menu que vive em ``felixo_notion_mcp.api.launcher``.
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import textwrap
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]

TERCEIROS = ("requests", "docx", "django", "mcp", "rich", "questionary", "openpyxl")


def _carregar():
    spec = importlib.util.spec_from_file_location("start_app_raiz", RAIZ / "start_app.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _ambiente_sem_pythonpath() -> dict[str, str]:
    """Ambiente do filho sem nada que ajude a achar o pacote."""

    ambiente = {chave: valor for chave, valor in os.environ.items() if chave != "PYTHONPATH"}
    # O filho escreve UTF-8 e o pai o decodifica como UTF-8 (no Windows o padrão seria cp1252).
    ambiente.update(PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
    return ambiente


def test_start_app_raiz_acha_src_sem_instalacao(monkeypatch):
    mod = _carregar()
    monkeypatch.setattr(sys, "path", [p for p in sys.path if not p.endswith("src")])
    monkeypatch.setattr(mod.importlib.util, "find_spec", lambda nome: None)
    assert mod._garantir_src_no_path(RAIZ) is True
    assert str(RAIZ / "src") in sys.path


def test_start_app_raiz_nao_mexe_no_path_quando_instalado():
    assert _carregar()._garantir_src_no_path(RAIZ) is False


def test_start_app_raiz_nao_insere_pasta_src_que_nao_existe(monkeypatch, tmp_path):
    """Um ``start_app.py`` copiado para fora do checkout não inventa caminho."""

    mod = _carregar()
    caminho_antes = list(sys.path)
    monkeypatch.setattr(mod.importlib.util, "find_spec", lambda nome: None)

    assert mod._garantir_src_no_path(tmp_path) is False
    assert sys.path == caminho_antes


def test_start_app_raiz_nao_duplica_src_no_path(monkeypatch):
    mod = _carregar()
    src = str(RAIZ / "src")
    monkeypatch.setattr(sys, "path", [src])
    monkeypatch.setattr(mod.importlib.util, "find_spec", lambda nome: None)

    assert mod._garantir_src_no_path(RAIZ) is False
    assert sys.path == [src]


def test_start_app_raiz_so_importa_biblioteca_padrao():
    """O arquivo é lido por um Python sem instalação: nada de terceiros no topo."""

    import ast

    arvore = ast.parse((RAIZ / "start_app.py").read_text(encoding="utf-8"))
    nomes: set[str] = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            nomes.update(alias.name.split(".")[0] for alias in no.names)
        elif isinstance(no, ast.ImportFrom) and no.level == 0 and no.module:
            nomes.add(no.module.split(".")[0])

    permitidos = set(sys.stdlib_module_names) | {"felixo_notion_mcp"}
    assert nomes <= permitidos, f"importa fora da biblioteca padrão: {sorted(nomes - permitidos)}"


def test_start_app_raiz_chega_ao_launcher_sem_nenhum_terceiro(tmp_path):
    """Sem o pacote no ``sys.path`` e sem terceiros, o menu ainda é alcançável."""

    codigo = textwrap.dedent(
        """
        import importlib.util
        import sys
        from pathlib import Path

        raiz = Path(sys.argv[1])
        for nome in sys.argv[2:]:
            sys.modules[nome] = None

        # Tira do caminho tudo o que serviria o pacote (o `.pth` do modo editável
        # e o diretório de trabalho), como num Python recém-baixado.
        src = (raiz / "src").resolve()
        sys.path[:] = [p for p in sys.path if Path(p or ".").resolve() != src]

        spec = importlib.util.spec_from_file_location("start_app_raiz", raiz / "start_app.py")
        modulo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modulo)

        assert importlib.util.find_spec("felixo_notion_mcp") is None, "pré-condição"
        assert modulo._garantir_src_no_path(raiz) is True
        assert str(raiz / "src") in sys.path

        from felixo_notion_mcp.api import launcher

        assert Path(launcher.__file__).resolve().is_relative_to(src)
        modulo.main(["--help"])
        carregados = sorted(n for n in TERCEIROS if sys.modules.get(n) is not None)
        assert not carregados, carregados
        """
    ).replace("TERCEIROS", repr(TERCEIROS))

    resultado = subprocess.run(
        [sys.executable, "-c", codigo, str(RAIZ), *TERCEIROS],
        cwd=tmp_path,
        env=_ambiente_sem_pythonpath(),
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
        check=False,
    )

    assert resultado.returncode == 0, resultado.stderr
    assert "Uso: notion-automacoes-app" in resultado.stdout


def test_start_app_raiz_roda_como_script_num_python_sem_site_packages(tmp_path):
    """``python -S start_app.py --help``: nada instalado, só a biblioteca padrão."""

    resultado = subprocess.run(
        [sys.executable, "-S", str(RAIZ / "start_app.py"), "--help"],
        cwd=tmp_path,
        env=_ambiente_sem_pythonpath(),
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
        check=False,
    )

    assert resultado.returncode == 0, resultado.stderr
    assert "Uso: notion-automacoes-app" in resultado.stdout


def test_main_da_raiz_entrega_os_argumentos_ao_launcher(monkeypatch):
    mod = _carregar()
    from felixo_notion_mcp.api import launcher

    recebidos: list[list[str]] = []
    monkeypatch.setattr(launcher, "main", lambda argv=None: recebidos.append(argv))
    monkeypatch.setattr(sys, "argv", ["start_app.py", "--action", "status"])

    mod.main()

    assert recebidos == [["--action", "status"]]
