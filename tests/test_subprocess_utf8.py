"""Guarda: nenhum subprocess lê saída como texto na codepage da localidade.

``text=True`` sem ``encoding`` decodifica com a codepage do sistema. No Windows ela é
cp1252, enquanto os filhos Python (CLI, menu) e o ``git`` escrevem UTF-8: qualquer
acento na saída vira ``UnicodeDecodeError`` e ``stdout`` chega ``None``. Este teste
varre o AST de ``src/``, ``scripts/`` e ``tests/`` e reprova a chamada que pede texto
sem ``encoding="utf-8"`` nem ``errors="replace"``, para o erro não voltar só no CI do
Windows.
"""

from __future__ import annotations

import ast
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
PASTAS = ("src", "scripts", "tests")
CHAMADAS = {"run", "Popen", "check_output", "check_call", "call"}

# Exceção pontual: comentário ``# utf8-exempt: motivo`` numa linha da própria chamada.
MARCA_ISENCAO = "# utf8-exempt:"


def _chamadas_de_subprocess(arvore: ast.AST):
    for no in ast.walk(arvore):
        if not isinstance(no, ast.Call) or not isinstance(no.func, ast.Attribute):
            continue
        dono = no.func.value
        if no.func.attr in CHAMADAS and isinstance(dono, ast.Name) and dono.id == "subprocess":
            yield no


def _pede_texto(chamada: ast.Call) -> bool:
    for palavra in chamada.keywords:
        if palavra.arg in {"text", "universal_newlines"}:
            return not (isinstance(palavra.value, ast.Constant) and palavra.value.value is False)
    return False


def _decodificacao_segura(chamada: ast.Call) -> bool:
    """``encoding="utf-8"`` ou ``errors="replace"``: a leitura não levanta erro de decodificação."""

    for palavra in chamada.keywords:
        valor = palavra.value
        if not isinstance(valor, ast.Constant):
            continue
        if palavra.arg == "encoding" and valor.value == "utf-8":
            return True
        if palavra.arg == "errors" and valor.value == "replace":
            return True
    return False


def _isenta(chamada: ast.Call, linhas: list[str]) -> bool:
    trecho = linhas[chamada.lineno - 1 : (chamada.end_lineno or chamada.lineno)]
    return any(MARCA_ISENCAO in linha for linha in trecho)


def _arquivos():
    for pasta in PASTAS:
        yield from sorted((RAIZ / pasta).rglob("*.py"))


def test_subprocess_com_texto_declara_decodificacao_segura():
    infratores = []
    for arquivo in _arquivos():
        relativo = arquivo.relative_to(RAIZ).as_posix()
        codigo = arquivo.read_text(encoding="utf-8")
        linhas = codigo.splitlines()
        for chamada in _chamadas_de_subprocess(ast.parse(codigo, filename=relativo)):
            if (
                _pede_texto(chamada)
                and not _decodificacao_segura(chamada)
                and not _isenta(chamada, linhas)
            ):
                infratores.append(f"{relativo}:{chamada.lineno}")

    assert not infratores, (
        "subprocess com text=True precisa de encoding='utf-8' (saída em UTF-8) ou "
        "errors='replace' (saída em codepage local), ou '# utf8-exempt: motivo': "
        + ", ".join(infratores)
    )


def test_o_guarda_reconhece_chamadas_seguras_e_inseguras():
    def _analisar(codigo: str):
        (chamada,) = _chamadas_de_subprocess(ast.parse(codigo))
        return chamada, codigo.splitlines()

    ruim, _ = _analisar("import subprocess\nsubprocess.run(['x'], text=True)\n")
    assert _pede_texto(ruim) and not _decodificacao_segura(ruim)

    for seguro in (
        "subprocess.run(['x'], text=True, encoding='utf-8')",
        "subprocess.run(['x'], text=True, errors='replace')",
    ):
        chamada, _ = _analisar(f"import subprocess\n{seguro}\n")
        assert _decodificacao_segura(chamada)

    estrito, _ = _analisar("import subprocess\nsubprocess.run(['x'], text=True, errors='strict')\n")
    assert not _decodificacao_segura(estrito)

    isenta, linhas = _analisar(
        "import subprocess\nsubprocess.run(['x'], text=True)  # utf8-exempt: ASCII puro\n"
    )
    assert _isenta(isenta, linhas)
