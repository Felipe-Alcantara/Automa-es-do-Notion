"""Fixtures válidas para a suíte inteira.

As duas fixtures são ``autouse`` de propósito: a suíte nunca deve ler nem gravar o perfil
nem a pasta de backup REAIS de quem a executa. Elas vieram do ``conftest.py`` da CLI
original; o truque de ``sys.path`` que havia lá deixou de existir, porque o ``pythonpath``
do ``pyproject.toml`` já põe ``src`` na frente.
"""

from __future__ import annotations

import pytest

from felixo_notion_mcp.core import workspaces
from felixo_notion_mcp.services.backups import VARIAVEL_DIRETORIO_BACKUP


@pytest.fixture(autouse=True)
def backups_isolados(tmp_path_factory, monkeypatch):
    """Manda os backups em JSON de ``reordenar-bloco`` para uma pasta temporária.

    O backup deixou de cair no diretório corrente (onde acabava versionado
    num repositório git) e passou para a pasta de estado do usuário. Sem esta
    fixture, a suíte gravaria nessa pasta real a cada teste de reordenação.
    """

    monkeypatch.setenv(VARIAVEL_DIRETORIO_BACKUP, str(tmp_path_factory.mktemp("backups")))


@pytest.fixture(autouse=True)
def perfis_isolados(tmp_path, monkeypatch):
    """Impede que o perfil REAL da máquina vaze para dentro dos testes.

    O store de perfis (``.notion-workspaces.json``) mora na pasta de configuração do
    usuário. Se o arquivo existir na máquina de quem roda a suíte, ``aplicar_perfil``
    exporta token e ``NOTION_DATABASE_ID`` de verdade no ambiente do processo, e testes
    que só queriam um double passam a falar com a configuração real, falhando (ou pior,
    passando) por um motivo que não tem nada a ver com o código.

    Foi exatamente o que aconteceu ao copiar o store para o diretório do módulo
    durante uma validação manual: três testes ficaram vermelhos sem nenhuma
    mudança de comportamento. O padrão aponta para o mesmo tipo de defeito de
    isolamento já visto em outros projetos do ecossistema.
    """

    monkeypatch.setattr(workspaces, "ARQUIVO_PADRAO", tmp_path / "workspaces.json")
    for variavel in (workspaces.ENV_TOKEN, workspaces.ENV_DATABASE, workspaces.ENV_PERFIL):
        monkeypatch.delenv(variavel, raising=False)
