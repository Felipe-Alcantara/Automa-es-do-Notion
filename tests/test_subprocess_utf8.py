"""Guarda: nenhum subprocess lê saída como texto na codepage da localidade.

``text=True`` sem ``encoding`` decodifica com a codepage do sistema. No Windows ela é
cp1252, enquanto os filhos Python (CLI, menu) e o ``git`` escrevem UTF-8: qualquer
acento na saída vira ``UnicodeDecodeError`` e ``stdout`` chega ``None``. Este teste
varre o AST de ``src/``, ``scripts/`` e ``tests/`` e reprova a chamada que pede texto
sem ``encoding="utf-8"`` explícito, para o erro não voltar só no CI do Windows.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
PASTAS = ("src", "scripts", "tests")
CHAMADAS = {"run", "Popen", "check_output", "check_call", "call"}

# Exceções deliberadas, com o motivo. Caminho relativo à raiz -> por que não é UTF-8.
EXCECOES = {
    # icacls devolve texto na codepage OEM do console; só entra em mensagem de aviso.
    "src/felixo_notion_mcp/core/workspaces.py": "icacls fala a codepage OEM",
    # ``node --version`` é ASCII puro.
    "src/felixo_notion_mcp/api/launcher.py": "saída ASCII (versão do node)",
    # Script de migração pontual; só repassa mensagens de erro do controle de versão.
    "scripts/migracao/mover_para_camadas.py": "migração pontual, só mensagens de erro",
}


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


def _encoding_utf8(chamada: ast.Call) -> bool:
    for palavra in chamada.keywords:
        if palavra.arg == "encoding":
            return isinstance(palavra.value, ast.Constant) and palavra.value.value == "utf-8"
    return False


def _arquivos():
    for pasta in PASTAS:
        yield from sorted((RAIZ / pasta).rglob("*.py"))


def test_subprocess_com_texto_declara_utf8():
    infratores = []
    for arquivo in _arquivos():
        relativo = arquivo.relative_to(RAIZ).as_posix()
        if relativo in EXCECOES:
            continue
        arvore = ast.parse(arquivo.read_text(encoding="utf-8"), filename=relativo)
        for chamada in _chamadas_de_subprocess(arvore):
            if _pede_texto(chamada) and not _encoding_utf8(chamada):
                infratores.append(f"{relativo}:{chamada.lineno}")

    assert not infratores, (
        "subprocess com text=True precisa de encoding='utf-8' (e o filho de "
        "PYTHONIOENCODING/PYTHONUTF8): " + ", ".join(infratores)
    )


def test_o_guarda_reprova_text_true_sem_encoding():
    ruim = ast.parse("import subprocess\nsubprocess.run(['x'], text=True)\n")
    bom = ast.parse("import subprocess\nsubprocess.run(['x'], text=True, encoding='utf-8')\n")

    (chamada_ruim,) = _chamadas_de_subprocess(ruim)
    (chamada_boa,) = _chamadas_de_subprocess(bom)
    assert _pede_texto(chamada_ruim) and not _encoding_utf8(chamada_ruim)
    assert _pede_texto(chamada_boa) and _encoding_utf8(chamada_boa)


@pytest.mark.parametrize("relativo", sorted(EXCECOES))
def test_as_excecoes_existem_de_verdade(relativo):
    assert (RAIZ / relativo).is_file()
