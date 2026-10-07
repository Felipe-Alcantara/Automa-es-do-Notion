"""Testes da conversão de imports relativos em absolutos pela tabela de movimentos."""

from __future__ import annotations

import pytest
from scripts.migracao import reescrever_imports
from scripts.migracao.mapa_modulos import (
    RAIZES,
    TABELA_MOVIMENTOS,
    modulo_antigo_do_arquivo,
    montar_mapa,
)
from scripts.migracao.reescrever_imports import ImportAmbiguo, reescrever_codigo

MAPA = montar_mapa(TABELA_MOVIMENTOS, RAIZES)


def _reescrever(texto, modulo_antigo, *, pacote=False, mapa=MAPA):
    return reescrever_codigo(
        texto,
        mapa,
        em_migracao_django=False,
        modulo_antigo=modulo_antigo,
        eh_pacote_antigo=pacote,
    )


# --------------------------------------------------------------------------------------
# Reescrita de código com o nome antigo do arquivo
# --------------------------------------------------------------------------------------


def test_import_de_modulo_irmao_no_init_do_pacote_raiz():
    novo, _ = _reescrever("from .client import NotionClient\n", "notion_starter", pacote=True)
    assert novo == "from felixo_notion_mcp.integrations.notion_client import NotionClient\n"


def test_import_de_um_nivel_acima_em_modulo_de_subpacote():
    novo, _ = _reescrever(
        "from ..exceptions import NotionSyncError\n", "notion_starter.services.tarefas"
    )
    assert novo == "from felixo_notion_mcp.core.exceptions import NotionSyncError\n"


def test_from_ponto_import_submodulo_no_init_de_subpacote():
    novo, _ = _reescrever("from . import conteudo\n", "notion_starter.services", pacote=True)
    assert novo == "from felixo_notion_mcp.services import conteudo\n"


def test_arquivo_fora_da_tabela_mantem_os_relativos():
    src = "from .client import NotionClient\nfrom . import x\nfrom ..y import z\n"
    assert reescrever_codigo(src, MAPA, em_migracao_django=False)[0] == src


def test_nome_resolvido_que_o_mapa_nao_conhece_nao_muda():
    src = "from .inexistente import x\nfrom . import y\n"
    assert _reescrever(src, "pacote_desconhecido.modulo")[0] == src


def test_prefixo_do_mapa_sem_o_modulo_exato_nao_vale_para_relativo():
    # `notion_starter.fantasma` não existe no mapa; só o prefixo `notion_starter` casaria.
    src = "from .fantasma import x\n"
    assert _reescrever(src, "notion_starter", pacote=True)[0] == src


def test_nomes_do_mesmo_pai_novo_ficam_num_import_so():
    novo, _ = _reescrever(
        "from . import git_historico, properties, readers\n", "notion_starter", pacote=True
    )
    assert novo == "from felixo_notion_mcp.domain import git_historico, properties, readers\n"


def test_import_com_alias_e_comentario_preserva_o_resto_da_linha():
    novo, _ = _reescrever(
        "from . import properties as p  # escrita\n", "notion_starter.tasks", pacote=False
    )
    assert novo == "from felixo_notion_mcp.domain import properties as p  # escrita\n"


def test_relativo_em_varias_linhas_entre_parenteses():
    src = "from .constants import (\n    MAX_RICH_TEXT,\n    MAX_URL,\n)\n"
    novo, _ = _reescrever(src, "notion_starter.properties")
    assert novo == (
        "from felixo_notion_mcp.core.constants import (\n    MAX_RICH_TEXT,\n    MAX_URL,\n)\n"
    )


def test_relativo_dentro_de_funcao_com_recuo():
    src = "def f():\n    from .utils import chave_de_id\n    return chave_de_id\n"
    novo, _ = _reescrever(src, "notion_starter.client")
    assert "    from felixo_notion_mcp.core.utils import chave_de_id\n" in novo


def test_relativo_de_tres_pontos_sobe_dois_niveis():
    mapa = {"a": "n.a", "a.x": "n.a.x"}
    novo, _ = _reescrever("from ... import x\n", "a.b.c.d", mapa=mapa)
    assert novo == "from n.a import x\n"


def test_relativo_que_passa_da_raiz_do_pacote_nao_muda():
    src = "from ... import x\n"
    assert _reescrever(src, "notion_starter.client")[0] == src


def test_relativo_de_modulo_renomeado_pelo_pai_vira_pendencia():
    with pytest.raises(ImportAmbiguo) as erro:
        _reescrever("from . import client\n", "notion_starter", pacote=True)
    assert erro.value.linha == 1


def test_relativo_com_nomes_de_pais_diferentes_vira_pendencia():
    with pytest.raises(ImportAmbiguo):
        _reescrever("from . import properties, NotionClient\n", "notion_starter", pacote=True)


