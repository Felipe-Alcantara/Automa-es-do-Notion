"""Grava o retrato da CLI a partir do código ANTIGO (antes de juntar os módulos).

Importa os parsers de `notion-tasks-cli` (`cli.notion_tasks` e `cli.unificada`) e o caminho
padrão do arquivo de perfis (`core.workspaces`), e grava um JSON com o contrato de linha de
comando. Esse arquivo é a referência dos testes de contrato: prova que a CLI nova aceita
exatamente o que a antiga aceitava.

Uso:
    python scripts/migracao/gravar_retrato_cli.py \\
        --cli <clone do notion-tasks-cli> --starter <clone do notion-starter> \\
        --saida tests/contrato/retrato_cli.json

Os clones devem estar nos commits fixos registrados no plano da etapa 1, para que o retrato
seja reproduzível.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import tempfile
from collections.abc import Sequence
from pathlib import Path
from types import ModuleType
from typing import Any

RAIZ = Path(__file__).resolve().parents[2]
ARQUIVO_RETRATO = RAIZ / "src" / "felixo_notion_mcp" / "api" / "cli" / "retrato.py"


def carregar_retrato() -> ModuleType:
    """Carrega `retrato.py` pelo caminho do arquivo, sem depender do pacote instalado."""
    spec = importlib.util.spec_from_file_location("retrato_cli_gravacao", ARQUIVO_RETRATO)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Não foi possível carregar {ARQUIVO_RETRATO}")
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def montar_retrato(cli: Path, starter: Path, pasta_falsa: Path) -> dict[str, Any]:
    """Retrata os dois parsers antigos e o caminho padrão de perfis.

    `XDG_CONFIG_HOME` e `APPDATA` apontam para `pasta_falsa` antes de qualquer import do
    código antigo, porque `core.workspaces` resolve a pasta de configuração ao ser
    importado. Assim o caminho gravado não depende da máquina nem do sistema operacional.
    """
    os.environ["XDG_CONFIG_HOME"] = str(pasta_falsa)
    os.environ["APPDATA"] = str(pasta_falsa)
    for pasta in (starter / "src", cli):
        sys.path.insert(0, str(pasta))

    # Imports tardios de propósito: só funcionam depois do sys.path e do ambiente acima.
    from cli import notion_tasks, unificada
    from core import workspaces

    retratar_parser = carregar_retrato().retratar_parser
    relativo = workspaces.caminho_padrao().relative_to(pasta_falsa)
    return {
        "notion_tasks": retratar_parser(notion_tasks.construir_parser()),
        "unificada": retratar_parser(unificada.construir_parser()),
        "perfis": {"relativo": relativo.as_posix()},
    }


def _argumentos(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Grava o retrato da CLI antiga para os testes de contrato."
    )
    parser.add_argument("--cli", type=Path, required=True, help="clone do notion-tasks-cli")
    parser.add_argument("--starter", type=Path, required=True, help="clone do notion-starter")
    parser.add_argument("--saida", type=Path, required=True, help="arquivo JSON de saída")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Ponto de entrada: valida os clones, monta o retrato e grava o JSON."""
    args = _argumentos(argv)
    cli = args.cli.resolve()
    starter = args.starter.resolve()
    if not (cli / "cli" / "notion_tasks.py").is_file():
        print(f"Clone do notion-tasks-cli inválido: {cli}", file=sys.stderr)
        return 2
    if not (starter / "src" / "notion_starter").is_dir():
        print(f"Clone do notion-starter inválido: {starter}", file=sys.stderr)
        return 2

    with tempfile.TemporaryDirectory(prefix="retrato-cli-") as pasta:
        retrato = montar_retrato(cli, starter, Path(pasta))

    args.saida.parent.mkdir(parents=True, exist_ok=True)
    texto = json.dumps(retrato, sort_keys=True, ensure_ascii=False, indent=2)
    args.saida.write_text(texto + "\n", encoding="utf-8")
    print(f"Retrato gravado em {args.saida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
