#!/usr/bin/env python3
"""Porta de entrada única do Felixo Notion MCP: abre o menu do projeto.

Rode ``python start_app.py`` na raiz do checkout para abrir um menu interativo,
colorido e descritivo, onde você instala as dependências, configura o token do
Notion, sobe o app local e o servidor MCP e vê o estado do ambiente. Não é preciso
decorar comando nenhum.

O menu segue o contrato de menu de entrada do Felixo System Design, com no mínimo:

- Iniciar/Rodar: app local (API e SPA), servidor MCP e a CLI ``notion-tasks``;
- Instalar/Setup: instala o pacote em modo editável no Python que roda o menu;
- Configurar: o token do Notion e o database de tarefas, guardados em ``.env``
  (ignorado pelo git) e nunca no script; os perfis de workspace se gerenciam à parte, com
  ``felixo-notion-mcp auth`` (ou ``notion-tasks perfis``);
- Status/Sair: o estado do ambiente, incluindo de onde o pacote é importado (a mesma
  informação do ``doctor``), e a saída.

Este arquivo é só a porta: ele acha ``src/`` no checkout e chama o launcher que vive no
pacote (``felixo_notion_mcp.api.launcher``). Por isso usa apenas a biblioteca padrão e
roda num Python onde ainda não há nada instalado, em Windows, Linux e macOS. Quem
instalou o pacote a partir do checkout (``pip install -e ".[app]"``) abre o mesmo menu com
``notion-automacoes-app``. O nome ``felixo-notion-mcp`` ainda não está publicado no PyPI.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
PACOTE = "felixo_notion_mcp"


def _garantir_src_no_path(raiz: Path) -> bool:
    """Põe ``<raiz>/src`` no ``sys.path`` quando o pacote ainda não é importável.

    Num checkout recém-clonado, sem ``pip install -e``, o pacote só existe em
    ``src/``. Se o Python já o enxerga (instalação ou modo editável), o caminho não
    é tocado, para o menu nunca carregar uma segunda cópia do código.

    Devolve ``True`` quando inseriu o caminho.
    """

    if importlib.util.find_spec(PACOTE) is not None:
        return False
    src = raiz / "src"
    if not src.is_dir() or str(src) in sys.path:
        return False
    sys.path.insert(0, str(src))
    return True


def main(argv: list[str] | None = None) -> None:
    """Abre o menu do launcher, repassando os argumentos da linha de comando."""

    _garantir_src_no_path(RAIZ)
    try:
        from felixo_notion_mcp.api import launcher
    except ModuleNotFoundError as erro:
        if erro.name not in (PACOTE, f"{PACOTE}.api"):
            raise
        raise SystemExit(
            f"Não achei o pacote {PACOTE} (esperado em {RAIZ / 'src'}).\n"
            "Rode este arquivo de dentro do checkout do código-fonte (a pasta com src/ e\n"
            "pyproject.toml). A distribuição ainda não está publicada no PyPI (a publicação\n"
            "é de uma etapa posterior); instale a partir do checkout com:\n"
            '  uv sync --all-extras   ou   pip install -e ".[app]"'
        ) from None
    launcher.main(sys.argv[1:] if argv is None else argv)


if __name__ == "__main__":
    main()
