"""Ponto de entrada ASGI do servidor (deploy assíncrono / websockets futuros)."""

from __future__ import annotations

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "felixo_notion_mcp.api.http.config.settings")

application = get_asgi_application()
