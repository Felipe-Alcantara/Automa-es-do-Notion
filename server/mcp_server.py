"""Servidor MCP — expoe as capacidades de Notion como ferramentas MCP.

Cada ferramenta e um involucro fino sobre os casos de uso de
``services.tarefas``.  O Felixo-AI-Core consome estas ferramentas via MCP
(stdio) para que agentes leiam e editem tarefas sem acessar o Notion
diretamente.

Guarda-corpos
~~~~~~~~~~~~~
- Ferramentas de escrita sinalizam ``readOnlyHint=False`` e
  ``openWorldHint=True`` — o cliente (Felixo-AI-Core) decide se pede
  confirmacao com base no seu catalogo (``requiresConfirmation``).
- Nenhuma ferramenta apaga dados (nao ha ``delete``).
- Segredos (token, database ID) vem do ambiente, nunca hardcoded.

A ``TaskList`` e criada diretamente do ``notion_starter`` (sem Django),
e **injetada** nas funcoes de ``services.tarefas`` — o mesmo padrao de DI
que os testes usam.

Uso::

    python server/mcp_server.py            # stdio (padrao — Felixo-AI-Core spawna assim)
    python server/mcp_server.py --transport streamable-http  # debug HTTP local
"""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any, Literal, TypeVar

# Garante que ``server/`` esta no ``sys.path`` para importar ``services``.
_SERVER_DIR = Path(__file__).resolve().parent
if str(_SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(_SERVER_DIR))

from core.config import carregar_env_file  # noqa: E402
from mcp.server.fastmcp import FastMCP  # noqa: E402
from mcp.types import ToolAnnotations  # noqa: E402

from notion_starter import (  # noqa: E402
    NotionAPIError,
    NotionClient,
    NotionConfigurationError,
    NotionHTTPError,
    TaskList,
)

# Carrega ``.env`` (se existir) para resolver token e database ID.
carregar_env_file()

# ---------------------------------------------------------------------------
# Anotacoes reutilizaveis (MCP spec 2025-03-26)
# ---------------------------------------------------------------------------

_READ = ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True)
_CREATE = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=False,
    idempotentHint=False,
    openWorldHint=True,
)
_UPDATE = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=True,
)

_T = TypeVar("_T")
Transport = Literal["stdio", "streamable-http"]

# ---------------------------------------------------------------------------
# Servidor MCP
# ---------------------------------------------------------------------------

mcp = FastMCP(
    "notion",
    instructions=(
        "Ferramentas para gerenciar tarefas no Notion. "
        "Ferramentas de escrita (notion.create_task, notion.move_status e "
        "notion.conclude_task) e atualizacao de projetos "
        "(notion.update_project_page) requerem confirmacao: o cliente so deve "
        "executa-las depois que o usuario confirmar a operacao."
    ),
)


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------


def _criar_notion_client() -> NotionClient:
    """Cria um cliente Notion direto do ambiente (sem Django)."""

    token = os.environ.get("NOTION_TOKEN", "").strip()
    if not token:
        raise NotionConfigurationError(
            "NOTION_TOKEN nao configurado. Defina a variavel de ambiente ou "
            "use o .env na raiz do projeto."
        )
    return NotionClient(token=token)


def _criar_tasklist() -> TaskList:
    """Cria uma ``TaskList`` direto do ambiente (sem Django)."""

    db_id = os.environ.get("NOTION_DATABASE_ID", "").strip()
    if not db_id:
        raise NotionConfigurationError(
            "NOTION_DATABASE_ID nao configurado. Defina a variavel de ambiente "
            "ou use o .env na raiz do projeto."
        )
    return TaskList(_criar_notion_client(), db_id)


def _tarefa_dict(tarefa: Any) -> dict[str, Any]:
    """Serializa uma ``Tarefa`` para dict (mesmo contrato da API REST)."""

    return {
        "id": tarefa.id,
        "nome": tarefa.nome,
        "status": tarefa.status,
        "prazo": tarefa.prazo,
        "url": tarefa.url,
    }


