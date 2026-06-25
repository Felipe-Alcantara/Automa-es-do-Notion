"""Testes do servidor MCP (``server/mcp_server.py``).

Cada ferramenta e testada com o Notion mockado via ``responses`` — sem token
nem rede real.  A ``TaskList`` e injetada diretamente, seguindo o mesmo padrao
de DI dos testes de ``services.tarefas``.

Tambem verifica que as anotacoes MCP (``readOnlyHint``, ``openWorldHint``)
estao corretas, garantindo que o Felixo-AI-Core receba os sinais certos
sobre quais ferramentas requerem confirmacao.
"""

from __future__ import annotations

import asyncio
import json
import os
from unittest import mock

import pytest
import responses

# Importa o modulo do servidor MCP (server/ ja esta no sys.path via conftest).
from mcp_server import (
    _criar_tasklist,
    _resolver_transporte,
    _tarefa_dict,
    conclude_task,
    create_task,
    list_tasks,
    main,
    mcp,
    move_status,
    update_project_page,
)

from notion_starter import NotionClient, NotionConfigurationError, TaskList
from notion_starter.constants import NOTION_BASE_URL

TOKEN = "ntn_test_token"
DB = "db_mcp_test"


def _tasklist() -> TaskList:
    return TaskList(NotionClient(token=TOKEN), DB)


def _pagina(id_: str, nome: str, status: str | None = None, prazo: str | None = None):
    props: dict = {"Nome": {"type": "title", "title": [{"plain_text": nome}]}}
    if status is not None:
        props["Status"] = {"type": "status", "status": {"name": status}}
    if prazo is not None:
        props["Próximo prazo"] = {"type": "date", "date": {"start": prazo}}
    return {"id": id_, "url": f"https://notion.so/{id_}", "properties": props}


# ---------------------------------------------------------------------------
# Anotacoes MCP
# ---------------------------------------------------------------------------


class TestAnotacoesMCP:
    """Verifica que as ferramentas declaram as anotacoes certas."""

    def _tools(self):
        return {tool.name: tool for tool in asyncio.run(mcp.list_tools())}

    def test_list_tasks_e_read_only(self):
        ann = self._tools()["notion.list_tasks"].annotations
        assert ann.readOnlyHint is True
        assert ann.destructiveHint is False
        assert ann.openWorldHint is True

    def test_create_task_e_write(self):
        ann = self._tools()["notion.create_task"].annotations
        assert ann.readOnlyHint is False
        assert ann.destructiveHint is False
        assert ann.idempotentHint is False
        assert ann.openWorldHint is True

    def test_move_status_e_write(self):
        ann = self._tools()["notion.move_status"].annotations
        assert ann.readOnlyHint is False
        assert ann.destructiveHint is False
        assert ann.idempotentHint is True
        assert ann.openWorldHint is True

    def test_conclude_task_e_write(self):
        ann = self._tools()["notion.conclude_task"].annotations
        assert ann.readOnlyHint is False
        assert ann.destructiveHint is False
        assert ann.idempotentHint is True
        assert ann.openWorldHint is True

    def test_update_project_page_e_write(self):
        ann = self._tools()["notion.update_project_page"].annotations
        assert ann.readOnlyHint is False
        assert ann.destructiveHint is False
        assert ann.idempotentHint is True
        assert ann.openWorldHint is True

    def test_superficie_publica_tem_namespace_notion(self):
        assert set(self._tools()) == {
            "notion.list_tasks",
            "notion.create_task",
            "notion.move_status",
            "notion.conclude_task",
            "notion.update_project_page",
        }


# ---------------------------------------------------------------------------
# Serializacao
# ---------------------------------------------------------------------------


class TestSerializacao:
    """Verifica o helper ``_tarefa_dict``."""

    def test_tarefa_para_dict_campos_corretos(self):
        from notion_starter import Tarefa

        t = Tarefa(
            id="abc",
            nome="Teste",
            status="Inbox",
            prazo="2026-07-01",
            url="https://notion.so/abc",
            bruto={},
        )
        d = _tarefa_dict(t)
        assert d == {
            "id": "abc",
            "nome": "Teste",
            "status": "Inbox",
            "prazo": "2026-07-01",
            "url": "https://notion.so/abc",
        }

    def test_tarefa_para_dict_sem_bruto(self):
        from notion_starter import Tarefa

        t = Tarefa(id="x", nome="N", status=None, prazo=None, url="u", bruto={"segredo": 42})
        d = _tarefa_dict(t)
        assert "bruto" not in d
        assert "segredo" not in d


# ---------------------------------------------------------------------------
# _criar_tasklist
# ---------------------------------------------------------------------------


