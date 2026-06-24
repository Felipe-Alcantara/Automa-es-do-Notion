"""Transforma itens crus do Notion em um inventário navegável do workspace.

Lógica pura, sem rede: recebe a lista de páginas/databases retornada por
:meth:`NotionClient.buscar` e reconstrói a hierarquia (via ``parent``), além de
destacar duplicatas por nome, itens possivelmente vazios e itens órfãos.

Fluxo típico:
    itens_crus = client.buscar(buscar_todos=True)
    inventario = construir_inventario(itens_crus)
    inventario.duplicatas        # nomes repetidos
    inventario.raizes            # topo da árvore (filhos em cada NoArvore)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

SEM_TITULO = "(sem título)"


@dataclass
class ItemInventario:
    """Forma normalizada de uma página ou database do Notion.

    Attributes:
        id: Identificador do item no Notion.
        tipo: ``"page"`` ou ``"database"``.
        titulo: Título legível (ou ``"(sem título)"``).
        parent_tipo: Tipo do parent (``workspace``/``page_id``/``database_id``/``block_id``).
        parent_id: ID do parent, ou ``None`` quando o parent é o workspace.
        url: URL do item no Notion, quando disponível.
    """

    id: str
    tipo: str
    titulo: str
    parent_tipo: str
    parent_id: str | None
    url: str | None = None


@dataclass
class NoArvore:
    """Nó da árvore do workspace: um item com seus filhos diretos."""

    item: ItemInventario
    filhos: list[NoArvore] = field(default_factory=list)


@dataclass
class Inventario:
    """Resultado do inventário do workspace.

    Attributes:
        itens: Todos os itens normalizados, indexados por ``id``.
        raizes: Nós de topo da árvore (parent fora do conjunto ou workspace).
        duplicatas: Mapa de título para a lista de itens que o compartilham.
        vazios: Itens sem filhos na árvore (candidatos a revisão/arquivamento).
        orfaos: Itens cujo parent não está entre os itens visíveis.
    """

    itens: dict[str, ItemInventario]
    raizes: list[NoArvore]
    duplicatas: dict[str, list[ItemInventario]]
    vazios: list[ItemInventario]
    orfaos: list[ItemInventario]

    @property
    def total_paginas(self) -> int:
        return sum(1 for i in self.itens.values() if i.tipo == "page")

    @property
    def total_databases(self) -> int:
        return sum(1 for i in self.itens.values() if i.tipo == "database")


def _extrair_titulo(item: dict[str, Any]) -> str:
    """Extrai um título legível de um item cru de página ou database."""

    if item.get("object") == "database":
        partes = item.get("title", [])
        return "".join(p.get("plain_text", "") for p in partes).strip() or SEM_TITULO

    for prop in item.get("properties", {}).values():
        if prop.get("type") == "title":
            partes = prop.get("title", [])
            return "".join(p.get("plain_text", "") for p in partes).strip() or SEM_TITULO
    return SEM_TITULO


def _extrair_parent(item: dict[str, Any]) -> tuple[str, str | None]:
    """Devolve ``(parent_tipo, parent_id)`` de um item cru.

    O Notion usa uma chave diferente conforme o tipo de parent
    (``page_id``/``database_id``/``block_id``); ``workspace`` não tem id.
    """

    parent = item.get("parent", {})
    parent_tipo = parent.get("type", "workspace")
    parent_id = parent.get(parent_tipo) if parent_tipo != "workspace" else None
    # ``workspace`` vem como booleano ``True``; normaliza para None.
    if not isinstance(parent_id, str):
        parent_id = None
    return parent_tipo, parent_id


def normalizar_item(item: dict[str, Any]) -> ItemInventario:
    """Converte um item cru do ``/search`` em :class:`ItemInventario`.

    Args:
        item: JSON de uma página ou database como vem de :meth:`NotionClient.buscar`.

    Returns:
        O item normalizado.
    """

    parent_tipo, parent_id = _extrair_parent(item)
    return ItemInventario(
        id=item.get("id", ""),
        tipo=item.get("object", "page"),
        titulo=_extrair_titulo(item),
        parent_tipo=parent_tipo,
        parent_id=parent_id,
        url=item.get("url"),
    )


def construir_inventario(itens_crus: list[dict[str, Any]]) -> Inventario:
    """Monta o inventário completo a partir dos itens crus do workspace.

    Args:
        itens_crus: Lista de páginas/databases de :meth:`NotionClient.buscar`.

    Returns:
        Um :class:`Inventario` com árvore, duplicatas, vazios e órfãos.
    """

    itens = {
        item.id: item
        for item in (normalizar_item(cru) for cru in itens_crus)
        if item.id
    }

    nos = {item_id: NoArvore(item=item) for item_id, item in itens.items()}

    raizes: list[NoArvore] = []
    orfaos: list[ItemInventario] = []

    for no in nos.values():
        pai_id = no.item.parent_id
        if pai_id is None:
            # Parent é o workspace: nó de topo.
            raizes.append(no)
        elif pai_id in nos:
            nos[pai_id].filhos.append(no)
        else:
            # Parent existe no Notion mas não está entre os itens visíveis.
            orfaos.append(no.item)
            raizes.append(no)

    duplicatas: dict[str, list[ItemInventario]] = {}
    for item in itens.values():
        if item.titulo != SEM_TITULO:
            duplicatas.setdefault(item.titulo, []).append(item)
    duplicatas = {titulo: lista for titulo, lista in duplicatas.items() if len(lista) > 1}

    vazios = [no.item for no in nos.values() if not no.filhos]

    return Inventario(
        itens=itens,
        raizes=raizes,
        duplicatas=duplicatas,
        vazios=vazios,
        orfaos=orfaos,
    )