def _projeto_dict(projeto: Any) -> dict[str, Any]:
    """Serializa a referência pública de uma página de projeto."""

    return {"id": projeto.id, "url": projeto.url}


def _texto_obrigatorio(valor: str, campo: str) -> str:
    """Normaliza uma entrada textual obrigatoria da borda MCP."""

    normalizado = valor.strip()
    if not normalizado:
        raise ValueError(f"'{campo}' e obrigatorio")
    return normalizado


def _texto_opcional(valor: str | None) -> str | None:
    """Normaliza uma entrada textual opcional; vazio vira ``None``."""

    if valor is None:
        return None
    return valor.strip() or None


def _inteiro_nao_negativo(valor: int, campo: str) -> int:
    """Valida uma contagem inteira da borda MCP."""

    if valor < 0:
        raise ValueError(f"'{campo}' nao pode ser negativo")
    return valor


def _executar(acao: Callable[[], _T]) -> _T:
    """Executa uma ferramenta sem expor detalhes internos ou do provedor."""

    try:
        return acao()
    except ValueError:
        raise
    except NotionHTTPError as exc:
        if exc.status_code == 404:
            raise RuntimeError("Tarefa nao encontrada.") from exc
        raise RuntimeError("Falha ao falar com o Notion.") from exc
    except NotionAPIError as exc:
        raise RuntimeError("Falha ao falar com o Notion.") from exc
    except NotionConfigurationError as exc:
        raise RuntimeError("Servidor MCP nao configurado corretamente.") from exc
    except Exception as exc:
        raise RuntimeError("Erro interno inesperado no servidor MCP.") from exc


# ---------------------------------------------------------------------------
# Ferramentas MCP
# ---------------------------------------------------------------------------


@mcp.tool(name="notion.list_tasks", annotations=_READ)
def list_tasks(status: str | None = None) -> list[dict[str, Any]]:
    """Lista tarefas do Notion, opcionalmente filtrando por status.

    Ferramenta de leitura (read) — nao modifica dados.

    Args:
        status: Nome do status para filtrar (ex.: "00. Inbox").
                Se omitido, lista todas.

    Returns:
        Lista de tarefas com id, nome, status, prazo e url.
    """

    from services import tarefas as svc

    def _listar() -> list[dict[str, Any]]:
        tl = _criar_tasklist()
        tarefas = svc.listar_tarefas(status=_texto_opcional(status), tasklist=tl)
        return [_tarefa_dict(t) for t in tarefas]

    return _executar(_listar)


@mcp.tool(name="notion.create_task", annotations=_CREATE)
def create_task(
    nome: str,
    status: str | None = None,
    prazo: str | None = None,
) -> dict[str, Any]:
    """Cria uma nova tarefa no Notion.

    Ferramenta de escrita (write) — requer confirmacao do usuario.

    Args:
        nome: Titulo da tarefa (obrigatorio).
        status: Status inicial (ex.: "00. Inbox"). Opcional.
        prazo: Data no formato AAAA-MM-DD. Opcional.

    Returns:
        A tarefa criada com id, nome, status, prazo e url.
    """

    from services import tarefas as svc

    def _criar() -> dict[str, Any]:
        nome_normalizado = _texto_obrigatorio(nome, "nome")
        tl = _criar_tasklist()
        tarefa = svc.criar_tarefa(
            nome_normalizado,
            status=_texto_opcional(status),
            prazo=_texto_opcional(prazo),
            tasklist=tl,
        )
        return _tarefa_dict(tarefa)

    return _executar(_criar)


@mcp.tool(name="notion.move_status", annotations=_UPDATE)
def move_status(task_id: str, status: str) -> dict[str, Any]:
    """Move uma tarefa para outro status no Notion.

    Ferramenta de escrita (write) — requer confirmacao do usuario.

    Args:
        task_id: ID da tarefa no Notion.
        status: Novo status (ex.: "02. Fazendo").

    Returns:
        A tarefa atualizada com id, nome, status, prazo e url.
    """

    from services import tarefas as svc

    def _mover() -> dict[str, Any]:
        task_id_normalizado = _texto_obrigatorio(task_id, "task_id")
        status_normalizado = _texto_obrigatorio(status, "status")
        tl = _criar_tasklist()
        tarefa = svc.mover_status(
            task_id_normalizado,
            status_normalizado,
            tasklist=tl,
        )
        return _tarefa_dict(tarefa)

    return _executar(_mover)


