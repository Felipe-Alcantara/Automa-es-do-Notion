"""Contrato de linha de comando: o que a CLI aceitava antes continua sendo aceito.

``retrato_cli.json`` foi gravado a partir da CLI original (``notion-tasks-cli``), antes de
qualquer arquivo mudar de lugar. Se um destes testes falhar, alguma linha de comando que
funcionava deixou de ser aceita (ou passou a ter outro significado): isso é regressão, não
motivo para regravar o retrato.
"""

from __future__ import annotations

import json
from pathlib import Path

from felixo_notion_mcp.api.cli import notion_tasks, unificada
from felixo_notion_mcp.api.cli.retrato import retratar_parser
from felixo_notion_mcp.core import workspaces

RETRATO = json.loads((Path(__file__).parent / "retrato_cli.json").read_text(encoding="utf-8"))


def test_notion_tasks_aceita_exatamente_as_mesmas_linhas_de_comando():
    assert retratar_parser(notion_tasks.construir_parser()) == RETRATO["notion_tasks"]


def test_fachada_aceita_exatamente_as_mesmas_linhas_de_comando():
    assert retratar_parser(unificada.construir_parser()) == RETRATO["unificada"]


def test_perfis_continuam_no_mesmo_caminho(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    monkeypatch.setenv("APPDATA", str(tmp_path))

    relativo = workspaces.caminho_padrao().relative_to(tmp_path).as_posix()

    assert relativo == RETRATO["perfis"]["relativo"]
