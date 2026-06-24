"""Constantes compartilhadas do ``notion_starter``."""

from __future__ import annotations

NOTION_BASE_URL = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"
NOTION_TIMEOUT_SECONDS = 15

#: Variável de ambiente lida por padrão quando nenhum token é passado explicitamente.
NOTION_TOKEN_ENV = "NOTION_TOKEN"

#: Prefixo com que todo token de integração atual do Notion começa.
NOTION_TOKEN_PREFIX = "ntn_"
