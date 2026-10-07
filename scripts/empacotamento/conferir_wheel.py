"""Confere se o wheel carrega os arquivos de dados que o pacote precisa em tempo de execução.

O `hatchling` empacota os módulos Python sozinho, mas migrações, templates, estáticos e o
bundle da SPA são dados: se saírem do wheel, o pacote instala sem erro e quebra só quando o
app sobe. Esta conferência roda no CI depois do `uv build` e também à mão.

Uso: `python -m scripts.empacotamento.conferir_wheel dist/*.whl`
"""

from __future__ import annotations

import argparse
import glob
import sys
import zipfile
from pathlib import Path

ARQUIVOS_OBRIGATORIOS: tuple[str, ...] = (
    "felixo_notion_mcp/repositories/operations/migrations/0001_initial.py",
    "felixo_notion_mcp/api/http/templates/tarefas.html",
    "felixo_notion_mcp/api/http/static/frontend/index.html",
    "felixo_notion_mcp/api/http/static/css/app.css",
)


def faltando_no_wheel(caminho_wheel: Path) -> list[str]:
    """Lista, na ordem de `ARQUIVOS_OBRIGATORIOS`, o que não está dentro do wheel."""

    with zipfile.ZipFile(caminho_wheel) as wheel:
        presentes = set(wheel.namelist())
    return [nome for nome in ARQUIVOS_OBRIGATORIOS if nome not in presentes]


def _expandir(padrao: str) -> list[Path]:
    """Expande `*` e `?` quando o shell não o fez (o `cmd` e o PowerShell não expandem)."""

    if Path(padrao).exists():
        return [Path(padrao)]
    return [Path(achado) for achado in sorted(glob.glob(padrao))]


def main(argv: list[str] | None = None) -> int:
    """Confere cada wheel informado; sai com 1 e lista o que falta se algum estiver incompleto."""

    parser = argparse.ArgumentParser(
        description="Confere se o wheel contém os arquivos de dados obrigatórios."
    )
    parser.add_argument("wheels", nargs="+", help="caminho(s) do wheel, aceita curingas")
    args = parser.parse_args(argv)

    caminhos = [caminho for padrao in args.wheels for caminho in _expandir(padrao)]
    if not caminhos:
        print(f"Nenhum wheel encontrado em: {' '.join(args.wheels)}", file=sys.stderr)
        return 1

    incompleto = False
    for caminho in caminhos:
        faltando = faltando_no_wheel(caminho)
        if faltando:
            incompleto = True
            print(f"{caminho.name}: faltam {len(faltando)} arquivo(s) de dados:", file=sys.stderr)
            for nome in faltando:
                print(f"  - {nome}", file=sys.stderr)
        else:
            print(f"{caminho.name}: ok ({len(ARQUIVOS_OBRIGATORIOS)} arquivos de dados presentes)")
    return 1 if incompleto else 0


if __name__ == "__main__":
    raise SystemExit(main())
