#!/usr/bin/env python3
"""Executa o gate local de qualidade do repositório.

Uso principal:
    python3 scripts/quality_check.py

O script usa apenas ferramentas já declaradas no projeto. Antes de rodar, instale
as dependências com ``pip install -e ".[dev]"`` e, para o front, ``npm install``
dentro de ``front/``.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
FRONT = RAIZ / "front"


@dataclass(frozen=True)
class Verificacao:
    nome: str
    comando: tuple[str, ...]
    cwd: Path
    dica: str


VERIFICACOES_PYTHON = (
    Verificacao(
        nome="Ruff",
        comando=("ruff", "check", "."),
        cwd=RAIZ,
        dica='Instale as dependências de dev com: pip install -e ".[dev]"',
    ),
    Verificacao(
        nome="Pytest",
        comando=("pytest", "-q"),
        cwd=RAIZ,
        dica='Instale as dependências de dev com: pip install -e ".[dev]"',
    ),
)

VERIFICACOES_FRONT = (
    Verificacao(
        nome="Oxlint",
        comando=("npm", "run", "lint"),
        cwd=FRONT,
        dica="Instale as dependências do front com: cd front && npm install",
    ),
    Verificacao(
        nome="Vite build",
        comando=("npm", "run", "build"),
        cwd=FRONT,
        dica="Instale as dependências do front com: cd front && npm install",
    ),
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    grupo = parser.add_mutually_exclusive_group()
    grupo.add_argument(
        "--python-only",
        action="store_true",
        help="roda apenas Ruff e Pytest",
    )
    grupo.add_argument(
        "--front-only",
        action="store_true",
        help="roda apenas lint e build do front",
    )
    return parser


def _selecionar_verificacoes(args: argparse.Namespace) -> tuple[Verificacao, ...]:
    if args.python_only:
        return VERIFICACOES_PYTHON
    if args.front_only:
        return VERIFICACOES_FRONT
    return (*VERIFICACOES_PYTHON, *VERIFICACOES_FRONT)


def _executavel_disponivel(comando: tuple[str, ...]) -> bool:
    return shutil.which(comando[0]) is not None


def _rodar(verificacao: Verificacao) -> int:
    print(f"\n==> {verificacao.nome}: {' '.join(verificacao.comando)}", flush=True)
    if not verificacao.cwd.exists():
        print(f"Diretório inexistente: {verificacao.cwd}", file=sys.stderr)
        return 1
    if not _executavel_disponivel(verificacao.comando):
        print(f"Comando não encontrado: {verificacao.comando[0]}", file=sys.stderr)
        print(verificacao.dica, file=sys.stderr)
        return 127

    resultado = subprocess.run(verificacao.comando, cwd=verificacao.cwd, check=False)
    if resultado.returncode != 0:
        print(
            f"Falhou: {verificacao.nome} retornou código {resultado.returncode}",
            file=sys.stderr,
        )
    return resultado.returncode


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    verificacoes = _selecionar_verificacoes(args)

    falhas: list[str] = []
    for verificacao in verificacoes:
        if _rodar(verificacao) != 0:
            falhas.append(verificacao.nome)

    if falhas:
        print("\nGate de qualidade reprovado: " + ", ".join(falhas), file=sys.stderr)
        return 1

    print("\nGate de qualidade aprovado.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
