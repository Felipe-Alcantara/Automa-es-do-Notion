from __future__ import annotations

import json

import responses

from notion_starter import CamposTarefa, NotionClient, TaskList, tarefa_de_pagina
from notion_starter.constants import NOTION_BASE_URL

TOKEN = "ntn_test_token"
DB = "db_tarefas"


def criar_tasklist() -> TaskList:
    return TaskList(NotionClient(token=TOKEN), DB)


def pagina_tarefa(id_, nome, status=None, prazo=None, duracao=None, areas=None):
    """Monta o JSON cru de uma página de tarefa como vem do Notion."""
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
            "relation": [{"id": aid} for aid in areas],
        }
    return {"id": id_, "url": f"https://notion.so/{id_}", "properties": props}


# -- Normalização ----------------------------------------------------------


def test_tarefa_de_pagina_extrai_campos():
    t = tarefa_de_pagina(
        pagina_tarefa(
            "t1", "Estudar", "00. Inbox", "2026-07-01",
            duracao="Dias", areas=["area-1"],
        ),
        CamposTarefa(),
    )
    assert t.id == "t1"
    assert t.nome == "Estudar"
    assert t.status == "00. Inbox"
    assert t.prazo == "2026-07-01"
    assert t.duracao == "Dias"
    assert t.areas == ["area-1"]
    assert t.areas_nomes == []  # puro, sem enriquecimento


def test_tarefa_de_pagina_lida_com_campos_ausentes():
    t = tarefa_de_pagina(pagina_tarefa("t1", "Sem status"), CamposTarefa())
    assert t.status is None
    assert t.prazo is None
    assert t.duracao is None
    assert t.areas == []


def test_campos_configuraveis():
    pagina = {
        "id": "t1",
        "properties": {"Título": {"type": "title", "title": [{"plain_text": "X"}]}},
    }
    t = tarefa_de_pagina(pagina, CamposTarefa(nome="Título"))
    assert t.nome == "X"


# -- Listar ----------------------------------------------------------------


@responses.activate
def test_listar_retorna_tarefas():
    responses.add(
        responses.POST,
        f"{NOTION_BASE_URL}/databases/{DB}/query",
        json={"results": [pagina_tarefa("t1", "A", "00. Inbox")], "has_more": False},
        status=200,
    )
    tarefas = criar_tasklist().listar()
    assert [t.nome for t in tarefas] == ["A"]


@responses.activate
def test_listar_por_status_envia_filtro():
    responses.add(
        responses.POST,
        f"{NOTION_BASE_URL}/databases/{DB}/query",
        json={"results": [], "has_more": False},
        status=200,
    )
    criar_tasklist().listar(status="00. Inbox")
    corpo = json.loads(responses.calls[0].request.body)
    assert corpo["filter"] == {
        "property": "Status",
        "status": {"equals": "00. Inbox"},
    }


# -- Criar -----------------------------------------------------------------


@responses.activate
def test_criar_envia_propriedades():
    responses.add(
        responses.POST,
        f"{NOTION_BASE_URL}/pages",
        json=pagina_tarefa("novo", "Nova tarefa", "00. Inbox"),
        status=200,
    )
    t = criar_tasklist().criar("Nova tarefa", status="00. Inbox", prazo="2026-07-01")
    corpo = json.loads(responses.calls[0].request.body)
    assert corpo["parent"]["database_id"] == DB
    assert corpo["properties"]["Nome"]["title"][0]["text"]["content"] == "Nova tarefa"
    assert corpo["properties"]["Status"]["status"]["name"] == "00. Inbox"
    assert corpo["properties"]["Próximo prazo"]["date"]["start"] == "2026-07-01"
    assert t.id == "novo"


# -- Atualizar / concluir --------------------------------------------------


@responses.activate
def test_atualizar_status_faz_patch():
    responses.add(
        responses.PATCH,
        f"{NOTION_BASE_URL}/pages/t1",
        json=pagina_tarefa("t1", "A", "06. Feito"),
        status=200,
    )
    t = criar_tasklist().atualizar_status("t1", "06. Feito")
    corpo = json.loads(responses.calls[0].request.body)
    assert corpo["properties"]["Status"]["status"]["name"] == "06. Feito"
    assert t.status == "06. Feito"


@responses.activate
def test_concluir_usa_status_informado():
    responses.add(
        responses.PATCH,
        f"{NOTION_BASE_URL}/pages/t1",
        json=pagina_tarefa("t1", "A", "06. Feito"),
        status=200,
    )
    t = criar_tasklist().concluir("t1", "06. Feito")
    assert t.status == "06. Feito"


# -- Criar com duracao/areas ------------------------------------------------