def test_relativo_ambiguo_fica_como_esta_e_o_resto_do_arquivo_e_reescrito():
    analise = reescrever_imports.analisar_codigo(
        "from . import client\nfrom .utils import chave_de_id\n",
        MAPA,
        em_migracao_django=False,
        modulo_antigo="notion_starter",
        eh_pacote_antigo=True,
    )
    assert analise.texto == (
        "from . import client\nfrom felixo_notion_mcp.core.utils import chave_de_id\n"
    )
    assert [p.linha for p in analise.pendencias] == [1]


def test_conversao_de_relativos_e_idempotente():
    fonte = "from .client import NotionClient\nfrom . import properties\n"
    uma, _ = _reescrever(fonte, "notion_starter", pacote=True)
    assert _reescrever(uma, "notion_starter", pacote=True)[0] == uma


def test_trocas_de_relativos_aparecem_na_lista():
    _, trocas = _reescrever("from .client import X\n", "notion_starter", pacote=True)
    assert trocas == ["linha 1: from .client -> felixo_notion_mcp.integrations.notion_client"]


# --------------------------------------------------------------------------------------
# Nome antigo de um arquivo pela tabela (consulta reversa)
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("destino", "esperado"),
    [
        ("src/felixo_notion_mcp/__init__.py", ("notion_starter", True)),
        ("src/felixo_notion_mcp/services/__init__.py", ("notion_starter.services", True)),
        # O shim da CLI e do app aponta para o mesmo destino, mas o módulo real é o do starter.
        (
            "src/felixo_notion_mcp/services/tarefas.py",
            ("notion_starter.services.tarefas", False),
        ),
        ("src/felixo_notion_mcp/integrations/notion_client.py", ("notion_starter.client", False)),
        ("src/felixo_notion_mcp/core/config.py", ("core.config", False)),
        ("src/felixo_notion_mcp/api/cli/__init__.py", ("cli", True)),
        ("src/felixo_notion_mcp/api/http/rest/views.py", ("server.api.views", False)),
        ("scripts/empacotamento/build_native.py", ("scripts.build_native", False)),
    ],
)
def test_nome_antigo_do_arquivo_pela_tabela(destino, esperado):
    assert modulo_antigo_do_arquivo(destino, TABELA_MOVIMENTOS, RAIZES) == esperado


def test_nome_antigo_de_arquivo_que_nao_esta_na_tabela_e_none():
    assert (
        modulo_antigo_do_arquivo("src/felixo_notion_mcp/novo.py", TABELA_MOVIMENTOS, RAIZES) is None
    )
    assert (
        modulo_antigo_do_arquivo("tests/api/cli/test_retrato.py", TABELA_MOVIMENTOS, RAIZES) is None
    )


def test_origem_ainda_nao_movida_tambem_tem_nome_antigo():
    origem = "_importado/notion-starter/src/notion_starter/tasks.py"
    assert modulo_antigo_do_arquivo(origem, TABELA_MOVIMENTOS, RAIZES) == (
        "notion_starter.tasks",
        False,
    )


# --------------------------------------------------------------------------------------
# Arquivos
# --------------------------------------------------------------------------------------


def test_arquivo_destino_da_tabela_converte_relativos(tmp_path):
    arquivo = tmp_path / "src/felixo_notion_mcp/services/tarefas.py"
    arquivo.parent.mkdir(parents=True)
    arquivo.write_text("from ..exceptions import NotionSyncError\n", encoding="utf-8")
    resultado = reescrever_imports.reescrever_arquivo(arquivo, MAPA, aplicar=True, raiz=tmp_path)
    assert resultado.mudou and not resultado.pendencias
    assert arquivo.read_text(encoding="utf-8") == (
        "from felixo_notion_mcp.core.exceptions import NotionSyncError\n"
    )


def test_arquivo_novo_fora_da_tabela_mantem_os_relativos(tmp_path):
    arquivo = tmp_path / "src/felixo_notion_mcp/novo.py"
    arquivo.parent.mkdir(parents=True)
    arquivo.write_text("from .client import X\n", encoding="utf-8")
    resultado = reescrever_imports.reescrever_arquivo(arquivo, MAPA, aplicar=True, raiz=tmp_path)
    assert not resultado.mudou
    assert arquivo.read_text(encoding="utf-8") == "from .client import X\n"


def test_cli_converte_relativos_de_arquivo_da_tabela(tmp_path, monkeypatch, capsys):
    arquivo = tmp_path / "src/felixo_notion_mcp/__init__.py"
    arquivo.parent.mkdir(parents=True)
    arquivo.write_text("from .client import NotionClient\n", encoding="utf-8")
    monkeypatch.setattr(reescrever_imports, "RAIZ", tmp_path)
    assert reescrever_imports.main(["--aplicar", str(tmp_path / "src")]) == 0
    assert arquivo.read_text(encoding="utf-8") == (
        "from felixo_notion_mcp.integrations.notion_client import NotionClient\n"
    )
    assert "integrations.notion_client" in capsys.readouterr().out
