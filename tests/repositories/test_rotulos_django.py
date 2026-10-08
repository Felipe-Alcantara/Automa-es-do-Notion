import pytest

pytest.importorskip("django")
import django


def test_rotulos_django_preservados(monkeypatch):
    monkeypatch.setenv("DJANGO_SETTINGS_MODULE", "felixo_notion_mcp.api.http.config.settings")
    # Sem DEBUG as settings exigem a DJANGO_SECRET_KEY real; o teste não depende de segredo.
    monkeypatch.setenv("DJANGO_DEBUG", "1")
    django.setup()
    from django.apps import apps

    from felixo_notion_mcp.repositories.operations.models import Job, Lock

    assert apps.get_app_config("operations").name == "felixo_notion_mcp.repositories.operations"
    assert apps.get_app_config("api").name == "felixo_notion_mcp.api.http.rest"
    assert (Job._meta.db_table, Lock._meta.db_table) == ("operations_job", "operations_lock")
