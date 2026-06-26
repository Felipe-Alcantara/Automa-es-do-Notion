"""Testes da camada de conteúdo: blocos no NotionClient + conversor Markdown."""

from __future__ import annotations

import json

import pytest
import responses

from notion_starter import (
    NotionClient,
    blocos_para_markdown,
    markdown_para_blocos,
)
from notion_starter.constants import NOTION_BASE_URL
from notion_starter.exceptions import NotionConfigurationError

TOKEN = "ntn_test_token"


def criar_client() -> NotionClient:
    return NotionClient(token=TOKEN, max_retries=0)


# -- Conversor Markdown -> blocos ------------------------------------------


def test_markdown_para_blocos_tipos_comuns():
    md = (
        "# Título\n"
        "## Sub\n"
        "Um parágrafo.\n"
        "- item a\n"
        "1. passo um\n"
        "- [ ] pendente\n"
        "- [x] feito\n"
        "> citação\n"
        "---"
    )
    blocos = markdown_para_blocos(md)
    tipos = [b["type"] for b in blocos]
    assert tipos == [
        "heading_1",
        "heading_2",
        "paragraph",
        "bulleted_list_item",
        "numbered_list_item",
        "to_do",
        "to_do",
        "quote",
        "divider",
    ]
    assert blocos[5]["to_do"]["checked"] is False
    assert blocos[6]["to_do"]["checked"] is True
    assert blocos[0]["heading_1"]["rich_text"][0]["text"]["content"] == "Título"


def test_markdown_para_blocos_bloco_de_codigo_preserva_linhas():
    md = "```python\nx = 1\ny = 2\n```"
    blocos = markdown_para_blocos(md)
    assert len(blocos) == 1
    assert blocos[0]["type"] == "code"
    assert blocos[0]["code"]["language"] == "python"
    assert blocos[0]["code"]["rich_text"][0]["text"]["content"] == "x = 1\ny = 2"


def test_markdown_para_blocos_ignora_linhas_em_branco():
    blocos = markdown_para_blocos("a\n\n\nb")
    assert [b["type"] for b in blocos] == ["paragraph", "paragraph"]


# -- Conversor blocos -> Markdown (ida e volta) ----------------------------


def test_blocos_para_markdown_round_trip():
    md = "# Título\n\nUm parágrafo.\n\n- item\n\n- [x] feito"
    blocos = markdown_para_blocos(md)
    # Reidrata ``plain_text`` como a API faria, para exercitar a leitura.
    for bloco in blocos:
        corpo = bloco[bloco["type"]]
        for rt in corpo.get("rich_text", []):
            rt["plain_text"] = rt["text"]["content"]
    assert blocos_para_markdown(blocos) == md


def test_blocos_para_markdown_tipo_desconhecido_vira_paragrafo():
    blocos = [
        {
            "type": "callout",
            "callout": {"rich_text": [{"plain_text": "aviso"}]},
        }
    ]
    assert blocos_para_markdown(blocos) == "aviso"


# -- Blocos no NotionClient ------------------------------------------------


@responses.activate
def test_ler_blocos_pagina_unica():
    responses.add(
        responses.GET,
        f"{NOTION_BASE_URL}/blocks/page1/children",
        json={"results": [{"id": "b1", "type": "paragraph"}], "has_more": False},
        status=200,
    )
    blocos = criar_client().ler_blocos("page1")
    assert blocos[0]["id"] == "b1"


@responses.activate
def test_ler_blocos_pagina_todos_segue_cursor():
    responses.add(
        responses.GET,
        f"{NOTION_BASE_URL}/blocks/page1/children",
        json={"results": [{"id": "b1"}], "has_more": True, "next_cursor": "cur2"},
        status=200,
    )
    responses.add(
        responses.GET,
        f"{NOTION_BASE_URL}/blocks/page1/children",
        json={"results": [{"id": "b2"}], "has_more": False},
        status=200,
    )
    blocos = criar_client().ler_blocos("page1", buscar_todos=True)
    assert [b["id"] for b in blocos] == ["b1", "b2"]
    assert "start_cursor=cur2" in responses.calls[1].request.url


@responses.activate
def test_anexar_blocos_envia_children():
    responses.add(
        responses.PATCH,
        f"{NOTION_BASE_URL}/blocks/page1/children",
        json={"results": []},
        status=200,
    )
    criar_client().anexar_blocos("page1", markdown_para_blocos("oi"))
    corpo = json.loads(responses.calls[0].request.body)
    assert corpo["children"][0]["type"] == "paragraph"


def test_anexar_blocos_vazio_levanta():
    with pytest.raises(ValueError):
        criar_client().anexar_blocos("page1", [])


@responses.activate
def test_atualizar_bloco_envia_payload():
    responses.add(
        responses.PATCH,
        f"{NOTION_BASE_URL}/blocks/b1",
        json={"id": "b1"},
        status=200,
    )
    criar_client().atualizar_bloco(
        "b1", {"paragraph": {"rich_text": [{"text": {"content": "novo"}}]}}
    )
    corpo = json.loads(responses.calls[0].request.body)
    assert corpo["paragraph"]["rich_text"][0]["text"]["content"] == "novo"


@responses.activate
def test_excluir_bloco_usa_delete():
    responses.add(
        responses.DELETE,
        f"{NOTION_BASE_URL}/blocks/b1",
        json={"id": "b1", "archived": True},
        status=200,
    )
    resultado = criar_client().excluir_bloco("b1")
    assert resultado["archived"] is True
    assert responses.calls[0].request.method == "DELETE"


def test_excluir_bloco_id_vazio_levanta():
    with pytest.raises(NotionConfigurationError):
        criar_client().excluir_bloco("   ")