@mcp.tool(name="notion.conclude_task", annotations=_UPDATE)
def conclude_task(task_id: str, status_concluido: str) -> dict[str, Any]:
    """Conclui uma tarefa no Notion com o status de conclusao informado.

    Ferramenta de escrita (write) — requer confirmacao do usuario.

    Args:
        task_id: ID da tarefa no Notion.
        status_concluido: Nome do status que representa conclusao
                          (ex.: "06. Feito").

    Returns:
        A tarefa concluida com id, nome, status, prazo e url.
    """

    from services import tarefas as svc

    def _concluir() -> dict[str, Any]:
        task_id_normalizado = _texto_obrigatorio(task_id, "task_id")
        status_normalizado = _texto_obrigatorio(status_concluido, "status_concluido")
        tl = _criar_tasklist()
        tarefa = svc.concluir_tarefa(
            task_id_normalizado,
            status_normalizado,
            tasklist=tl,
        )
        return _tarefa_dict(tarefa)

    return _executar(_concluir)


@mcp.tool(name="notion.update_project_page", annotations=_UPDATE)
def update_project_page(
    page_id: str,
    nome_completo: str,
    descricao: str | None = None,
    url_html: str | None = None,
    homepage: str | None = None,
    linguagem: str | None = None,
    topicos: list[str] | None = None,
    estrelas: int = 0,
    forks: int = 0,
    privado: bool = False,
    atualizado_em: str | None = None,
) -> dict[str, Any]:
    """Atualiza uma página de projeto com metadados normalizados do GitHub.

    Ferramenta de escrita idempotente — requer confirmacao do usuario.
    """

    from integrations.github import RepoInfo
    from services import projetos as svc

    def _atualizar() -> dict[str, Any]:
        page_id_normalizado = _texto_obrigatorio(page_id, "page_id")
        nome_normalizado = _texto_obrigatorio(nome_completo, "nome_completo")
        repo = RepoInfo(
            nome=nome_normalizado.rsplit("/", 1)[-1],
            nome_completo=nome_normalizado,
            descricao=_texto_opcional(descricao),
            url_html=_texto_opcional(url_html),
            homepage=_texto_opcional(homepage),
            linguagem=_texto_opcional(linguagem),
            topicos=[
                topico_normalizado
                for topico in (topicos or [])
                if (topico_normalizado := topico.strip())
            ],
            estrelas=_inteiro_nao_negativo(estrelas, "estrelas"),
            forks=_inteiro_nao_negativo(forks, "forks"),
            privado=privado,
            atualizado_em=_texto_opcional(atualizado_em),
        )
        projeto = svc.atualizar_pagina_projeto(
            page_id_normalizado,
            repo,
            notion_client=_criar_notion_client(),
        )
        return _projeto_dict(projeto)

    return _executar(_atualizar)


# ---------------------------------------------------------------------------
# Ponto de entrada
# ---------------------------------------------------------------------------


def _resolver_transporte(argv: Sequence[str] | None = None) -> Transport:
    """Resolve o transporte solicitado pela CLI."""

    parser = argparse.ArgumentParser(description="Servidor MCP de tarefas do Notion.")
    parser.add_argument(
        "--transport",
        choices=("stdio", "streamable-http"),
        default="stdio",
        help="Transporte MCP (padrao: stdio).",
    )
    args = parser.parse_args(argv)
    return args.transport


def main(argv: Sequence[str] | None = None) -> None:
    """Inicia o servidor no transporte escolhido."""

    mcp.run(transport=_resolver_transporte(argv))


if __name__ == "__main__":
    main()