@responses.activate
def test_criar_com_duracao_e_areas():
    responses.add(
        responses.POST,
        f"{NOTION_BASE_URL}/pages",
        json=pagina_tarefa("novo", "Tarefa", duracao="Dias", areas=["a1"]),
        status=200,
    )
    t = criar_tasklist().criar("Tarefa", duracao="Dias", areas=["a1"])
    corpo = json.loads(responses.calls[0].request.body)
    assert corpo["properties"]["Duração"]["status"]["name"] == "Dias"
    assert corpo["properties"]["Áreas-da-Vida"]["relation"] == [{"id": "a1"}]
    assert t.duracao == "Dias"
    assert t.areas == ["a1"]


# -- Editar ----------------------------------------------------------------


@responses.activate
def test_editar_envia_campos_parciais():
    responses.add(
        responses.PATCH,
        f"{NOTION_BASE_URL}/pages/t1",
        json=pagina_tarefa("t1", "Renomeada", "02. ASAP", duracao="Poucas horas"),
        status=200,
    )
    t = criar_tasklist().editar(
        "t1", nome="Renomeada", status="02. ASAP", duracao="Poucas horas"
    )
    corpo = json.loads(responses.calls[0].request.body)
    assert corpo["properties"]["Nome"]["title"][0]["text"]["content"] == "Renomeada"
    assert corpo["properties"]["Status"]["status"]["name"] == "02. ASAP"
    assert corpo["properties"]["Duração"]["status"]["name"] == "Poucas horas"
    assert t.nome == "Renomeada"


@responses.activate
def test_editar_aceita_areas():
    responses.add(
        responses.PATCH,
        f"{NOTION_BASE_URL}/pages/t1",
        json=pagina_tarefa("t1", "A", areas=["a1", "a2"]),
        status=200,
    )
    criar_tasklist().editar("t1", areas=["a1", "a2"])
    corpo = json.loads(responses.calls[0].request.body)
    assert corpo["properties"]["Áreas-da-Vida"]["relation"] == [
        {"id": "a1"},
        {"id": "a2"},
    ]


def test_editar_sem_campos_levanta_erro():
    import pytest

    with pytest.raises(ValueError, match="Ao menos um campo"):
        criar_tasklist().editar("t1")


# -- Opções ----------------------------------------------------------------

AREAS_DB = "db_areas"

SCHEMA_TAREFAS = {
    "properties": {
        "Nome": {"type": "title", "title": {}},
        "Status": {
            "type": "status",
            "status": {
                "options": [
                    {"name": "00. Inbox", "color": "default"},
                    {"name": "06. Feito", "color": "green"},
                ],
            },
        },
        "Duração": {
            "type": "status",
            "status": {
                "options": [
                    {"name": "Minutos", "color": "blue"},
                    {"name": "Dias", "color": "orange"},
                ],
            },
        },
        "Áreas-da-Vida": {
            "type": "relation",
            "relation": {"database_id": AREAS_DB},
        },
    },
}


def pagina_area(id_, nome):
    return {
        "id": id_,
        "properties": {"Nome": {"type": "title", "title": [{"plain_text": nome}]}},
    }


@responses.activate
def test_opcoes_retorna_status_duracao_areas():
    responses.add(
        responses.GET,
        f"{NOTION_BASE_URL}/databases/{DB}",
        json=SCHEMA_TAREFAS,
        status=200,
    )
    responses.add(
        responses.POST,
        f"{NOTION_BASE_URL}/databases/{AREAS_DB}/query",
        json={
            "results": [pagina_area("a1", "Estudos"), pagina_area("a2", "Trabalho")],
            "has_more": False,
        },
        status=200,
    )
    opcoes = criar_tasklist().opcoes()
    assert opcoes["status"] == ["00. Inbox", "06. Feito"]
    assert opcoes["duracao"] == ["Minutos", "Dias"]
    assert opcoes["areas"] == [
        {"id": "a1", "nome": "Estudos"},
        {"id": "a2", "nome": "Trabalho"},
    ]


# -- Listar com enriquecimento de áreas ------------------------------------


@responses.activate
def test_listar_enriquece_areas_nomes():
    responses.add(
        responses.POST,
        f"{NOTION_BASE_URL}/databases/{DB}/query",
        json={
            "results": [pagina_tarefa("t1", "A", areas=["a1"])],
            "has_more": False,
        },
        status=200,
    )
    # Schema para descobrir o database de áreas
    responses.add(
        responses.GET,
        f"{NOTION_BASE_URL}/databases/{DB}",
        json=SCHEMA_TAREFAS,
        status=200,
    )
    # Consulta ao database de áreas
    responses.add(
        responses.POST,
        f"{NOTION_BASE_URL}/databases/{AREAS_DB}/query",
        json={"results": [pagina_area("a1", "Estudos")], "has_more": False},
        status=200,
    )
    tarefas = criar_tasklist().listar()
    assert tarefas[0].areas_nomes == ["Estudos"]
