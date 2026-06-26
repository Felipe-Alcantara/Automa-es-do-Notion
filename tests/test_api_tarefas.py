"""Testes das rotas REST de tarefas, ponta a ponta pela borda HTTP.

Usa o test client do Django (sem rede) com o Notion mockado por ``responses``,
exercitando o caminho real: view → service → ``TaskList`` → ``NotionClient``.
Pulado se o Django não estiver instalado (extras de servidor ausentes).
"""

from __future__ import annotations

import json
import os

import pytest

pytest.importorskip("django")

import responses  # noqa: E402

from notion_starter.constants import NOTION_BASE_URL  # noqa: E402

DB = "db_tarefas"


@pytest.fixture(scope="module", autouse=True)
def _django():
    # Config mínima para subir o Django sem segredo real nem rede.
    os.environ.setdefault("DJANGO_DEBUG", "1")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    import django

    django.setup()


@pytest.fixture(autouse=True)
def _notion_env(monkeypatch):
    # Fixa token/database deste módulo a cada teste. Usa setenv (não
    # setdefault) para não herdar valores que outro teste possa ter deixado
    # em os.environ — as rotas montam o NotionClient a partir do ambiente.
    monkeypatch.setenv("NOTION_TOKEN", "ntn_test_token")
    monkeypatch.setenv("NOTION_DATABASE_ID", DB)


@pytest.fixture
def client():
    from django.test import Client

    return Client()


def _pagina(id_, nome, status=None, prazo=None, duracao=None, areas=None):
    props = {"Nome": {"type": "title", "title": [{"plain_text": nome}]}}
    if status is not None:
        props["Status"] = {"type": "status", "status": {"name": status}}
    if prazo is not None:
        props["Próximo prazo"] = {"type": "date", "date": {"start": prazo}}
    if duracao is not None:
        props["Duração"] = {"type": "status", "status": {"name": duracao}}
    if areas is not None:
        props["Áreas-da-Vida"] = {
            "type": "relation",
            "relation": [{"id": area_id} for area_id in areas],
        }
    return {"id": id_, "url": f"https://notion.so/{id_}", "properties": props}


@responses.activate
def test_get_tarefas_lista(client):
    responses.add(
        responses.POST,
        f"{NOTION_BASE_URL}/databases/{DB}/query",
        json={"results": [_pagina("t1", "A", "00. Inbox")], "has_more": False},
        status=200,
    )
    resp = client.get("/api/tarefas")
    assert resp.status_code == 200
    corpo = resp.json()
    assert corpo["tarefas"][0]["nome"] == "A"
    assert "bruto" not in corpo["tarefas"][0]


@responses.activate
def test_get_tarefas_filtra_por_status(client):
    responses.add(
        responses.POST,
        f"{NOTION_BASE_URL}/databases/{DB}/query",
        json={"results": [], "has_more": False},
        status=200,
    )
    client.get("/api/tarefas", {"status": "00. Inbox"})
    corpo = json.loads(responses.calls[0].request.body)
    assert corpo["filter"] == {"property": "Status", "status": {"equals": "00. Inbox"}}


@responses.activate
def test_get_tarefas_filtra_por_status_duracao_e_area(client):
    responses.add(
        responses.POST,
        f"{NOTION_BASE_URL}/databases/{DB}/query",
        json={"results": [], "has_more": False},
        status=200,
    )
    client.get("/api/tarefas", {"status": "00. Inbox", "duracao": "Dias", "area": "a1"})
    corpo = json.loads(responses.calls[0].request.body)
    assert corpo["filter"] == {
        "and": [
            {"property": "Status", "status": {"equals": "00. Inbox"}},
            {"property": "Duração", "status": {"equals": "Dias"}},
            {"property": "Áreas-da-Vida", "relation": {"contains": "a1"}},
        ]
    }


@responses.activate
def test_post_tarefa_cria(client):
    responses.add(
        responses.POST,
        f"{NOTION_BASE_URL}/pages",
        json=_pagina("novo", "Nova", "00. Inbox", duracao="Dias", areas=["a1"]),
        status=200,
    )
    resp = client.post(
        "/api/tarefas",
        data=json.dumps(
            {
                "nome": "Nova",
                "status": "00. Inbox",
                "duracao": "Dias",
                "areas": ["a1"],
            }
        ),
        content_type="application/json",
    )
    assert resp.status_code == 201
    corpo = resp.json()
    assert corpo["id"] == "novo"
    assert corpo["duracao"] == "Dias"
    assert corpo["areas"] == ["a1"]

    request = json.loads(responses.calls[0].request.body)
    assert request["properties"]["Duração"]["status"]["name"] == "Dias"
    assert request["properties"]["Áreas-da-Vida"]["relation"] == [{"id": "a1"}]


def test_post_tarefa_sem_nome_e_400(client):
    resp = client.post(
        "/api/tarefas",
        data=json.dumps({"status": "00. Inbox"}),
        content_type="application/json",
    )
    assert resp.status_code == 400
    assert resp.json()["erro"]["codigo"] == "validacao"


