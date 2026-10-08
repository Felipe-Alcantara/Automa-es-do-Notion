"""O pacote importa os nomes públicos sob demanda, sem perder nenhum deles.

``import felixo_notion_mcp`` não pode puxar o ``requests`` (nem o resto da biblioteca): o
launcher (``api/launcher.py``) e a configuração (``core/config.py``) precisam abrir num Python
sem nenhuma dependência instalada, para que o menu consiga oferecer Instalar/Setup. Os nomes
da API pública, herdada do ``notion_starter``, continuam importáveis por
``from felixo_notion_mcp import X``; só passam a ser resolvidos na primeira vez que são usados.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

import felixo_notion_mcp

RAIZ = Path(__file__).resolve().parents[2]

#: A ``__all__`` do pacote antes de ele passar a ser preguiçoso (Tarefa 6, correção 1).
API_PUBLICA_ANTIGA = (
    "NotionClient",
    "git_historico",
    "properties",
    "readers",
    "extrair_valores",
    "ler_propriedade",
    "markdown_para_blocos",
    "blocos_para_markdown",
    "Schema",
    "SchemaComparison",
    "EscritaAbaixoDeDatabaseError",
    "comparar_schema",
    "descrever_database",
    "DescricaoDatabase",
    "Coluna",
    "Relacao",
    "extrair_tipos_propriedades",
    "Inventario",
    "ItemInventario",
    "NoArvore",
    "GrupoSchema",
    "construir_inventario",
    "normalizar_item",
    "assinatura_schema",
    "assinatura_perfil",
    "extrair_perfil_database",
    "agrupar_por_schema",
    "agrupar_por_assinatura",
    "TaskList",
    "Tarefa",
    "CamposTarefa",
    "tarefa_de_pagina",
    "configure_logging",
    "get_logger",
    "NotionSyncError",
    "NotionAPIError",
    "NotionConfigurationError",
    "NotionConnectionError",
    "NotionHTTPError",
    "NotionInvalidResponseError",
    "NotionSchemaError",
    "__version__",
)


def _rodar(codigo: str) -> subprocess.CompletedProcess[str]:
    """Roda ``codigo`` num Python novo que só enxerga o pacote pelo ``src/``."""
    ambiente = dict(os.environ)
    ambiente["PYTHONPATH"] = str(RAIZ / "src")
    ambiente.update(PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
    return subprocess.run(
        [sys.executable, "-c", codigo],
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        env=ambiente,
        cwd=RAIZ,
        timeout=60,
        check=False,
    )


def test_all_e_exatamente_a_api_publica_antiga():
    assert list(felixo_notion_mcp.__all__) == list(API_PUBLICA_ANTIGA)
    assert len(set(felixo_notion_mcp.__all__)) == len(felixo_notion_mcp.__all__)


def test_tabela_de_origem_cobre_exatamente_o_all():
    cobertos = set(felixo_notion_mcp._ORIGEM) | set(felixo_notion_mcp._SUBMODULOS)

    assert cobertos == set(felixo_notion_mcp.__all__) - {"__version__"}


@pytest.mark.parametrize("nome", API_PUBLICA_ANTIGA)
def test_cada_nome_publico_resolve(nome):
    assert getattr(felixo_notion_mcp, nome) is not None


@pytest.mark.parametrize("nome", API_PUBLICA_ANTIGA)
def test_from_import_de_cada_nome_publico_funciona(nome):
    namespace: dict[str, object] = {}
    exec(f"from felixo_notion_mcp import {nome}", namespace)  # noqa: S102 - nome vem da lista acima

    assert namespace[nome] is getattr(felixo_notion_mcp, nome)


def test_from_import_estrela_traz_a_api_inteira():
    namespace: dict[str, object] = {}
    exec("from felixo_notion_mcp import *", namespace)  # noqa: S102

    assert set(API_PUBLICA_ANTIGA) <= set(namespace)


def test_nomes_sao_os_mesmos_objetos_dos_modulos_de_origem():
    from felixo_notion_mcp.core.exceptions import NotionSyncError
    from felixo_notion_mcp.domain import properties, readers
    from felixo_notion_mcp.domain.schema import comparar_schema
    from felixo_notion_mcp.integrations.notion_client import NotionClient

    assert felixo_notion_mcp.NotionClient is NotionClient
    assert felixo_notion_mcp.NotionSyncError is NotionSyncError
    assert felixo_notion_mcp.comparar_schema is comparar_schema
    assert felixo_notion_mcp.properties is properties
    assert felixo_notion_mcp.readers is readers


def test_nome_desconhecido_levanta_attribute_error_com_mensagem_clara():
    with pytest.raises(AttributeError, match="felixo_notion_mcp.*nao_existe"):
        felixo_notion_mcp.nao_existe  # noqa: B018 - o acesso é o que se testa

    with pytest.raises(ImportError):
        exec("from felixo_notion_mcp import nao_existe", {})  # noqa: S102


def test_dir_lista_a_api_publica():
    assert set(API_PUBLICA_ANTIGA) <= set(dir(felixo_notion_mcp))


def test_versao_e_texto_simples_disponivel_sem_resolver_nada():
    resultado = _rodar(
        "import sys; sys.modules['requests'] = None;"
        "import felixo_notion_mcp as p;"
        "assert 'NotionClient' not in vars(p);"
        "assert isinstance(vars(p)['__version__'], str);"
        "print(p.__version__)"
    )

    assert resultado.returncode == 0, resultado.stderr
    assert resultado.stdout.strip() == felixo_notion_mcp.__version__


def test_importar_o_pacote_nao_puxa_nenhuma_dependencia():
    resultado = _rodar(
        "import sys;"
        "[sys.modules.__setitem__(n, None) for n in "
        "('requests', 'docx', 'django', 'mcp', 'rich', 'questionary', 'openpyxl')];"
        "import felixo_notion_mcp;"
        "assert 'felixo_notion_mcp.integrations.notion_client' not in sys.modules"
    )

    assert resultado.returncode == 0, resultado.stderr


def test_nome_que_precisa_do_requests_falha_so_quando_e_usado():
    resultado = _rodar(
        "import sys; sys.modules['requests'] = None;"
        "import felixo_notion_mcp as p;"
        "print(p.NotionSyncError.__name__);"
        "p.NotionClient"
    )

    assert "NotionSyncError" in resultado.stdout
    assert resultado.returncode != 0
    assert "requests" in resultado.stderr