class TestCriarTasklist:
    """Verifica que ``_criar_tasklist`` exige as variaveis de ambiente."""

    def test_erro_sem_token(self):
        ambiente = {"NOTION_TOKEN": "", "NOTION_DATABASE_ID": "db"}
        with (
            mock.patch.dict(os.environ, ambiente, clear=False),
            pytest.raises(NotionConfigurationError, match="NOTION_TOKEN"),
        ):
            _criar_tasklist()

    def test_erro_sem_database_id(self):
        ambiente = {"NOTION_TOKEN": "ntn_x", "NOTION_DATABASE_ID": ""}
        with (
            mock.patch.dict(os.environ, ambiente, clear=False),
            pytest.raises(NotionConfigurationError, match="NOTION_DATABASE_ID"),
        ):
            _criar_tasklist()

    def test_cria_tasklist_com_env_ok(self):
        ambiente = {"NOTION_TOKEN": TOKEN, "NOTION_DATABASE_ID": DB}
        with mock.patch.dict(os.environ, ambiente, clear=False):
            tl = _criar_tasklist()
            assert tl is not None


# ---------------------------------------------------------------------------
# Validacao da borda MCP
# ---------------------------------------------------------------------------


class TestValidacao:
    """Entradas invalidas falham antes de tocar no Notion."""

    def test_create_task_exige_nome(self):
        with (
            mock.patch("mcp_server._criar_tasklist") as criar_tasklist,
            pytest.raises(ValueError, match="nome"),
        ):
            create_task(nome="   ")
        criar_tasklist.assert_not_called()

    def test_move_status_exige_task_id(self):
        with (
            mock.patch("mcp_server._criar_tasklist") as criar_tasklist,
            pytest.raises(ValueError, match="task_id"),
        ):
            move_status(task_id="", status="Fazendo")
        criar_tasklist.assert_not_called()

    def test_move_status_exige_status(self):
        with (
            mock.patch("mcp_server._criar_tasklist") as criar_tasklist,
            pytest.raises(ValueError, match="status"),
        ):
            move_status(task_id="t1", status=" ")
        criar_tasklist.assert_not_called()

    def test_erro_de_configuracao_e_sanitizado_na_ferramenta(self):
        erro = NotionConfigurationError("token-interno-nao-deve-vazar")
        with (
            mock.patch("mcp_server._criar_tasklist", side_effect=erro),
            pytest.raises(RuntimeError, match="nao configurado") as exc_info,
        ):
            list_tasks()
        assert "token-interno" not in str(exc_info.value)

    def test_update_project_page_rejeita_contagem_negativa(self):
        with (
            mock.patch("mcp_server._criar_notion_client") as criar_cliente,
            pytest.raises(ValueError, match="estrelas"),
        ):
            update_project_page(
                page_id="projeto-1",
                nome_completo="felipe/projeto",
                estrelas=-1,
            )
        criar_cliente.assert_not_called()


# ---------------------------------------------------------------------------
# Ferramentas MCP (funcoes puras, Notion mockado)
# ---------------------------------------------------------------------------


class TestListTasks:
    """Testes da ferramenta ``list_tasks``."""

    @responses.activate
    def test_lista_todas_as_tarefas(self):
        responses.add(
            responses.POST,
            f"{NOTION_BASE_URL}/databases/{DB}/query",
            json={
                "results": [_pagina("t1", "A", "Inbox"), _pagina("t2", "B", "Fazendo")],
                "has_more": False,
            },
            status=200,
        )
        with mock.patch("mcp_server._criar_tasklist", return_value=_tasklist()):
            resultado = list_tasks()
        assert len(resultado) == 2
        assert resultado[0]["nome"] == "A"
        assert resultado[1]["nome"] == "B"

    @responses.activate
    def test_filtra_por_status(self):
        responses.add(
            responses.POST,
            f"{NOTION_BASE_URL}/databases/{DB}/query",
            json={"results": [_pagina("t1", "A", "Inbox")], "has_more": False},
            status=200,
        )
        with mock.patch("mcp_server._criar_tasklist", return_value=_tasklist()):
            resultado = list_tasks(status="Inbox")
        corpo = json.loads(responses.calls[0].request.body)
        assert corpo["filter"]["status"]["equals"] == "Inbox"
        assert len(resultado) == 1

    @responses.activate
    def test_lista_vazia(self):
        responses.add(
            responses.POST,
            f"{NOTION_BASE_URL}/databases/{DB}/query",
            json={"results": [], "has_more": False},
            status=200,
        )
        with mock.patch("mcp_server._criar_tasklist", return_value=_tasklist()):
            resultado = list_tasks()
        assert resultado == []


