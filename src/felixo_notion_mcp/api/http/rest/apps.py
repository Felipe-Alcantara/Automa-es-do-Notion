"""Registro do app ``api`` (borda HTTP do servidor)."""

from __future__ import annotations

from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "felixo_notion_mcp.api.http.rest"
    #: O rótulo antigo é o que as migrações e o ``reverse()`` já conhecem; mudar o ``name``
    #: do módulo não pode mudar o que o usuário e o banco enxergam.
    label = "api"
