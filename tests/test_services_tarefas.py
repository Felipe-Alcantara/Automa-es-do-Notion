"""Testes dos casos de uso de tarefas (``services.tarefas``).

A ``TaskList`` é injetada e o HTTP do Notion é mockado com ``responses`` — sem
token nem rede real. Verifica que cada caso de uso delega corretamente à
``TaskList`` e devolve a tarefa normalizada.
"""

from __future__ import annotations

import json

import responses
from services import tarefas as svc

from notion_starter import NotionClient, TaskList
from notion_starter.constants import NOTION_BASE_URL

TOKEN = "ntn_test_token"
DB = "db_tarefas"


def _tasklist() -> TaskList:
    return TaskList(NotionClient(token=TOKEN), DB)


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
def test_listar_tarefas_delega_para_tasklist():
    responses.add(
        responses.POST,
        f"{NOTION_BASE_URL}/databases/{DB}/query",
        json={"results": [_pagina("t1", "A", "00. Inbox")], "has_more": False},
        status=200,
    )
    tarefas = svc.listar_tarefas(tasklist=_tasklist())
    assert [t.nome for t in tarefas] == ["A"]


@responses.activate
def test_listar_tarefas_filtra_por_status():
    responses.add(
        responses.POST,
        f"{NOTION_BASE_URL}/databases/{DB}/query",
        json={"results": [], "has_more": False},
        status=200,
    )
    svc.listar_tarefas(status="00. Inbox", tasklist=_tasklist())
    corpo = json.loads(responses.calls[0].request.body)
    assert corpo["filter"] == {"property": "Status", "status": {"equals": "00. Inbox"}}


@responses.activate
def test_listar_tarefas_repassa_filtros_amplos():
    responses.add(
        responses.POST,
        f"{NOTION_BASE_URL}/databases/{DB}/query",
        json={"results": [], "has_more": False},
        status=200,
    )
    svc.listar_tarefas(
        status="00. Inbox",
        duracao="Dias",
        areas=["a1"],
        tasklist=_tasklist(),
    )
    corpo = json.loads(responses.calls[0].request.body)
    assert corpo["filter"] == {
        "and": [
            {"property": "Status", "status": {"equals": "00. Inbox"}},
            {"property": "Duração", "status": {"equals": "Dias"}},
            {"property": "Áreas-da-Vida", "relation": {"contains": "a1"}},
        ]
    }


@responses.activate
def test_criar_tarefa_devolve_tarefa_criada():
    responses.add(
        responses.POST,
        f"{NOTION_BASE_URL}/pages",
        json=_pagina("novo", "Nova", "00. Inbox", duracao="Dias", areas=["a1"]),
        status=200,
    )
    tarefa = svc.criar_tarefa(
        "Nova",
        status="00. Inbox",
        duracao="Dias",
        areas=["a1"],
        tasklist=_tasklist(),
    )
    assert tarefa.id == "novo"
    assert tarefa.nome == "Nova"
    assert tarefa.duracao == "Dias"
    assert tarefa.areas == ["a1"]


@responses.activate
def test_editar_tarefa_delega_campos_amplos():
    responses.add(
        responses.PATCH,
        f"{NOTION_BASE_URL}/pages/t1",
        json=_pagina("t1", "Renomeada", "02. Fazendo", duracao="Poucas horas"),
        status=200,
    )
    tarefa = svc.editar_tarefa(
        "t1",
        nome="Renomeada",
        status="02. Fazendo",
        duracao="Poucas horas",
        tasklist=_tasklist(),
    )
    corpo = json.loads(responses.calls[0].request.body)
    assert corpo["properties"]["Nome"]["title"][0]["text"]["content"] == "Renomeada"
    assert corpo["properties"]["Duração"]["status"]["name"] == "Poucas horas"
    assert tarefa.nome == "Renomeada"


@responses.activate
def test_mover_status_faz_patch():
    responses.add(
        responses.PATCH,
        f"{NOTION_BASE_URL}/pages/t1",
        json=_pagina("t1", "A", "02. Fazendo"),
        status=200,
    )
    tarefa = svc.mover_status("t1", "02. Fazendo", tasklist=_tasklist())
    assert tarefa.status == "02. Fazendo"


@responses.activate
def test_concluir_tarefa_usa_status_informado():
    responses.add(
        responses.PATCH,
        f"{NOTION_BASE_URL}/pages/t1",
        json=_pagina("t1", "A", "06. Feito"),
        status=200,
    )
    tarefa = svc.concluir_tarefa("t1", "06. Feito", tasklist=_tasklist())
    assert tarefa.status == "06. Feito"


@responses.activate
def test_listar_opcoes_delega_para_tasklist():
    responses.add(
        responses.GET,
        f"{NOTION_BASE_URL}/databases/{DB}",
        json={
            "properties": {
                "Status": {
                    "type": "status",
                    "status": {"options": [{"name": "00. Inbox"}]},
                },
                "Duração": {
                    "type": "status",
                    "status": {"options": [{"name": "Dias"}]},
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
    assert svc.listar_opcoes(tasklist=_tasklist()) == {
        "status": ["00. Inbox"],
        "duracao": ["Dias"],
        "areas": [{"id": "a1", "nome": "Estudos"}],
    }
