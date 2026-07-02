#!/usr/bin/env python
"""Bootstrap do workspace de desenvolvimento do ecossistema.

Clona (ou atualiza com ``git pull``) os módulos do ecossistema em ``modules/``,
que é ignorado pelo git deste hub.

Uso: python bootstrap.py

Pós-bootstrap, rode: python check-dev.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

MODULOS = [
    "notion-starter",
    "notion-tasks-cli",
    "notion-workspace-app",
]
BASE_URL = "https://github.com/Felipe-Alcantara"
DESTINO = Path(__file__).resolve().parent / "modules"


def _rodar(comando: list[str], cwd: Path | None = None) -> int:
    """Executa comando e retorna exit code."""
    print(f"$ {' '.join(comando)}")
    return subprocess.call(comando, cwd=str(cwd) if cwd else None)


def main() -> int:
    print("\n" + "=" * 60)
    print("Bootstrap do ecossistema Automações do Notion")
    print("=" * 60 + "\n")

    DESTINO.mkdir(exist_ok=True)
    falhas: list[str] = []

    for nome in MODULOS:
        pasta = DESTINO / nome
        if (pasta / ".git").exists():
            print(f"\n[{nome}] Atualizando com git pull --ff-only...")
            codigo = _rodar(["git", "pull", "--ff-only"], cwd=pasta)
        else:
            print(f"\n[{nome}] Clonando do GitHub...")
            codigo = _rodar(["git", "clone", f"{BASE_URL}/{nome}.git", str(pasta)])
        if codigo != 0:
            falhas.append(nome)

    print("\n" + "=" * 60)
    if falhas:
        print(f"FALHA ao preparar: {', '.join(falhas)}", file=sys.stderr)
        return 1

    print(f"OK - Workspace pronto em modules/")
    print("\nProximo passo:")
    print("  python check-dev.py")
    print("=" * 60 + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