@responses.activate
def test_patch_tarefa_move_status(client):
    responses.add(
        responses.PATCH,
        f"{NOTION_BASE_URL}/pages/t1",
        json=_pagina("t1", "A", "02. Fazendo"),
        status=200,
    )
    resp = client.patch(
        "/api/tarefas/t1",
        data=json.dumps({"status": "02. Fazendo"}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "02. Fazendo"


@responses.activate
def test_patch_tarefa_edita_campos_amplos(client):
    responses.add(
        responses.PATCH,
        f"{NOTION_BASE_URL}/pages/t1",
        json=_pagina("t1", "Renomeada", "02. Fazendo", duracao="Poucas horas", areas=["a1"]),
        status=200,
    )
    resp = client.patch(
        "/api/tarefas/t1",
        data=json.dumps(
            {
                "nome": "Renomeada",
                "status": "02. Fazendo",
                "duracao": "Poucas horas",
                "areas": ["a1"],
            }
        ),
        content_type="application/json",
    )
    assert resp.status_code == 200
    corpo = resp.json()
    assert corpo["nome"] == "Renomeada"
    assert corpo["duracao"] == "Poucas horas"
    assert corpo["areas"] == ["a1"]

    request = json.loads(responses.calls[0].request.body)
    assert request["properties"]["Nome"]["title"][0]["text"]["content"] == "Renomeada"
    assert request["properties"]["Duração"]["status"]["name"] == "Poucas horas"
    assert request["properties"]["Áreas-da-Vida"]["relation"] == [{"id": "a1"}]


def test_patch_tarefa_sem_campos_e_400(client):
    resp = client.patch(
        "/api/tarefas/t1",
        data=json.dumps({}),
        content_type="application/json",
    )
    assert resp.status_code == 400
    assert resp.json()["erro"]["codigo"] == "validacao"


def test_patch_tarefa_areas_invalidas_e_400(client):
    resp = client.patch(
        "/api/tarefas/t1",
        data=json.dumps({"areas": "a1"}),
        content_type="application/json",
    )
    assert resp.status_code == 400
    assert resp.json()["erro"]["codigo"] == "validacao"


@responses.activate
def test_patch_tarefa_inexistente_e_404(client):
    responses.add(
        responses.PATCH,
        f"{NOTION_BASE_URL}/pages/inexistente",
        json={"message": "Could not find page"},
        status=404,
    )
    resp = client.patch(
        "/api/tarefas/inexistente",
        data=json.dumps({"status": "06. Feito"}),
        content_type="application/json",
    )
    assert resp.status_code == 404
    assert resp.json()["erro"]["codigo"] == "nao_encontrado"


@responses.activate
def test_falha_do_notion_vira_502(client):
    responses.add(
        responses.POST,
        f"{NOTION_BASE_URL}/databases/{DB}/query",
        json={"message": "erro interno"},
        status=500,
    )
    resp = client.get("/api/tarefas")
    assert resp.status_code == 502
    assert resp.json()["erro"]["codigo"] == "erro_upstream"


def test_configuracao_ausente_orienta_iniciar_tudo(client, monkeypatch):
    from api import views
    from django.core.exceptions import ImproperlyConfigured

    def falhar(*args, **kwargs):
        raise ImproperlyConfigured("detalhe interno")

    monkeypatch.setattr(views.svc, "listar_tarefas", falhar)

    resp = client.get("/api/tarefas")

    assert resp.status_code == 500
    assert resp.json()["erro"]["codigo"] == "erro_interno"
    assert "Iniciar tudo" in resp.json()["erro"]["mensagem"]
    assert "detalhe interno" not in resp.content.decode()


def test_metodo_nao_permitido_e_405(client):
    resp = client.delete("/api/tarefas/t1")
    assert resp.status_code == 405


@responses.activate
def test_get_opcoes_lista_status_duracao_areas(client):
    responses.add(
        responses.GET,
        f"{NOTION_BASE_URL}/databases/{DB}",
        json={
            "properties": {
                "Status": {
                    "type": "status",
                    "status": {"options": [{"name": "00. Inbox"}, {"name": "06. Feito"}]},
                },
                "Duração": {
                    "type": "status",
                    "status": {"options": [{"name": "Minutos"}, {"name": "Dias"}]},
                },
                "Áreas-da-Vida": {
                    "type": "relation",
                    "relation": {"database_id": "db_areas"},
                },
            },
        },
        status=200,
    )
    responses.add(
        responses.POST,
        f"{NOTION_BASE_URL}/databases/db_areas/query",
        json={
            "results": [
                {
                    "id": "a1",
                    "properties": {
                        "Nome": {
                            "type": "title",
                            "title": [{"plain_text": "Estudos"}],
                        }
                    },
                }
            ],
            "has_more": False,
        },
        status=200,
    )
    resp = client.get("/api/opcoes")
    assert resp.status_code == 200
    assert resp.json() == {
        "status": ["00. Inbox", "06. Feito"],
        "duracao": ["Minutos", "Dias"],
        "areas": [{"id": "a1", "nome": "Estudos"}],
    }
