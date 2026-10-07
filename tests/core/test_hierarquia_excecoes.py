"""Toda falha da biblioteca deriva de NotionSyncError (AGENTS.md do módulo).

A base builtin antiga continua como segunda base: quem já capturava
``ValueError``/``RuntimeError`` (a CLI e o MCP do app) segue igual, e quem
captura ``NotionSyncError`` passa a pegar todas.
"""

from __future__ import annotations

import pytest

from felixo_notion_mcp.core.exceptions import NotionSyncError
from felixo_notion_mcp.domain.git_historico import GitIndisponivelError
from felixo_notion_mcp.integrations.github import GitHubAPIError, GitHubConnectionError
from felixo_notion_mcp.integrations.openrouter import CatalogoErro, ProvedorErro
from felixo_notion_mcp.services.ia import InterpretacaoErro
from felixo_notion_mcp.services.reordenacao import BlocoArriscadoError, BlocoImpossivelError


@pytest.mark.parametrize(
    "classe,base_antiga",
    [
        (BlocoArriscadoError, ValueError),
        (BlocoImpossivelError, ValueError),
        (InterpretacaoErro, ValueError),
        (GitIndisponivelError, RuntimeError),
        (CatalogoErro, RuntimeError),
        (ProvedorErro, RuntimeError),
        (GitHubAPIError, Exception),
        (GitHubConnectionError, Exception),
    ],
)
def test_excecoes_derivam_de_notion_sync_error_sem_perder_a_base_antiga(classe, base_antiga):
    assert issubclass(classe, NotionSyncError)
    assert issubclass(classe, base_antiga)


def test_github_api_error_mantem_a_assinatura():
    erro = GitHubAPIError(404, "x" * 600)
    assert erro.status_code == 404 and len(erro.body) == 500
