"""felixo_notion_mcp — Notion em um único pacote: biblioteca, CLI, servidor MCP e app.

Esta é a API pública herdada do ``notion_starter``: tudo o que o ``notion_starter``
oferecia continua importável daqui.

API pública:
    NotionClient: o cliente HTTP (cria/consulta databases, páginas e blocos).
    properties / readers: par de escrita e leitura de valores de propriedade.
    markdown_para_blocos / blocos_para_markdown: par de escrita e leitura do
        conteúdo (blocos) de uma página como Markdown.
    extrair_valores: reduz uma página do Notion a um mapa coluna -> valor simples.
    comparar_schema / SchemaComparison: valida um database contra um schema.
    descrever_database / DescricaoDatabase: lê o schema real de um database —
        colunas, tipos, opções válidas e como cada relação está configurada.
    construir_inventario / Inventario: mapeia o workspace (árvore, duplicatas, órfãos).
    configure_logging: logging opcional em console/arquivo.
    Exceções: NotionSyncError e suas subclasses.
"""

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING, Any

# Nada abaixo é importado ao abrir o pacote: `import felixo_notion_mcp` só custa a stdlib.
# O launcher (`api/launcher.py`) e a configuração (`core/config.py`) moram dentro deste
# pacote e precisam abrir num Python sem nenhuma dependência instalada (um `.venv` recém-criado),
# justamente para o menu poder oferecer Instalar/Setup. Importar o cliente HTTP aqui puxaria o
# `requests` já na primeira linha. Cada nome da API pública é resolvido na primeira vez que é
# pedido (PEP 562) e fica guardado no módulo.
__version__ = "0.6.0.dev0"

#: Nome público -> módulo que o define.
_ORIGEM: dict[str, str] = {
    "NotionClient": "felixo_notion_mcp.integrations.notion_client",
    "extrair_valores": "felixo_notion_mcp.domain.readers",
    "ler_propriedade": "felixo_notion_mcp.domain.readers",
    "markdown_para_blocos": "felixo_notion_mcp.domain.content",
    "blocos_para_markdown": "felixo_notion_mcp.domain.content",
    "Schema": "felixo_notion_mcp.domain.schema",
    "SchemaComparison": "felixo_notion_mcp.domain.schema",
    "comparar_schema": "felixo_notion_mcp.domain.schema",
    "descrever_database": "felixo_notion_mcp.domain.schema",
    "DescricaoDatabase": "felixo_notion_mcp.domain.schema",
    "Coluna": "felixo_notion_mcp.domain.schema",
    "Relacao": "felixo_notion_mcp.domain.schema",
    "extrair_tipos_propriedades": "felixo_notion_mcp.domain.schema",
    "Inventario": "felixo_notion_mcp.services.inventory",
    "ItemInventario": "felixo_notion_mcp.services.inventory",
    "NoArvore": "felixo_notion_mcp.services.inventory",
    "GrupoSchema": "felixo_notion_mcp.services.inventory",
    "construir_inventario": "felixo_notion_mcp.services.inventory",
    "normalizar_item": "felixo_notion_mcp.services.inventory",
    "assinatura_schema": "felixo_notion_mcp.services.inventory",
    "assinatura_perfil": "felixo_notion_mcp.services.inventory",
    "extrair_perfil_database": "felixo_notion_mcp.services.inventory",
    "agrupar_por_schema": "felixo_notion_mcp.services.inventory",
    "agrupar_por_assinatura": "felixo_notion_mcp.services.inventory",
    "TaskList": "felixo_notion_mcp.domain.tasks",
    "Tarefa": "felixo_notion_mcp.domain.tasks",
    "CamposTarefa": "felixo_notion_mcp.domain.tasks",
    "tarefa_de_pagina": "felixo_notion_mcp.domain.tasks",
    "configure_logging": "felixo_notion_mcp.core.logging",
    "get_logger": "felixo_notion_mcp.core.logging",
    "NotionSyncError": "felixo_notion_mcp.core.exceptions",
    "NotionAPIError": "felixo_notion_mcp.core.exceptions",
    "NotionConfigurationError": "felixo_notion_mcp.core.exceptions",
    "NotionConnectionError": "felixo_notion_mcp.core.exceptions",
    "NotionHTTPError": "felixo_notion_mcp.core.exceptions",
    "NotionInvalidResponseError": "felixo_notion_mcp.core.exceptions",
    "NotionSchemaError": "felixo_notion_mcp.core.exceptions",
    "EscritaAbaixoDeDatabaseError": "felixo_notion_mcp.core.exceptions",
}

#: Nome público -> submódulo inteiro (em vez de um nome dentro de um módulo).
_SUBMODULOS: dict[str, str] = {
    "git_historico": "felixo_notion_mcp.domain.git_historico",
    "properties": "felixo_notion_mcp.domain.properties",
    "readers": "felixo_notion_mcp.domain.readers",
}

if TYPE_CHECKING:  # só para o editor e o type checker; em execução nada disto roda
    from felixo_notion_mcp.core.exceptions import (
        EscritaAbaixoDeDatabaseError,
        NotionAPIError,
        NotionConfigurationError,
        NotionConnectionError,
        NotionHTTPError,
        NotionInvalidResponseError,
        NotionSchemaError,
        NotionSyncError,
    )
    from felixo_notion_mcp.core.logging import configure_logging, get_logger
    from felixo_notion_mcp.domain import git_historico, properties, readers
    from felixo_notion_mcp.domain.content import blocos_para_markdown, markdown_para_blocos
    from felixo_notion_mcp.domain.readers import extrair_valores, ler_propriedade
    from felixo_notion_mcp.domain.schema import (
        Coluna,
        DescricaoDatabase,
        Relacao,
        Schema,
        SchemaComparison,
        comparar_schema,
        descrever_database,
        extrair_tipos_propriedades,
    )
    from felixo_notion_mcp.domain.tasks import CamposTarefa, Tarefa, TaskList, tarefa_de_pagina
    from felixo_notion_mcp.integrations.notion_client import NotionClient
    from felixo_notion_mcp.services.inventory import (
        GrupoSchema,
        Inventario,
        ItemInventario,
        NoArvore,
        agrupar_por_assinatura,
        agrupar_por_schema,
        assinatura_perfil,
        assinatura_schema,
        construir_inventario,
        extrair_perfil_database,
        normalizar_item,
    )


def __getattr__(nome: str) -> Any:
    """Resolve um nome da API pública na primeira vez que ele é pedido (PEP 562)."""

    if nome in _SUBMODULOS:
        valor: Any = importlib.import_module(_SUBMODULOS[nome])
    elif nome in _ORIGEM:
        valor = getattr(importlib.import_module(_ORIGEM[nome]), nome)
    else:
        raise AttributeError(f"module {__name__!r} has no attribute {nome!r}")
    globals()[nome] = valor
    return valor


def __dir__() -> list[str]:
    """Inclui a API pública, que ainda não foi resolvida, no `dir()` do pacote."""

    return sorted({*globals(), *__all__})


__all__ = [
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
]
