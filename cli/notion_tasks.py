"""CLI para IA operar tarefas do Notion via ``server/services``.

Esta borda valida entradas, escolhe formato de saída e delega a regra para os
services compartilhados com API/MCP. Não monta payload cru do Notion.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Callable, Iterable, Sequence
from pathlib import Path
from typing import Any

RAIZ = Path(__file__).resolve().parents[1]
SERVER_DIR = RAIZ / "server"
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))

from core.config import carregar_env_file  # noqa: E402
from services import tarefas as svc  # noqa: E402

from notion_starter import (  # noqa: E402
    NotionAPIError,
    NotionClient,
    NotionConfigurationError,
    NotionHTTPError,
    TaskList,
    construir_inventario,
)

carregar_env_file()

TaskListFactory = Callable[[], TaskList]
ClientFactory = Callable[[], NotionClient]


class CLIError(RuntimeError):
    """Erro esperado de uso/configuração, seguro para exibir ao consumidor."""


def _criar_client() -> NotionClient:
    token = os.environ.get("NOTION_TOKEN", "").strip()
    if not token:
        raise CLIError("NOTION_TOKEN não configurado.")
    return NotionClient(token=token)


def _criar_tasklist() -> TaskList:
    database_id = os.environ.get("NOTION_DATABASE_ID", "").strip()
    if not database_id:
        raise CLIError("NOTION_DATABASE_ID não configurado.")
    return TaskList(_criar_client(), database_id)


def _normalizar_texto(valor: str | None) -> str | None:
    if valor is None:
        return None
    return valor.strip() or None


def _texto_obrigatorio(valor: str | None, campo: str) -> str:
    normalizado = _normalizar_texto(valor)
    if not normalizado:
        raise CLIError(f"O campo '{campo}' é obrigatório.")
    return normalizado


def _lista_csv(valores: Sequence[str] | None) -> list[str] | None:
    if not valores:
        return None
    itens: list[str] = []
    for valor in valores:
        itens.extend(item.strip() for item in valor.split(",") if item.strip())
    return itens


def _tarefa_dict(tarefa: Any) -> dict[str, Any]:
    return {
        "id": tarefa.id,
        "nome": tarefa.nome,
        "status": tarefa.status,
        "prazo": tarefa.prazo,
        "duracao": tarefa.duracao,
        "areas": tarefa.areas,
        "areas_nomes": tarefa.areas_nomes,
        "url": tarefa.url,
    }


def _database_titulo(item: dict[str, Any]) -> str:
    partes = item.get("title", [])
    titulo = "".join(parte.get("plain_text", "") for parte in partes).strip()
    return titulo or "(sem título)"


def _database_dict(item: dict[str, Any]) -> dict[str, Any]:
    return {"id": item.get("id", ""), "titulo": _database_titulo(item), "url": item.get("url")}


def _envelope(sucesso: bool, dados: Any = None, erro: str | None = None) -> dict[str, Any]:
    if sucesso:
        return {"ok": True, "dados": dados}
    return {"ok": False, "erro": {"mensagem": erro or "Erro desconhecido."}}


def _json(dados: Any) -> str:
    return json.dumps(dados, ensure_ascii=False, indent=2, sort_keys=True)


def _linhas_tabela(registros: Iterable[dict[str, Any]], colunas: Sequence[str]) -> list[str]:
    linhas = list(registros)
    if not linhas:
        return ["Nenhum item encontrado."]
    larguras = {
        coluna: max(len(coluna), *(len(str(item.get(coluna) or "")) for item in linhas))
        for coluna in colunas
    }
    cabecalho = "  ".join(coluna.ljust(larguras[coluna]) for coluna in colunas)
    separador = "  ".join("-" * larguras[coluna] for coluna in colunas)
    corpo = [
        "  ".join(str(item.get(coluna) or "").ljust(larguras[coluna]) for coluna in colunas)
        for item in linhas
    ]
    return [cabecalho, separador, *corpo]


def _formatar_humano(comando: str, dados: Any) -> str:
    if comando in {"listar", "ler", "criar", "editar", "mover", "concluir"}:
        tarefas = dados if isinstance(dados, list) else [dados]
        return "\n".join(
            _linhas_tabela(
                tarefas,
                ("id", "nome", "status", "duracao", "areas_nomes", "prazo", "url"),
            )
        )
    if comando == "opcoes":
        return _json(dados)
    if comando == "databases":
        return "\n".join(_linhas_tabela(dados, ("id", "titulo", "url")))
    if comando == "database-atual":
        return f"Database atual: {dados['database_id'] or '(não configurado)'}"
    if comando == "mapear":
        return (
            f"Itens: {dados['total_itens']} | páginas: {dados['total_paginas']} | "
            f"databases: {dados['total_databases']} | raízes: {dados['total_raizes']} | "
            f"duplicatas: {dados['total_duplicatas']} | órfãos: {dados['total_orfaos']}"
        )
    return _json(dados)


def _salvar_database_env(database_id: str, env_file: Path = RAIZ / ".env") -> None:
    linhas: list[str] = []
    if env_file.exists():
        linhas = env_file.read_text(encoding="utf-8").splitlines()
    chave = "NOTION_DATABASE_ID"
    nova_linha = f"{chave}={database_id}"
    atualizado = False
    for indice, linha in enumerate(linhas):
        if linha.startswith(f"{chave}="):
            linhas[indice] = nova_linha
            atualizado = True
            break
    if not atualizado:
        linhas.append(nova_linha)
    env_file.write_text("\n".join(linhas).rstrip() + "\n", encoding="utf-8")
    os.environ[chave] = database_id


def cmd_listar(args: argparse.Namespace, *, tasklist_factory: TaskListFactory) -> Any:
    tarefas = svc.listar_tarefas(
        status=_normalizar_texto(args.status),
        duracao=_normalizar_texto(args.duracao),
        areas=_lista_csv(args.area),
        tasklist=tasklist_factory(),
    )
    return [_tarefa_dict(tarefa) for tarefa in tarefas]


def cmd_ler(args: argparse.Namespace, *, tasklist_factory: TaskListFactory) -> Any:
    task_id = _texto_obrigatorio(args.task_id, "task_id")
    tarefas = svc.listar_tarefas(tasklist=tasklist_factory())
    for tarefa in tarefas:
        if tarefa.id == task_id:
            return _tarefa_dict(tarefa)
    raise CLIError("Tarefa não encontrada.")


def cmd_criar(args: argparse.Namespace, *, tasklist_factory: TaskListFactory) -> Any:
    tarefa = svc.criar_tarefa(
        _texto_obrigatorio(args.nome, "nome"),
        status=_normalizar_texto(args.status),
        prazo=_normalizar_texto(args.prazo),
        duracao=_normalizar_texto(args.duracao),
        areas=_lista_csv(args.area),
        tasklist=tasklist_factory(),
    )
    return _tarefa_dict(tarefa)


def cmd_editar(args: argparse.Namespace, *, tasklist_factory: TaskListFactory) -> Any:
    campos = {
        "nome": _normalizar_texto(args.nome),
        "status": _normalizar_texto(args.status),
        "prazo": _normalizar_texto(args.prazo),
        "duracao": _normalizar_texto(args.duracao),
        "areas": _lista_csv(args.area),
    }
    if all(valor is None for valor in campos.values()):
        raise CLIError("Informe ao menos um campo para editar.")
    tarefa = svc.editar_tarefa(
        _texto_obrigatorio(args.task_id, "task_id"),
        **campos,
        tasklist=tasklist_factory(),
    )
    return _tarefa_dict(tarefa)


def cmd_mover(args: argparse.Namespace, *, tasklist_factory: TaskListFactory) -> Any:
    tarefa = svc.mover_status(
        _texto_obrigatorio(args.task_id, "task_id"),
        _texto_obrigatorio(args.status, "status"),
        tasklist=tasklist_factory(),
    )
    return _tarefa_dict(tarefa)


def cmd_concluir(args: argparse.Namespace, *, tasklist_factory: TaskListFactory) -> Any:
    tarefa = svc.concluir_tarefa(
        _texto_obrigatorio(args.task_id, "task_id"),
        _texto_obrigatorio(args.status, "status"),
        tasklist=tasklist_factory(),
    )
    return _tarefa_dict(tarefa)


def cmd_opcoes(args: argparse.Namespace, *, tasklist_factory: TaskListFactory) -> Any:
    return svc.listar_opcoes(tasklist=tasklist_factory())


def cmd_databases(args: argparse.Namespace, *, client_factory: ClientFactory) -> Any:
    itens = client_factory().buscar(
        query=_normalizar_texto(args.query),
        buscar_todos=True,
        filtro={"property": "object", "value": "database"},
    )
    return [_database_dict(item) for item in itens]


def cmd_database_atual(args: argparse.Namespace) -> Any:
    return {"database_id": os.environ.get("NOTION_DATABASE_ID", "").strip()}


def cmd_escolher_database(args: argparse.Namespace) -> Any:
    database_id = _texto_obrigatorio(args.database_id, "database_id")
    _salvar_database_env(database_id)
    return {"database_id": database_id, "salvo_em": str(RAIZ / ".env")}


def cmd_mapear(args: argparse.Namespace, *, client_factory: ClientFactory) -> Any:
    itens = client_factory().buscar(
        query=_normalizar_texto(args.query),
        page_size=args.page_size,
        buscar_todos=True,
    )
    inventario = construir_inventario(itens)
    duplicatas = [
        {"titulo": titulo, "ids": [item.id for item in grupo]}
        for titulo, grupo in inventario.duplicatas.items()
    ]
    return {
        "total_itens": len(inventario.itens),
        "total_paginas": inventario.total_paginas,
        "total_databases": inventario.total_databases,
        "total_raizes": len(inventario.raizes),
        "total_duplicatas": len(inventario.duplicatas),
        "total_orfaos": len(inventario.orfaos),
        "duplicatas": duplicatas[: args.limite_duplicatas],
    }


def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m cli",
        description="CLI para IA operar tarefas do Notion via services.",
    )
    parser.add_argument("--json", action="store_true", help="emite envelope JSON estável")
    sub = parser.add_subparsers(dest="comando", required=True)

    listar = sub.add_parser("listar", help="lista tarefas")
    listar.add_argument("--status")
    listar.add_argument("--duracao")
    listar.add_argument("--area", action="append", help="ID de área; aceita CSV e repetição")

    ler = sub.add_parser("ler", help="lê uma tarefa pelo ID")
    ler.add_argument("task_id")

    criar = sub.add_parser("criar", help="cria uma tarefa")
    criar.add_argument("nome")
    criar.add_argument("--status")
    criar.add_argument("--prazo")
    criar.add_argument("--duracao")
    criar.add_argument("--area", action="append", help="ID de área; aceita CSV e repetição")

    editar = sub.add_parser("editar", help="edita uma tarefa")
    editar.add_argument("task_id")
    editar.add_argument("--nome")
    editar.add_argument("--status")
    editar.add_argument("--prazo")
    editar.add_argument("--duracao")
    editar.add_argument("--area", action="append", help="ID de área; aceita CSV e repetição")

    mover = sub.add_parser("mover", help="move tarefa para outro status")
    mover.add_argument("task_id")
    mover.add_argument("status")

    concluir = sub.add_parser("concluir", help="conclui tarefa com o status informado")
    concluir.add_argument("task_id")
    concluir.add_argument("status")

    sub.add_parser("opcoes", help="lista opções de status, duração e áreas")

    databases = sub.add_parser("databases", help="lista databases visíveis")
    databases.add_argument("--query")

    database_atual = sub.add_parser("database-atual", help="mostra o database configurado")
    database_atual.set_defaults(alias_comando="database-atual")

    escolher = sub.add_parser("escolher-database", help="grava NOTION_DATABASE_ID no .env")
    escolher.add_argument("database_id")

    mapear = sub.add_parser("mapear", help="resume o inventário do workspace")
    mapear.add_argument("--query")
    mapear.add_argument("--page-size", type=int, default=100)
    mapear.add_argument("--limite-duplicatas", type=int, default=10)
    return parser


def executar(
    argv: Sequence[str] | None = None,
    *,
    tasklist_factory: TaskListFactory = _criar_tasklist,
    client_factory: ClientFactory = _criar_client,
) -> tuple[int, dict[str, Any] | str]:
    parser = construir_parser()
    args = parser.parse_args(argv)
    try:
        comando = args.comando
        if comando == "listar":
            dados = cmd_listar(args, tasklist_factory=tasklist_factory)
        elif comando == "ler":
            dados = cmd_ler(args, tasklist_factory=tasklist_factory)
        elif comando == "criar":
            dados = cmd_criar(args, tasklist_factory=tasklist_factory)
        elif comando == "editar":
            dados = cmd_editar(args, tasklist_factory=tasklist_factory)
        elif comando == "mover":
            dados = cmd_mover(args, tasklist_factory=tasklist_factory)
        elif comando == "concluir":
            dados = cmd_concluir(args, tasklist_factory=tasklist_factory)
        elif comando == "opcoes":
            dados = cmd_opcoes(args, tasklist_factory=tasklist_factory)
        elif comando == "databases":
            dados = cmd_databases(args, client_factory=client_factory)
        elif comando == "database-atual":
            dados = cmd_database_atual(args)
        elif comando == "escolher-database":
            dados = cmd_escolher_database(args)
        elif comando == "mapear":
            dados = cmd_mapear(args, client_factory=client_factory)
        else:
            raise CLIError(f"Comando desconhecido: {comando}")
        return 0, _envelope(True, dados=dados) if args.json else _formatar_humano(comando, dados)
    except (CLIError, ValueError) as exc:
        return 2, _envelope(False, erro=str(exc)) if args.json else f"Erro: {exc}"
    except (NotionHTTPError, NotionAPIError) as exc:
        if isinstance(exc, NotionHTTPError) and exc.status_code == 404:
            mensagem = "Recurso não encontrado."
        else:
            mensagem = "Falha ao falar com o Notion."
        return 1, _envelope(False, erro=mensagem) if args.json else f"Erro: {mensagem}"
    except NotionConfigurationError:
        mensagem = "Configuração do Notion inválida."
        return 2, _envelope(False, erro=mensagem) if args.json else f"Erro: {mensagem}"


def main(argv: Sequence[str] | None = None) -> int:
    codigo, saida = executar(argv)
    if isinstance(saida, dict):
        print(_json(saida))
    else:
        print(saida)
    return codigo
