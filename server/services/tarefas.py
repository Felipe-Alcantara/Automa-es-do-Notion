"""Casos de uso de tarefas — a regra de negócio fina sobre a ``TaskList``.

Cada função é um caso de uso: recebe dados simples, delega à ``TaskList`` do
``notion_starter`` e devolve objetos :class:`Tarefa`. Esta camada **não conhece
HTTP** (isso é da camada ``api``) nem o **formato cru do Notion** (isso é do
``notion_starter``) — é a fronteira de negócio do servidor.

A ``TaskList`` é resolvida da configuração do servidor por padrão, mas pode ser
**injetada** (testes, ou um database alternativo). Isso mantém estas funções
puras e testáveis sem token nem rede real.
"""

from __future__ import annotations

from typing import Any

from notion_starter import Tarefa, TaskList


def _tasklist_padrao() -> TaskList:
    """Resolve a ``TaskList`` a partir da configuração do servidor.

    Import tardio de propósito: evita acoplar a camada de casos de uso ao Django
    no momento do import — a configuração só é tocada quando nenhuma ``TaskList``
    é injetada (uso real), nunca nos testes que injetam a sua própria.
    """

    from integrations.notion import criar_tasklist

    return criar_tasklist()


def listar_tarefas(
    status: str | None = None,
    duracao: str | None = None,
    areas: list[str] | None = None,
    *,
    tasklist: TaskList | None = None,
) -> list[Tarefa]:
    """Lista as tarefas, opcionalmente filtrando por propriedades do Notion."""

    return (tasklist or _tasklist_padrao()).listar(status=status, duracao=duracao, areas=areas)


def criar_tarefa(
    nome: str,
    status: str | None = None,
    prazo: str | None = None,
    duracao: str | None = None,
    areas: list[str] | None = None,
    *,
    tasklist: TaskList | None = None,
) -> Tarefa:
    """Cria uma tarefa nova (todos os campos exceto ``nome`` são opcionais)."""

    return (tasklist or _tasklist_padrao()).criar(
        nome, status=status, prazo=prazo, duracao=duracao, areas=areas
    )


def editar_tarefa(
    task_id: str,
    *,
    nome: str | None = None,
    status: str | None = None,
    prazo: str | None = None,
    duracao: str | None = None,
    areas: list[str] | None = None,
    tasklist: TaskList | None = None,
) -> Tarefa:
    """Edita uma tarefa existente (um ou mais campos).

    Retrocompatível: ``editar_tarefa(id, status=...)`` faz o mesmo que o antigo
    ``mover_status``.
    """

    return (tasklist or _tasklist_padrao()).editar(
        task_id, nome=nome, status=status, prazo=prazo, duracao=duracao, areas=areas
    )


def listar_opcoes(
    *,
    tasklist: TaskList | None = None,
) -> dict[str, Any]:
    """Retorna os valores possíveis para seletores (status, duração, áreas)."""

    return (tasklist or _tasklist_padrao()).opcoes()


def mover_status(
    task_id: str,
    status: str,
    *,
    tasklist: TaskList | None = None,
) -> Tarefa:
    """Move uma tarefa existente para outro ``status``."""

    return (tasklist or _tasklist_padrao()).atualizar_status(task_id, status)


def concluir_tarefa(
    task_id: str,
    status_concluido: str,
    *,
    tasklist: TaskList | None = None,
) -> Tarefa:
    """Conclui uma tarefa usando o status de "feito" do workspace.

    Helper de negócio para quem conhece o status de conclusão (IA/MCP); a borda
    HTTP conclui movendo o status pela rota ``PATCH`` comum.
    """

    return (tasklist or _tasklist_padrao()).concluir(task_id, status_concluido)
