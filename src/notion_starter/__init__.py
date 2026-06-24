"""notion_starter — um cliente Python pequeno e tipado para a API do Notion.

API pública:
    NotionClient: o cliente HTTP (cria/consulta databases e páginas).
    properties: helpers para montar valores de propriedade do Notion.
    comparar_schema / SchemaComparison: valida um database contra um schema.
    configure_logging: logging opcional em console/arquivo.
    Exceções: NotionSyncError e suas subclasses.
"""

from __future__ import annotations

from . import properties
from .client import NotionClient
from .exceptions import (
    NotionAPIError,
    NotionConfigurationError,
    NotionConnectionError,
    NotionHTTPError,
    NotionInvalidResponseError,
    NotionSchemaError,
    NotionSyncError,
)
from .logging import configure_logging, get_logger
from .schema import (
    Schema,
    SchemaComparison,
    comparar_schema,
    extrair_tipos_propriedades,
)

__version__ = "0.1.0"

__all__ = [
    "NotionClient",
    "properties",
    "Schema",
    "SchemaComparison",
    "comparar_schema",
    "extrair_tipos_propriedades",
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
