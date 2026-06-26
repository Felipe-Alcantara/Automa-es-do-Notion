"""Testes dos casos de uso de conteúdo (``services.conteudo``).

O :class:`NotionClient` é injetado e o HTTP do Notion é mockado com
``responses`` — sem token nem rede real. Verifica que cada caso de uso delega à
camada de conteúdo e devolve o resultado normalizado, incluindo o fluxo
destrutivo (``excluir_bloco``).
"""

from __future__ import annotations

import json

import pytest
import responses
from services import conteudo as svc

from notion_starter import NotionClient
from notion_starter.constants import NOTION_BASE_URL

TOKEN = "ntn_test_token"


def _cliente() -> NotionClient:
    return NotionClient(token=TOKEN, max_retries=0)


@responses.activate
def test_ler_conteudo_devolve_markdown():
    responses.add(
        responses.GET,
        f"{NOTION_BASE_URL}/blocks/page1/children",
        json={
            "results": [
                {"type": "heading_1", "heading_1": {"rich_text": [{"plain_text": "T"}]}},
                {"type": "paragraph", "paragraph": {"rich_text": [{"plain_text": "oi"}]}},
            ],
            "has_more": False,
        },
        status=200,
    )
    assert svc.ler_conteudo("page1", cliente=_cliente()) == "# T\n\noi"


@responses.activate
def test_escrever_conteudo_anexa_e_conta_blocos():
    responses.add(
        responses.PATCH,
        f"{NOTION_BASE_URL}/blocks/page1/children",
        json={"results": []},
        status=200,
    )
    total = svc.escrever_conteudo("page1", "linha um\nlinha dois", cliente=_cliente())
    assert total == 2
    corpo = json.loads(responses.calls[0].request.body)
    assert len(corpo["children"]) == 2


def test_escrever_conteudo_vazio_levanta():
    with pytest.raises(ValueError):
        svc.escrever_conteudo("page1", "   ", cliente=_cliente())


@responses.activate
def test_editar_bloco_envia_so_o_primeiro_bloco():
    responses.add(
        responses.PATCH,
        f"{NOTION_BASE_URL}/blocks/b1",
        json={"id": "b1"},
        status=200,
    )
    svc.editar_bloco("b1", "## Novo título", cliente=_cliente())
    corpo = json.loads(responses.calls[0].request.body)
    assert "heading_2" in corpo


@responses.activate
def test_excluir_bloco_delega_delete():
    responses.add(
        responses.DELETE,
        f"{NOTION_BASE_URL}/blocks/b1",
        json={"id": "b1", "archived": True},
        status=200,
    )
    resultado = svc.excluir_bloco("b1", cliente=_cliente())
    assert resultado["archived"] is True
    assert responses.calls[0].request.method == "DELETE"


@responses.activate
def test_buscar_normaliza_paginas_e_databases():
    responses.add(
        responses.POST,
        f"{NOTION_BASE_URL}/search",
        json={
            "results": [
                {
                    "object": "page",
                    "id": "p1",
                    "url": "https://notion.so/p1",
                    "properties": {
                        "Name": {"type": "title", "title": [{"plain_text": "Nota"}]}
                    },
                },
                {
                    "object": "database",
                    "id": "d1",
                    "url": "https://notion.so/d1",
                    "title": [{"plain_text": "Tarefas"}],
                },
            ],
            "has_more": False,
        },
        status=200,
    )
    itens = svc.buscar("x", cliente=_cliente())
    assert itens[0] == {
        "id": "p1",
        "tipo": "page",
        "titulo": "Nota",
        "url": "https://notion.so/p1",
    }
    assert itens[1]["titulo"] == "Tarefas"
