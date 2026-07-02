#!/usr/bin/env python
"""Sincroniza os módulos e valida o workspace.

Atualiza cada módulo em modules/ com 'git pull --ff-only' e valida
com check-dev.py.

Uso: python sync.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent


def _rodar(comando: list[str], descricao: str = "") -> int:
    """Executa comando e retorna exit code."""
    if descricao:
        print(f"\n{descricao}")
    print(f"$ {' '.join(comando)}")
    return subprocess.call(comando)


def main() -> int:
    print("\n" + "=" * 60)
    print("Sincronizacao - Automacoes do Notion")
    print("=" * 60)

    # 1. Bootstrap (clona ou atualiza modulos)
    codigo = _rodar(
        [sys.executable, "bootstrap.py"],
        descricao="[1/2] Sincronizando modulos com git pull...",
    )
    if codigo != 0:
        print("\nFalha no bootstrap. Abortando.", file=sys.stderr)
        return 1

    # 2. Check (valida workspace)
    codigo = _rodar(
        [sys.executable, "check-dev.py"],
        descricao="[2/2] Verificando workspace...",
    )

    print("\n" + "=" * 60)
    if codigo == 0:
        print("OK - Tudo sincronizado e pronto!")
    else:
        print("FALHA - Veja os erros acima.")
    print("=" * 60 + "\n")
    return codigo


if __name__ == "__main__":
    raise SystemExit(main())
