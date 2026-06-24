from __future__ import annotations

from notion_starter import (
    agrupar_por_schema,
    assinatura_schema,
    construir_inventario,
    normalizar_item,
)
from notion_starter.inventory import SEM_TITULO


def pagina(id_, titulo, parent_tipo="workspace", parent_id=None):
    """Monta um item cru de página no formato do /search."""
    parent: dict = {"type": parent_tipo}
    if parent_tipo == "workspace":
        parent["workspace"] = True
    else:
        parent[parent_tipo] = parent_id
    props = {}
    if titulo is not None:
        props = {"Name": {"type": "title", "title": [{"plain_text": titulo}]}}
    return {"object": "page", "id": id_, "parent": parent, "properties": props}


def database(id_, titulo, parent_tipo="workspace", parent_id=None):
    """Monta um item cru de database no formato do /search."""
    parent: dict = {"type": parent_tipo}
    if parent_tipo == "workspace":
        parent["workspace"] = True
    else:
        parent[parent_tipo] = parent_id
    return {
        "object": "database",
        "id": id_,
        "parent": parent,
        "title": [{"plain_text": titulo}],
    }


# -- Normalização ----------------------------------------------------------


def test_normalizar_pagina_extrai_titulo_e_parent():
    item = normalizar_item(pagina("p1", "Tarefas", "page_id", "pai"))
    assert item.id == "p1"
    assert item.tipo == "page"
    assert item.titulo == "Tarefas"
    assert item.parent_tipo == "page_id"
    assert item.parent_id == "pai"


def test_normalizar_database_extrai_titulo():
    item = normalizar_item(database("d1", "Projects"))
    assert item.tipo == "database"
    assert item.titulo == "Projects"
    assert item.parent_id is None  # workspace


def test_normalizar_sem_titulo_usa_placeholder():
    item = normalizar_item(pagina("p1", None))
    assert item.titulo == SEM_TITULO


# -- Árvore ----------------------------------------------------------------


def test_construir_arvore_aninha_filhos_no_pai():
    inv = construir_inventario([
        pagina("home", "HOME"),
        pagina("filho", "Estudo", "page_id", "home"),
    ])
    assert len(inv.raizes) == 1
    raiz = inv.raizes[0]
    assert raiz.item.id == "home"
    assert [n.item.id for n in raiz.filhos] == ["filho"]


def test_pagina_no_workspace_e_raiz():
    inv = construir_inventario([pagina("p1", "Solta")])
    assert [n.item.id for n in inv.raizes] == ["p1"]


# -- Duplicatas, vazios, órfãos -------------------------------------------


def test_duplicatas_agrupa_titulos_repetidos():
    inv = construir_inventario([
        database("d1", "Tarefas"),
        database("d2", "Tarefas"),
        database("d3", "Unico"),
    ])
    assert "Tarefas" in inv.duplicatas
    assert len(inv.duplicatas["Tarefas"]) == 2
    assert "Unico" not in inv.duplicatas


def test_sem_titulo_nao_conta_como_duplicata():
    inv = construir_inventario([pagina("p1", None), pagina("p2", None)])
    assert inv.duplicatas == {}


def test_vazios_sao_itens_sem_filhos():
    inv = construir_inventario([
        pagina("home", "HOME"),
        pagina("filho", "Estudo", "page_id", "home"),
    ])
    ids_vazios = {i.id for i in inv.vazios}
    assert ids_vazios == {"filho"}  # home tem filho, nao e vazio


def test_orfao_quando_parent_nao_esta_visivel():
    inv = construir_inventario([
        pagina("p1", "Perdida", "page_id", "pai_invisivel"),
    ])
    assert [i.id for i in inv.orfaos] == ["p1"]
    # Órfão também vira raiz para não sumir da árvore.
    assert [n.item.id for n in inv.raizes] == ["p1"]


def test_totais():
    inv = construir_inventario([
        pagina("p1", "A"),
        database("d1", "B"),
    ])
    assert inv.total_paginas == 1
    assert inv.total_databases == 1


# -- Agrupamento por schema -----------------------------------------------


def test_assinatura_independe_da_ordem_das_colunas():
    a = assinatura_schema({"Nome": "title", "Email": "email"})
    b = assinatura_schema({"Email": "email", "Nome": "title"})
    assert a == b


def test_assinatura_diferente_quando_tipo_muda():
    a = assinatura_schema({"Nome": "title"})
    b = assinatura_schema({"Nome": "rich_text"})
    assert a != b


def test_agrupar_junta_databases_com_mesma_estrutura():
    schemas = {
        "d1": {"Nome": "title", "Email": "email"},
        "d2": {"Email": "email", "Nome": "title"},  # mesma estrutura, ordem diferente
        "d3": {"Titulo": "title"},  # estrutura diferente
    }
    grupos = agrupar_por_schema(schemas)
    assert len(grupos) == 1
    assert set(grupos[0].databases) == {"d1", "d2"}


def test_agrupar_detecta_nomes_diferentes_no_grupo():
    schemas = {"d1": {"N": "title"}, "d2": {"N": "title"}}
    nomes = {"d1": "Tarefas", "d2": "To-do"}
    grupo = agrupar_por_schema(schemas, nomes)[0]
    assert not grupo.mesmos_nomes
    assert set(grupo.nomes) == {"Tarefas", "To-do"}


def test_agrupar_ignora_databases_sem_colunas():
    schemas = {"d1": {}, "d2": {}}
    assert agrupar_por_schema(schemas) == []


def test_agrupar_ordena_do_maior_grupo_para_o_menor():
    schemas = {
        "a1": {"X": "title"},
        "a2": {"X": "title"},
        "a3": {"X": "title"},
        "b1": {"Y": "number"},
        "b2": {"Y": "number"},
    }
    grupos = agrupar_por_schema(schemas)
    assert [len(g.databases) for g in grupos] == [3, 2]
