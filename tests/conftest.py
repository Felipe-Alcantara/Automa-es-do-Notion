"""Configuração de testes compartilhada.

Adiciona ``server/`` ao ``sys.path`` para que os testes da camada de servidor
(``api``, ``services``, ``core``…) importem os pacotes de topo como o Django faz
ao rodar a partir de ``server/``. Os testes do pacote ``notion_starter`` não são
afetados (eles importam via instalação editável).
"""

from __future__ import annotations

import sys
from pathlib import Path

_SERVER = Path(__file__).resolve().parents[1] / "server"
if _SERVER.exists() and str(_SERVER) not in sys.path:
    sys.path.insert(0, str(_SERVER))