class TestCreateTask:
    """Testes da ferramenta ``create_task``."""

    @responses.activate
    def test_cria_tarefa_simples(self):
        responses.add(
            responses.POST,
            f"{NOTION_BASE_URL}/pages",
            json=_pagina("novo", "Estudar IA", "Inbox"),
            status=200,
        )
        with mock.patch("mcp_server._criar_tasklist", return_value=_tasklist()):
            resultado = create_task(nome="Estudar IA")
        assert resultado["id"] == "novo"
        assert resultado["nome"] == "Estudar IA"

    @responses.activate
    def test_cria_tarefa_com_status_e_prazo(self):
        responses.add(
            responses.POST,
            f"{NOTION_BASE_URL}/pages",
            json=_pagina("t2", "Revisar PR", "Fazendo", "2026-07-01"),
            status=200,
        )
        with mock.patch("mcp_server._criar_tasklist", return_value=_tasklist()):
            resultado = create_task(nome="Revisar PR", status="Fazendo", prazo="2026-07-01")
        assert resultado["status"] == "Fazendo"
        assert resultado["prazo"] == "2026-07-01"


class TestMoveStatus:
    """Testes da ferramenta ``move_status``."""

    @responses.activate
    def test_move_status_com_sucesso(self):
        responses.add(
            responses.PATCH,
            f"{NOTION_BASE_URL}/pages/t1",
            json=_pagina("t1", "A", "Fazendo"),
            status=200,
        )
        with mock.patch("mcp_server._criar_tasklist", return_value=_tasklist()):
            resultado = move_status(task_id="t1", status="Fazendo")
        assert resultado["status"] == "Fazendo"


class TestConcludeTask:
    """Testes da ferramenta ``conclude_task``."""

    @responses.activate
    def test_conclui_tarefa_com_sucesso(self):
        responses.add(
            responses.PATCH,
            f"{NOTION_BASE_URL}/pages/t1",
            json=_pagina("t1", "A", "06. Feito"),
            status=200,
        )
        with mock.patch("mcp_server._criar_tasklist", return_value=_tasklist()):
            resultado = conclude_task(task_id="t1", status_concluido="06. Feito")
        assert resultado["status"] == "06. Feito"


class TestUpdateProjectPage:
    """Testes da ferramenta ``update_project_page``."""

    @responses.activate
    def test_atualiza_pagina_com_metadados_normalizados(self):
        responses.add(
            responses.PATCH,
            f"{NOTION_BASE_URL}/pages/projeto-1",
            json={
                "id": "projeto-1",
                "url": "https://notion.so/projeto-1",
                "properties": {},
            },
            status=200,
        )
        with mock.patch(
            "mcp_server._criar_notion_client",
            return_value=NotionClient(token=TOKEN),
        ):
            resultado = update_project_page(
                page_id="projeto-1",
                nome_completo="felipe/projeto",
                descricao="Estado atual",
                linguagem="Python",
                topicos=["notion", " mcp "],
                estrelas=4,
                forks=1,
            )

        corpo = json.loads(responses.calls[0].request.body)
        propriedades = corpo["properties"]
        assert propriedades["Nome"]["title"][0]["text"]["content"] == "felipe/projeto"
        assert propriedades["Descrição"]["rich_text"][0]["text"]["content"] == "Estado atual"
        assert propriedades["Tópicos"]["multi_select"] == [
            {"name": "notion"},
            {"name": "mcp"},
        ]
        assert resultado == {
            "id": "projeto-1",
            "url": "https://notion.so/projeto-1",
        }


# ---------------------------------------------------------------------------
# Servidor MCP: metadata
# ---------------------------------------------------------------------------


class TestMetadataServidor:
    """Verifica propriedades do servidor MCP."""

    def test_nome_do_servidor(self):
        assert mcp.name == "notion"

    def test_instructions_menciona_confirmacao(self):
        assert "confirmacao" in mcp.instructions.lower()


# ---------------------------------------------------------------------------
# CLI / transportes
# ---------------------------------------------------------------------------


class TestCLI:
    """Verifica o transporte efetivamente passado ao SDK MCP."""

    def test_transporte_padrao_e_stdio(self):
        assert _resolver_transporte([]) == "stdio"

    def test_transporte_http_e_resolvido(self):
        assert _resolver_transporte(["--transport", "streamable-http"]) == "streamable-http"

    def test_transporte_invalido_falha(self):
        with pytest.raises(SystemExit):
            _resolver_transporte(["--transport", "websocket"])

    def test_main_repassa_transporte_ao_sdk(self):
        with mock.patch.object(mcp, "run") as run:
            main(["--transport", "streamable-http"])
        run.assert_called_once_with(transport="streamable-http")
