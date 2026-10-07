"""Registro do app ``operations`` (estado operacional em SQLite)."""

from __future__ import annotations

from django.apps import AppConfig


class OperationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "felixo_notion_mcp.repositories.operations"
    #: O rótulo antigo dá nome às tabelas (``operations_job``, ``operations_lock``) e ao
    #: histórico de migrações; mantê-lo preserva o banco de quem já usa o app.
    label = "operations"
