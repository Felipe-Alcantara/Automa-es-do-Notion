"""Fixtures válidas para a suíte inteira.

As duas fixtures são ``autouse`` de propósito: a suíte nunca deve ler nem gravar o perfil
nem a pasta de backup REAIS de quem a executa. Elas vieram do ``conftest.py`` da CLI
original; o truque de ``sys.path`` que havia lá deixou de existir, porque o ``pythonpath``
do ``pyproject.toml`` já põe ``src`` na frente.

Antes das fixtures, no nível do módulo, está a proteção do ``.env`` do checkout: fixture só
existe depois da coleta, e ``notion_tasks`` e o servidor MCP carregam o ``.env`` ao serem
importados, isto é, na coleta.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest

from felixo_notion_mcp.core import config, workspaces
from felixo_notion_mcp.services.backups import VARIAVEL_DIRETORIO_BACKUP


def _ignorar_o_env_do_checkout(original: Callable[..., None]) -> Callable[..., None]:
    """Devolve um ``carregar_env_file`` que pula o ``.env`` padrão do checkout.

    O checkout principal tem um ``.env`` de verdade, com ``NOTION_TOKEN`` e
    ``NOTION_DATABASE_ID``. Se a suíte o carregasse, testes que só queriam um ambiente limpo
    passariam a falar com a configuração real. Pula só o caminho padrão (``ENV_FILE``, lido
    na hora da chamada, quer venha omitido ou por extenso); qualquer caminho explícito,
    como os que os testes do próprio carregador montam em ``tmp_path``, continua carregando.

    Não há gancho no código de produção (variável de ambiente ou opção) que sirva melhor:
    acrescentar um só para a suíte daria a quem usa o produto um interruptor que ele não
    pediu, e a única forma de ele valer na coleta seria exportá-lo antes do pytest.
    """

    def carregar_env_file(caminho: Path | None = None) -> None:
        if caminho is None or Path(caminho) == config.ENV_FILE:
            return
        original(caminho)

    carregar_env_file.ignora_env_do_checkout = True
    return carregar_env_file


# Precisa rodar antes de qualquer teste ser importado: `from ... import carregar_env_file`
# congela a função que existe naquele instante. Idempotente.
if not getattr(config.carregar_env_file, "ignora_env_do_checkout", False):
    config.carregar_env_file = _ignorar_o_env_do_checkout(config.carregar_env_file)


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
    # `_migrar_legado` usa `shutil.move`: com um store antigo (tokens incluídos) em um destes
    # endereços, qualquer teste que carregasse o store o moveria para uma pasta temporária que
    # some no fim da execução. É o único consumidor de endereço legado (`ARQUIVO_LEGADO` só
    # compõe esta tupla no import). Os testes da migração põem os seus em `tmp_path`.
    monkeypatch.setattr(workspaces, "ARQUIVOS_LEGADOS", ())
    for variavel in (workspaces.ENV_TOKEN, workspaces.ENV_DATABASE, workspaces.ENV_PERFIL):
        monkeypatch.delenv(variavel, raising=False)
