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


def _pagina(id_, nome, status=None, prazo=None):
    props = {"Nome": {"type": "title", "title": [{"plain_text": nome}]}}
    if status is not None:
        props["Status"] = {"type": "status", "status": {"name": status}}
    if prazo is not None:
        props["Próximo prazo"] = {"type": "date", "date": {"start": prazo}}
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
def test_criar_tarefa_devolve_tarefa_criada():
    responses.add(
        responses.POST,
        f"{NOTION_BASE_URL}/pages",
        json=_pagina("novo", "Nova", "00. Inbox"),
        status=200,
    )
    tarefa = svc.criar_tarefa("Nova", status="00. Inbox", tasklist=_tasklist())
    assert tarefa.id == "novo"
    assert tarefa.nome == "Nova"


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
