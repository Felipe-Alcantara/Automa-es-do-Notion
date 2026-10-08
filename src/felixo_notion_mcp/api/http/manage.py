#!/usr/bin/env python3
"""Utilitário de linha de comando do Django para tarefas administrativas.

Rode como módulo, com o pacote instalado (ou ``src`` no ``PYTHONPATH``)::

    python -m felixo_notion_mcp.api.http.manage migrate

Não rode o arquivo por caminho: a pasta ``api/http`` entraria no começo do
``sys.path`` e esconderia pacotes de terceiros e da biblioteca padrão.
"""

from __future__ import annotations

import os
import sys


def main() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "felixo_notion_mcp.api.http.config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:  # pragma: no cover - mensagem de ajuda
        raise ImportError(
            "Django não está instalado. Instale os extras do app com:\n"
            '  pip install -e ".[app]"'
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
