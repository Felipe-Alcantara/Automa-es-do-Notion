"""Camada de alto nível para trabalhar com um database de tarefas do Notion.

Traduz entre o JSON cru do Notion e um objeto :class:`Tarefa` simples — a forma
que um front ou um sistema de IA consome sem precisar conhecer o formato da API.
Fica acima de :class:`NotionClient`: lê, cria e atualiza tarefas, mapeando as
colunas comuns (Nome, Status, prazo) de um database de tasklist.

Os nomes das colunas são configuráveis porque variam entre workspaces; os
padrões batem com um database de tarefas típico do Notion.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from . import properties as p
from .client import NotionClient


@dataclass
class CamposTarefa:
    """Nomes das colunas do database de tarefas (configurável por workspace).

    Permite reaproveitar o módulo em databases que nomeiam as colunas de forma
    diferente, sem mudar a lógica.
    """

    nome: str = "Nome"
    status: str = "Status"
    prazo: str = "Próximo prazo"


@dataclass
class Tarefa:
    """Uma tarefa lida de um database do Notion, em forma simples.

    Attributes:
        id: ID da página (a tarefa) no Notion.
        nome: Texto do título.
        status: Nome do status atual (ou ``None`` se não definido).
        prazo: Data do prazo em ISO (ou ``None``).
        url: Link da tarefa no Notion.
        bruto: O JSON original, para quem precisar de campos não mapeados.
    """

    id: str
    nome: str
    status: str | None = None
    prazo: str | None = None
    url: str | None = None
    bruto: dict[str, Any] = field(default_factory=dict, repr=False)


def _texto_title(prop: dict[str, Any]) -> str:
    partes = prop.get("title", [])
    return "".join(t.get("plain_text", t.get("text", {}).get("content", "")) for t in partes)


def tarefa_de_pagina(pagina: dict[str, Any], campos: CamposTarefa) -> Tarefa:
    """Converte o JSON cru de uma página do Notion em :class:`Tarefa`.

    Args:
        pagina: Item retornado por :meth:`NotionClient.consultar_database`.
        campos: Nomes das colunas a ler.

    Returns:
        A tarefa normalizada.
    """

    props = pagina.get("properties", {})

    nome = ""
    if campos.nome in props:
        nome = _texto_title(props[campos.nome])

    status = None
    prop_status = props.get(campos.status, {})
    valor_status = prop_status.get(prop_status.get("type", ""))
    if isinstance(valor_status, dict):
        status = valor_status.get("name")

    prazo = None
    prop_prazo = props.get(campos.prazo, {})
    if prop_prazo.get("type") == "date" and isinstance(prop_prazo.get("date"), dict):
        prazo = prop_prazo["date"].get("start")

    return Tarefa(
        id=pagina.get("id", ""),
        nome=nome,
        status=status,
        prazo=prazo,
        url=pagina.get("url"),
        bruto=pagina,
    )


class TaskList:
    """Operações de tasklist sobre um database de tarefas do Notion.

    Args:
        client: Um :class:`NotionClient` já configurado.
        database_id: ID do database de tarefas.
        campos: Nomes das colunas (use o padrão ou ajuste ao seu database).
    """

    def __init__(
        self,
        client: NotionClient,
        database_id: str,
        campos: CamposTarefa | None = None,
    ) -> None:
        self._client = client
        self._database_id = database_id
        self._campos = campos or CamposTarefa()

    def listar(
        self,
        status: str | None = None,
        buscar_todos: bool = True,
    ) -> list[Tarefa]:
        """Lista as tarefas, opcionalmente filtrando por status.

        Args:
            status: Quando informado, retorna só as tarefas nesse status.
            buscar_todos: Percorre toda a paginação (padrão).

        Returns:
            As tarefas normalizadas.
        """

        filtro = None
        if status is not None:
            filtro = {
                "property": self._campos.status,
                "status": {"equals": status},
            }
        paginas = self._client.consultar_database(
            self._database_id, buscar_todos=buscar_todos, filtro=filtro
        )
        return [tarefa_de_pagina(pg, self._campos) for pg in paginas]

    def criar(
        self,
        nome: str,
        status: str | None = None,
        prazo: str | None = None,
    ) -> Tarefa:
        """Cria uma tarefa nova no database.

        Args:
            nome: Título da tarefa.
            status: Status inicial (deve existir no database).
            prazo: Data do prazo (ISO, ex.: ``"2026-07-01"``).

        Returns:
            A tarefa criada.
        """

        propriedades: dict[str, Any] = {self._campos.nome: p.title(nome)}
        if status is not None:
            propriedades[self._campos.status] = p.status(status)
        if prazo is not None:
            propriedades[self._campos.prazo] = p.date(prazo)

        pagina = self._client.criar_pagina(self._database_id, propriedades)
        return tarefa_de_pagina(pagina, self._campos)

    def atualizar_status(self, task_id: str, status: str) -> Tarefa:
        """Muda o status de uma tarefa existente.

        Args:
            task_id: ID da página (a tarefa).
            status: Novo status (deve existir no database).

        Returns:
            A tarefa atualizada.
        """

        pagina = self._client.atualizar_pagina(
            task_id, {self._campos.status: p.status(status)}
        )
        return tarefa_de_pagina(pagina, self._campos)

    def concluir(self, task_id: str, status_concluido: str) -> Tarefa:
        """Marca uma tarefa como concluída usando o status de conclusão do workspace.

        Args:
            task_id: ID da tarefa.
            status_concluido: Nome do status que representa "feito"
                (ex.: ``"06. Feito"``), específico do seu database.

        Returns:
            A tarefa atualizada.
        """

        return self.atualizar_status(task_id, status_concluido)
