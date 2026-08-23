#!/usr/bin/env python
"""Verifica se o workspace de desenvolvimento está pronto.

Saída:
  - 0: tudo OK
  - 1: algo está faltando; siga as instruções

Uso: python check-dev.py
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

MODULOS = ["notion-starter", "notion-tasks-cli", "notion-workspace-app"]
ROOT = Path(__file__).resolve().parent
MODULOS_DIR = ROOT / "modules"


def tabuleiro() -> tuple[bool, list[str]]:
    """Verifica o estado do workspace."""

    msgs: list[str] = []
    ok = True

    # 1. Python version
    if sys.version_info < (3, 10):
        msgs.append(f"[FALHA] Python 3.10+ necessário (tem {sys.version_info.major}.{sys.version_info.minor})")
        ok = False
    else:
        msgs.append(f"[OK] Python {sys.version_info.major}.{sys.version_info.minor}")

    # 2. bootstrap.py rodou?
    if not MODULOS_DIR.exists():
        msgs.append("[FALHA] `modules/` não existe. Rode: python bootstrap.py")
        ok = False
    else:
        mensagens_modulos: list[str] = []
        faltam = []
        for m in MODULOS:
            p = MODULOS_DIR / m
            if (p / ".git").exists():
                mensagens_modulos.append(f"  [OK] {m}")
            else:
                mensagens_modulos.append(f"  [FALHA] {m}")
                faltam.append(m)
        msgs.append("[OK] modules/")
        msgs.extend(mensagens_modulos)
        if faltam:
            msgs.append(f"  (faltam: {', '.join(faltam)} — rode `python bootstrap.py`)")
            ok = False

    # 3. .env?
    env_file = ROOT / ".env"
    if env_file.exists():
        msgs.append("[OK] .env existente")
    else:
        msgs.append("[INFO] .env não encontrado (necessário para usar a CLI)")

    # 4. Deps instaladas?
    #
    # `find_spec` em vez de `import`: aqui a pergunta e se o pacote esta
    # disponivel, e importar de verdade so para descobrir isso executa o modulo
    # inteiro e deixa um import sem uso que o lint (com razao) acusa. Assim
    # tambem da para dizer QUAL pacote falta, em vez de parar no primeiro.
    faltam_pacotes = [nome for nome in ("pytest", "requests") if importlib.util.find_spec(nome) is None]
    if faltam_pacotes:
        msgs.append(f"[AVISO] Alguns pacotes faltam: {', '.join(faltam_pacotes)}")
    else:
        msgs.append("[OK] pytest, requests instalados")

    return ok, msgs


def main() -> int:
    print("\n" + "=" * 60)
    print("Verificacao do workspace - Automacoes do Notion")
    print("=" * 60 + "\n")

    ok, msgs = tabuleiro()

    for msg in msgs:
        print(msg)

    print("\n" + "=" * 60)
    if ok:
        print("OK - Workspace pronto para desenvolver!")
        print("\nProximos passos:")
        print("  1. Leia AGENTS.md para o roteamento")
        print("  2. cd modules/<nome>")
        print("  3. Edite o codigo")
        print("  4. python -m pytest")
        print("  5. git commit && git push (no modulo, nao aqui)")
        return 0
    else:
        print("FALHA - Workspace incompleto. Siga as instrucoes acima.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
