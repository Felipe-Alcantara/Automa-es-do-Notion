"""Testes da CLI para IA.

A CLI é testada por injeção de doubles de ``TaskList``/``NotionClient``: sem
token, sem rede e sem tocar no Notion real.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest import mock

from cli import notion_tasks as cli
from notion_starter import Tarefa


class FakeTaskList:
    def __init__(self) -> None:
        self.chamadas: list[tuple[str, object]] = []

    def listar(self, status=None, duracao=None, areas=None):
        self.chamadas.append(("listar", (status, duracao, areas)))
        return [
            Tarefa(
                id="t1",
                nome="Estudar",
                status=status or "00. Inbox",
                prazo="2026-07-01",
                duracao=duracao or "Dias",
                areas=areas or ["a1"],
                areas_nomes=["Estudos"],
                url="https://notion.so/t1",
            )
        ]

    def criar(self, nome, status=None, prazo=None, duracao=None, areas=None):
        self.chamadas.append(("criar", (nome, status, prazo, duracao, areas)))
        return Tarefa(
            id="novo",
            nome=nome,
            status=status,
            prazo=prazo,
            duracao=duracao,
            areas=areas or [],
            url="https://notion.so/novo",
        )

    def editar(self, task_id, *, nome=None, status=None, prazo=None, duracao=None, areas=None):
        self.chamadas.append(("editar", (task_id, nome, status, prazo, duracao, areas)))
        return Tarefa(
            id=task_id,
            nome=nome or "Editada",
            status=status,
            prazo=prazo,
            duracao=duracao,
            areas=areas or [],
            url=f"https://notion.so/{task_id}",
        )

    def atualizar_status(self, task_id, status):
        self.chamadas.append(("atualizar_status", (task_id, status)))
        return Tarefa(id=task_id, nome="Movida", status=status, url=f"https://notion.so/{task_id}")

    def concluir(self, task_id, status_concluido):
        self.chamadas.append(("concluir", (task_id, status_concluido)))
        return Tarefa(
            id=task_id,
            nome="Concluída",
            status=status_concluido,
            url=f"https://notion.so/{task_id}",
        )

    def opcoes(self):
        self.chamadas.append(("opcoes", None))
        return {
            "status": ["00. Inbox", "06. Feito"],
            "duracao": ["Dias"],
            "areas": [{"id": "a1", "nome": "Estudos"}],
        }


class FakeClient:
    def buscar(self, query=None, page_size=100, buscar_todos=False, filtro=None):
        if filtro == {"property": "object", "value": "database"}:
            return [
                {
                    "id": "db1",
                    "object": "database",
                    "title": [{"plain_text": "Tarefas"}],
                    "url": "https://notion.so/db1",
                }
            ]
        return [
            {
                "id": "p1",
                "object": "page",
                "parent": {"type": "workspace", "workspace": True},
                "properties": {"Nome": {"type": "title", "title": [{"plain_text": "Home"}]}},
            },
            {
                "id": "db1",
                "object": "database",
                "parent": {"type": "page_id", "page_id": "p1"},
                "title": [{"plain_text": "Tarefas"}],
            },
        ]


def _executar(args, fake: FakeTaskList | None = None):
    tasklist = fake or FakeTaskList()
    return cli.executar(args, tasklist_factory=lambda: tasklist, client_factory=FakeClient)


def test_listar_json_emite_envelope_estavel():
    codigo, saida = _executar(
        ["--json", "listar", "--status", "00. Inbox", "--duracao", "Dias", "--area", "a1"]
    )
    assert codigo == 0
    assert saida["ok"] is True
    assert saida["dados"][0]["id"] == "t1"
    assert "bruto" not in saida["dados"][0]


def test_listar_delega_filtros_para_services():
    fake = FakeTaskList()
    codigo, _ = _executar(
        ["--json", "listar", "--status", "00. Inbox", "--duracao", "Dias", "--area", "a1,a2"],
        fake,
    )

    assert codigo == 0
    assert fake.chamadas == [("listar", ("00. Inbox", "Dias", ["a1", "a2"]))]


def test_criar_delega_campos_amplos_para_services():
    fake = FakeTaskList()
    codigo, saida = _executar(
        [
            "--json",
            "criar",
            "Nova tarefa",
            "--status",
            "00. Inbox",
            "--duracao",
            "Dias",
            "--area",
            "a1,a2",
        ],
        fake,
    )
    assert codigo == 0
    assert fake.chamadas == [("criar", ("Nova tarefa", "00. Inbox", None, "Dias", ["a1", "a2"]))]
    assert saida["dados"]["areas"] == ["a1", "a2"]


def test_editar_exige_ao_menos_um_campo():
    codigo, saida = _executar(["--json", "editar", "t1"])
    assert codigo == 2
    assert saida == {
        "ok": False,
        "erro": {"mensagem": "Informe ao menos um campo para editar."},
    }


def test_mover_e_concluir_delegam_para_tasklist():
    fake = FakeTaskList()
    codigo_mover, _ = _executar(["mover", "t1", "02. Fazendo"], fake)
    codigo_concluir, _ = _executar(["concluir", "t1", "06. Feito"], fake)
    assert codigo_mover == 0
    assert codigo_concluir == 0
    assert fake.chamadas == [
        ("atualizar_status", ("t1", "02. Fazendo")),
        ("concluir", ("t1", "06. Feito")),
    ]


def test_ler_busca_tarefa_por_id():
    codigo, saida = _executar(["--json", "ler", "t1"])
    assert codigo == 0
    assert saida["dados"]["nome"] == "Estudar"


def test_ler_retorna_erro_quando_nao_encontra():
    codigo, saida = _executar(["--json", "ler", "inexistente"])
    assert codigo == 2
    assert saida["erro"]["mensagem"] == "Tarefa não encontrada."


def test_opcoes_retorna_json_dos_seletores():
    codigo, saida = _executar(["--json", "opcoes"])
    assert codigo == 0
    assert saida["dados"]["status"] == ["00. Inbox", "06. Feito"]


def test_databases_lista_databases_visiveis():
    codigo, saida = _executar(["--json", "databases"])
    assert codigo == 0
    assert saida["dados"] == [{"id": "db1", "titulo": "Tarefas", "url": "https://notion.so/db1"}]


def test_mapear_resume_workspace():
    codigo, saida = _executar(["--json", "mapear"])
    assert codigo == 0
    assert saida["dados"]["total_itens"] == 2
    assert saida["dados"]["total_paginas"] == 1
    assert saida["dados"]["total_databases"] == 1


def test_escolher_database_grava_env_file(tmp_path: Path):
    env_file = tmp_path / ".env"
    salvar_database_env = cli._salvar_database_env
    with (
        mock.patch.object(cli, "RAIZ", tmp_path),
        mock.patch.object(
            cli,
            "_salvar_database_env",
            wraps=lambda db_id: salvar_database_env(db_id, env_file),
        ),
    ):
        codigo, saida = _executar(["--json", "escolher-database", "db_novo"])
    assert codigo == 0
    assert env_file.read_text(encoding="utf-8") == "NOTION_DATABASE_ID=db_novo\n"
    assert saida["dados"]["database_id"] == "db_novo"


def test_main_imprime_json(capsys):
    with mock.patch.object(cli, "executar", return_value=(0, {"ok": True, "dados": []})):
        codigo = cli.main(["--json", "listar"])
    assert codigo == 0
    assert json.loads(capsys.readouterr().out) == {"ok": True, "dados": []}
