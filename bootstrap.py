#!/usr/bin/env python
"""Bootstrap do workspace de desenvolvimento do ecossistema.

Prepara os módulos do ecossistema sob ``modules/`` (ignorado pelo git deste hub),
mantendo ``modules/<nome>`` como o caminho canônico de desenvolvimento. Para cada
módulo, a ordem de preferência é:

1. Já preparado em ``modules/<nome>`` (clone ou link) → ``git pull --ff-only``.
2. Já clonado na pasta acima (``../<nome>``) → cria um **link** para reusar o mesmo
   working copy, sem duplicar (junction no Windows, symlink no POSIX). O link não
   precisa de privilégio de administrador.
3. Não existe em lugar nenhum → clona do GitHub.

Uso: python bootstrap.py

Pós-bootstrap, rode: python check-dev.py
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

MODULOS = [
    "notion-starter",
    "notion-tasks-cli",
    "notion-workspace-app",
]
BASE_URL = "https://github.com/Felipe-Alcantara"
RAIZ = Path(__file__).resolve().parent
DESTINO = RAIZ / "modules"
ACIMA = RAIZ.parent


def _rodar(comando: list[str], cwd: Path | None = None) -> int:
    """Executa comando e retorna exit code."""
    print(f"$ {' '.join(comando)}")
    return subprocess.call(comando, cwd=str(cwd) if cwd else None)


def _criar_link(origem: Path, destino: Path) -> bool:
    """Cria um link de ``destino`` para ``origem`` (diretório).

    Usa symlink de diretório; no Windows, se faltar privilégio para symlink, cai
    para uma junction (``mklink /J``), que não exige administrador. Retorna ``True``
    em caso de sucesso.
    """
    try:
        os.symlink(origem, destino, target_is_directory=True)
        return True
    except (OSError, NotImplementedError):
        if os.name != "nt":
            return False
        # Windows sem privilégio de symlink: junction não precisa de admin.
        codigo = subprocess.call(
            ["cmd", "/c", "mklink", "/J", str(destino), str(origem)],
            stdout=subprocess.DEVNULL,
        )
        return codigo == 0


def _preparar(nome: str) -> bool:
    """Prepara um módulo em ``modules/<nome>``. Retorna ``True`` se ficou pronto."""
    pasta = DESTINO / nome

    # 1. Já preparado (clone ou link): apenas atualiza.
    if (pasta / ".git").exists():
        print(f"\n[{nome}] Já preparado — atualizando com git pull --ff-only...")
        return _rodar(["git", "pull", "--ff-only"], cwd=pasta) == 0

    # 2. Já clonado na pasta acima: reusa via link, sem duplicar.
    acima = ACIMA / nome
    if (acima / ".git").exists():
        print(f"\n[{nome}] Encontrado em {acima} — criando link para reusar o clone...")
        if _criar_link(acima, pasta):
            print(f"[{nome}] Link criado. Atualizando o clone compartilhado...")
            return _rodar(["git", "pull", "--ff-only"], cwd=pasta) == 0
        print(f"[{nome}] Não foi possível criar o link; clonando do GitHub...")

    # 3. Não existe em lugar nenhum: clona do GitHub.
    print(f"\n[{nome}] Clonando do GitHub...")
    return _rodar(["git", "clone", f"{BASE_URL}/{nome}.git", str(pasta)]) == 0


def main() -> int:
    print("\n" + "=" * 60)
    print("Bootstrap do ecossistema Automações do Notion")
    print("=" * 60 + "\n")

    DESTINO.mkdir(exist_ok=True)
    falhas = [nome for nome in MODULOS if not _preparar(nome)]

    print("\n" + "=" * 60)
    if falhas:
        print(f"FALHA ao preparar: {', '.join(falhas)}", file=sys.stderr)
        return 1

    print("OK - Workspace pronto em modules/")
    print("\nProximo passo:")
    print("  python check-dev.py")
    print("=" * 60 + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
