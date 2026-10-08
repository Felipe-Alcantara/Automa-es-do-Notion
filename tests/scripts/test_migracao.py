"""Testes do mapa de módulos e da reescrita de imports da migração para o monólito."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from scripts.migracao import reescrever_imports
from scripts.migracao.mapa_modulos import (
    APP,
    CLI,
    NOMES_DE_TESTE_REPETIDOS,
    RAIZES,
    STARTER,
    TABELA_MOVIMENTOS,
    UNIFICADOS,
    ConflitoDeNome,
    Movimento,
    RaizPython,
    cobre,
    destino_do_teste,
    destinos_conhecidos,
    montar_mapa,
    pacotes_a_criar,
)
from scripts.migracao.reescrever_imports import ImportAmbiguo, reescrever_codigo

RAIZ_DO_REPOSITORIO = Path(__file__).resolve().parents[2]
BOM = chr(0xFEFF)

MAPA = {
    "notion_starter": "felixo_notion_mcp",
    "notion_starter.client": "felixo_notion_mcp.integrations.notion_client",
    "cli": "felixo_notion_mcp.api.cli",
    "cli.notion_tasks": "felixo_notion_mcp.api.cli.notion_tasks",
    "core": "felixo_notion_mcp.core",
    "operations": "felixo_notion_mcp.repositories.operations",
}


def test_reescreve_from_import_e_import_com_alias():
    novo, _ = reescrever_codigo(
        "from notion_starter.client import NotionClient\nimport cli.notion_tasks as nt\n",
        MAPA,
        em_migracao_django=False,
    )
    assert novo == (
        "from felixo_notion_mcp.integrations.notion_client import NotionClient\n"
        "import felixo_notion_mcp.api.cli.notion_tasks as nt\n"
    )


def test_reescreve_alvo_de_monkeypatch_em_string():
    novo, _ = reescrever_codigo(
        'monkeypatch.setattr("cli.notion_tasks.main", f)\n', MAPA, em_migracao_django=False
    )
    assert '"felixo_notion_mcp.api.cli.notion_tasks.main"' in novo


def test_from_pacote_import_submodulo_sem_renomear():
    novo, _ = reescrever_codigo("from core import workspaces\n", MAPA, em_migracao_django=False)
    assert novo == "from felixo_notion_mcp.core import workspaces\n"


def test_nao_toca_prefixo_parecido_nem_a_biblioteca_mcp():
    src = 'import client_x\nfrom mcp.server.fastmcp import FastMCP\nx = "clientes.cli"\n'
    assert reescrever_codigo(src, MAPA, em_migracao_django=False)[0] == src


def test_string_de_rotulo_django_nao_muda_dentro_de_migracao():
    src = 'dependencies = [("operations", "0001_initial")]\n'
    assert reescrever_codigo(src, MAPA, em_migracao_django=True)[0] == src


def test_import_de_modulo_renomeado_pelo_pacote_vira_pendencia():
    with pytest.raises(ImportAmbiguo):
        reescrever_codigo("from notion_starter import client\n", MAPA, em_migracao_django=False)


def test_from_pacote_fora_do_mapa_import_modulo_movido():
    mapa = {"scripts.build_native": "scripts.empacotamento.build_native"}
    novo, _ = reescrever_codigo(
        "from scripts import build_native\n", mapa, em_migracao_django=False
    )
    assert novo == "from scripts.empacotamento import build_native\n"


def test_reescrita_e_idempotente():
    uma, _ = reescrever_codigo(
        "from cli.notion_tasks import main\n", MAPA, em_migracao_django=False
    )
    assert reescrever_codigo(uma, MAPA, em_migracao_django=False)[0] == uma


def test_mapa_do_app_vale_com_e_sem_prefixo_server():
    mov = [
        Movimento(
            "_importado/notion-workspace-app/server/mcp_server.py",
            "src/felixo_notion_mcp/api/mcp/server.py",
            "notion-workspace-app",
        )
    ]
    mapa = montar_mapa(mov, RAIZES)
    assert mapa["mcp_server"] == mapa["server.mcp_server"] == "felixo_notion_mcp.api.mcp.server"


def test_tabela_sem_destinos_duplicados_fora_das_unificacoes():
    destinos = [m.destino for m in TABELA_MOVIMENTOS if m.destino and not m.apenas_mapear]
    repetidos = {d for d in destinos if destinos.count(d) > 1}
    assert repetidos <= UNIFICADOS


# --------------------------------------------------------------------------------------
# Tabela e mapa
# --------------------------------------------------------------------------------------


def _arquivos_importados_rastreados() -> list[str]:
    try:
        saida = subprocess.run(
            ["git", "ls-files", "-z", "_importado"],
            cwd=RAIZ_DO_REPOSITORIO,
            capture_output=True,
            check=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return []
    return [arquivo for arquivo in saida.decode("utf-8").split("\0") if arquivo]


def test_toda_origem_importada_tem_um_movimento():
    arquivos = _arquivos_importados_rastreados()
    if not arquivos:
        pytest.skip("`_importado/` não tem arquivos rastreados (migração concluída).")
    sem_movimento = [a for a in arquivos if not any(cobre(m, a) for m in TABELA_MOVIMENTOS)]
    com_dois = [a for a in arquivos if sum(cobre(m, a) for m in TABELA_MOVIMENTOS) > 1]
    assert sem_movimento == []
    assert com_dois == []


def test_toda_origem_da_tabela_esta_sob_a_pasta_do_proprio_modulo():
    for mov in TABELA_MOVIMENTOS:
        assert mov.origem.startswith(f"_importado/{mov.modulo}/"), mov


def test_origem_da_tabela_nao_se_repete():
    origens = [m.origem for m in TABELA_MOVIMENTOS]
    assert len(origens) == len(set(origens))


def test_destino_apenas_mapear_e_sempre_um_destino_que_existira():
    """O módulo real de um shim tem de ser escrito por algum movimento ou ser um pacote novo."""
    conhecidos = destinos_conhecidos()
    orfaos = [m for m in TABELA_MOVIMENTOS if m.apenas_mapear and m.destino not in conhecidos]
    assert orfaos == []


def test_apenas_mapear_exige_destino():
    with pytest.raises(ValueError):
        Movimento("_importado/notion-tasks-cli/x.py", "", "notion-tasks-cli", apenas_mapear=True)


def test_apenas_mapear_registra_os_nomes_antigos_apontando_para_o_modulo_real():
    movimentos = [
        Movimento(
            "_importado/notion-tasks-cli/services/tarefas.py",
            "src/felixo_notion_mcp/services/tarefas.py",
            CLI,
            apenas_mapear=True,
        )
    ]
    assert montar_mapa(movimentos, RAIZES) == {
        "services.tarefas": "felixo_notion_mcp.services.tarefas"
    }


def test_origem_removida_nao_gera_nome_no_mapa():
    movimentos = [Movimento("_importado/notion-tasks-cli/start_app.py", "", CLI)]
    assert montar_mapa(movimentos, RAIZES) == {}


def test_start_app_do_app_vira_launcher_e_o_da_cli_nao_conflita():
    mapa = montar_mapa(TABELA_MOVIMENTOS, RAIZES)
    assert mapa["start_app"] == "felixo_notion_mcp.api.launcher"
    removido = [m for m in TABELA_MOVIMENTOS if m.origem.endswith("notion-tasks-cli/start_app.py")]
    assert [m.destino for m in removido] == [""]


def test_nome_antigo_com_dois_destinos_diferentes_e_erro_claro():
    movimentos = [
        Movimento("_importado/notion-tasks-cli/start_app.py", "src/a/um.py", CLI),
        Movimento("_importado/notion-tasks-cli/start_app.py", "src/a/dois.py", CLI),
    ]
    with pytest.raises(ConflitoDeNome, match="start_app"):
        montar_mapa(movimentos, RAIZES)


def test_pacote_scripts_nunca_e_mapeado_inteiro():
    mapa = montar_mapa(TABELA_MOVIMENTOS, RAIZES)
    assert "scripts" not in mapa
    assert mapa["scripts.build_native"] == "scripts.empacotamento.build_native"


def test_mapa_da_tabela_tem_os_pacotes_raiz_antigos():
    mapa = montar_mapa(TABELA_MOVIMENTOS, RAIZES)
    esperado = {
        "notion_starter": "felixo_notion_mcp",
        "cli": "felixo_notion_mcp.api.cli",
        "core": "felixo_notion_mcp.core",
        "integrations": "felixo_notion_mcp.integrations",
        "services": "felixo_notion_mcp.services",
        "api": "felixo_notion_mcp.api.http.rest",
        "config": "felixo_notion_mcp.api.http.config",
        "operations": "felixo_notion_mcp.repositories.operations",
        "server": "felixo_notion_mcp.api.http",
        "start_app": "felixo_notion_mcp.api.launcher",
    }
    assert {nome: mapa[nome] for nome in esperado} == esperado


def test_mapa_da_tabela_nao_inclui_testes_nem_exemplos():
    mapa = montar_mapa(TABELA_MOVIMENTOS, RAIZES)
    assert not any(nome.split(".")[0] in {"tests", "examples", "conftest"} for nome in mapa)


def test_shim_e_modulo_real_apontam_para_o_mesmo_nome_novo():
    mapa = montar_mapa(TABELA_MOVIMENTOS, RAIZES)
    assert (
        mapa["services.tarefas"]
        == mapa["server.services.tarefas"]
        == mapa["notion_starter.services.tarefas"]
        == "felixo_notion_mcp.services.tarefas"
    )
    assert mapa["integrations.github"] == mapa["notion_starter.github"]


def test_raizes_do_app_dao_nomes_com_e_sem_server():
    assert RaizPython("_importado/notion-workspace-app", "") in RAIZES
    assert RaizPython("_importado/notion-workspace-app/server", "") in RAIZES


def test_pacotes_novos_so_para_pastas_com_codigo_python():
    pacotes = pacotes_a_criar(TABELA_MOVIMENTOS)
    assert "src/felixo_notion_mcp/domain/__init__.py" in pacotes
    assert "src/felixo_notion_mcp/api/mcp/__init__.py" in pacotes
    assert "src/felixo_notion_mcp/api/http/__init__.py" in pacotes
    assert "scripts/empacotamento/__init__.py" in pacotes
    assert not any("templates" in p or "static" in p for p in pacotes)
    # O que algum movimento já escreve como `__init__.py` não é criado de novo.
    assert "src/felixo_notion_mcp/services/__init__.py" not in pacotes


# --------------------------------------------------------------------------------------
# Regra de pasta dos testes
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("modulo", "nome", "esperado"),
    [
        (STARTER, "test_client.py", "tests/integrations/test_client.py"),
        (STARTER, "test_client_blocos.py", "tests/integrations/test_client_blocos.py"),
        (STARTER, "test_content_limites.py", "tests/domain/test_content_limites.py"),
        (STARTER, "test_schema_descricao.py", "tests/domain/test_schema_descricao.py"),
        (STARTER, "test_inventory.py", "tests/services/test_inventory.py"),
        (STARTER, "test_utils_ids.py", "tests/core/test_utils_ids.py"),
        (CLI, "test_workspaces.py", "tests/core/test_workspaces.py"),
        (CLI, "test_cli_schema_e_relacoes.py", "tests/api/cli/test_cli_schema_e_relacoes.py"),
        (CLI, "test_build_native.py", "tests/api/cli/test_build_native.py"),
        (APP, "test_mcp_server.py", "tests/api/mcp/test_mcp_server.py"),
        (APP, "test_api_tarefas.py", "tests/api/http/test_api_tarefas.py"),
        (APP, "test_start_app.py", "tests/api/test_start_app.py"),
        (STARTER, "test_versao.py", "tests/core/test_versao_starter.py"),
        (CLI, "test_versao.py", "tests/api/cli/test_versao_cli.py"),
        (CLI, "test_services_conteudo.py", "tests/services/test_services_conteudo_cli.py"),
        (APP, "test_services_conteudo.py", "tests/services/test_services_conteudo_app.py"),
        (
            STARTER,
            "test_services_inventario_github.py",
            "tests/services/test_services_inventario_github_starter.py",
        ),
        (CLI, "test_integrations_github.py", "tests/integrations/test_integrations_github_cli.py"),
        (APP, "test_integrations_github.py", "tests/integrations/test_integrations_github_app.py"),
    ],
)
def test_pasta_e_nome_do_teste_de_destino(modulo, nome, esperado):
    assert destino_do_teste(modulo, nome) == esperado


def test_nomes_de_teste_repetidos_ganham_sufixo_e_os_demais_nao():
    assert "test_versao.py" in NOMES_DE_TESTE_REPETIDOS
    assert "test_services_conteudo.py" in NOMES_DE_TESTE_REPETIDOS
    assert "test_client.py" not in NOMES_DE_TESTE_REPETIDOS


def test_todo_teste_vai_para_uma_pasta_de_camada():
    movimentos = [m for m in TABELA_MOVIMENTOS if m.origem.split("/")[2:3] == ["tests"]]
    destinos = [m.destino for m in movimentos if m.destino]
    for destino in destinos:
        assert destino.startswith("tests/") and destino.count("/") >= 2, destino
    assert len(destinos) == len(set(destinos))
    # Só o `conftest.py` de cada repositório é removido.
    assert [m.origem.rpartition("/")[2] for m in movimentos if not m.destino] == ["conftest.py"] * 3


# --------------------------------------------------------------------------------------
# Reescrita de código
# --------------------------------------------------------------------------------------


def _reescrever(texto, mapa=MAPA, *, migracao=False):
    return reescrever_codigo(texto, mapa, em_migracao_django=migracao)


def test_import_entre_parenteses_em_varias_linhas():
    novo, _ = _reescrever("from core import (\n    workspaces,\n    outro,\n)\n")
    assert novo == "from felixo_notion_mcp.core import (\n    workspaces,\n    outro,\n)\n"


def test_import_com_comentario_e_recuo_dentro_de_funcao():
    novo, _ = _reescrever("def f():\n    from core import workspaces  # perfis\n    return 1\n")
    assert "    from felixo_notion_mcp.core import workspaces  # perfis\n" in novo


def test_import_de_varios_modulos_numa_linha():
    novo, _ = _reescrever("import os, cli.notion_tasks, core.config as c\n")
    assert novo == (
        "import os, felixo_notion_mcp.api.cli.notion_tasks, felixo_notion_mcp.core.config as c\n"
    )


def test_o_nome_mais_longo_do_mapa_vence():
    novo, _ = _reescrever("import cli.notion_tasks.main\nimport cli.versao\n")
    assert "import felixo_notion_mcp.api.cli.notion_tasks.main\n" in novo
    assert "import felixo_notion_mcp.api.cli.versao\n" in novo


def test_imports_relativos_nao_mudam():
    src = "from . import client\nfrom .client import X\nfrom ..core import y\n"
    assert _reescrever(src)[0] == src


def test_comentarios_e_bytes_nao_mudam():
    src = '# from core import workspaces\n# "cli.notion_tasks.main"\ny = b"core"\n'
    assert _reescrever(src)[0] == src


def test_string_que_e_so_um_nome_antigo_muda_e_com_ponto_ou_dois_pontos_tambem():
    novo, _ = _reescrever(
        'a = "notion_starter"\nb = "cli.notion_tasks:main"\nc = "notion_starter extra"\n'
    )
    assert novo == (
        'a = "felixo_notion_mcp"\n'
        'b = "felixo_notion_mcp.api.cli.notion_tasks:main"\n'
        'c = "notion_starter extra"\n'
    )


def test_nome_comum_sozinho_numa_string_nao_muda_e_vira_aviso():
    analise = reescrever_imports.analisar_codigo(
        'a = "core"\nb = ("api.notion.com", 443)\nc = tmp / "cli"\n',
        MAPA,
        em_migracao_django=False,
    )
    assert analise.texto == 'a = "core"\nb = ("api.notion.com", 443)\nc = tmp / "cli"\n'
    assert len(analise.avisos) == 2  # "core" e "cli"; `api` nem está neste mapa


def test_nome_comum_dentro_de_um_nome_mais_longo_do_mapa_muda():
    mapa = {"api": "n.api.http.rest", "api.urls": "n.api.http.rest.urls", **MAPA}
    novo, _ = _reescrever('a = include("api.urls")\nb = "api.notion.com"\n', mapa)
    assert novo == 'a = include("n.api.http.rest.urls")\nb = "api.notion.com"\n'


def test_string_com_nome_de_arquivo_nao_muda():
    mapa = {"mcp_server": "n.api.mcp.server", "start_app": "n.api.launcher", **MAPA}
    src = 'a = RAIZ / "mcp_server.py"\nb = "start_app.py"\nc = "start_app"\n'
    esperado = 'a = RAIZ / "mcp_server.py"\nb = "start_app.py"\nc = "n.api.launcher"\n'
    assert _reescrever(src, mapa)[0] == esperado


def test_codigo_dentro_de_string_tambem_e_reescrito():
    src = 'cmd = "import sys; import cli.notion_tasks; from core import workspaces as w"\n'
    novo, _ = _reescrever(src)
    assert novo == (
        'cmd = "import sys; import felixo_notion_mcp.api.cli.notion_tasks; '
        'from felixo_notion_mcp.core import workspaces as w"\n'
    )


def test_docstring_so_muda_o_codigo_de_exemplo():
    src = '"""cli.notion_tasks é a borda.\n\n    from core import workspaces\n"""\n'
    novo, _ = _reescrever(src)
    assert novo == (
        '"""cli.notion_tasks é a borda.\n\n    from felixo_notion_mcp.core import workspaces\n"""\n'
    )


def test_migracao_do_django_nao_muda_nem_o_codigo_em_string():
    src = 'x = "core.config"\ny = "import core"\n'
    assert _reescrever(src, migracao=True)[0] == src


def test_import_de_modulo_com_o_mesmo_nome_vira_import_do_novo_pai():
    mapa = {"scripts.build_native": "scripts.empacotamento.build_native"}
    novo, _ = _reescrever("from scripts import build_native as bn, build_native\n", mapa)
    assert novo == "from scripts.empacotamento import build_native as bn, build_native\n"


def test_nomes_que_vao_para_pais_diferentes_viram_pendencia():
    mapa = {
        "notion_starter": "felixo_notion_mcp",
        "notion_starter.properties": "felixo_notion_mcp.domain.properties",
    }
    with pytest.raises(ImportAmbiguo) as erro:
        _reescrever("import os\nfrom notion_starter import NotionClient, properties\n", mapa)
    assert erro.value.linha == 2
    assert "NotionClient, properties" in erro.value.trecho


def test_nome_importado_que_tem_o_nome_de_um_pacote_antigo_nao_e_reescrito_em_string():
    novo, _ = _reescrever('cmd = "from core import cli"\n')
    assert novo == 'cmd = "from felixo_notion_mcp.core import cli"\n'


def test_import_ambiguo_guarda_arquivo_linha_e_trecho():
    erro = ImportAmbiguo("a.py", 3, "from x import y")
    assert (erro.arquivo, erro.linha, erro.trecho) == ("a.py", 3, "from x import y")
    assert "a.py:3" in str(erro)


def test_import_sem_alias_que_perde_o_nome_ligado_e_sinalizado():
    novo, trocas = _reescrever("import notion_starter\n")
    assert novo == "import felixo_notion_mcp\n"
    assert "revise os usos" in trocas[0]


def test_trocas_informam_linha_antigo_e_novo():
    _, trocas = _reescrever("import os\nfrom core import x\n")
    assert trocas == ["linha 2: from core -> felixo_notion_mcp.core"]


def test_acentos_antes_da_string_nao_deslocam_a_troca():
    src = 'f("ação, ção", "cli.notion_tasks.main")\n'
    assert _reescrever(src)[0] == 'f("ação, ção", "felixo_notion_mcp.api.cli.notion_tasks.main")\n'


def test_reescrita_do_mapa_real_e_idempotente():
    mapa = montar_mapa(TABELA_MOVIMENTOS, RAIZES)
    fonte = (
        "from notion_starter.services import conteudo\n"
        "from services import tarefas as svc\n"
        "import server.mcp_server as mcp\n"
        'os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")\n'
        'patch("server.services.tarefas.listar")\n'
    )
    uma, _ = reescrever_codigo(fonte, mapa, em_migracao_django=False)
    assert "notion_starter" not in uma and "server." not in uma
    assert reescrever_codigo(uma, mapa, em_migracao_django=False)[0] == uma


# --------------------------------------------------------------------------------------
# Arquivos e linha de comando
# --------------------------------------------------------------------------------------


def test_arquivo_preserva_bom_e_fim_de_linha_crlf(tmp_path):
    arquivo = tmp_path / "a.py"
    arquivo.write_bytes(f"{BOM}from core import x\r\ny = 1\r\n".encode())
    resultado = reescrever_imports.reescrever_arquivo(arquivo, MAPA, aplicar=True)
    assert resultado.mudou and not resultado.pendencias
    esperado = f"{BOM}from felixo_notion_mcp.core import x\r\ny = 1\r\n"
    assert arquivo.read_bytes() == esperado.encode()


def test_arquivo_em_pasta_migrations_nao_reescreve_strings(tmp_path):
    pasta = tmp_path / "operations" / "migrations"
    pasta.mkdir(parents=True)
    arquivo = pasta / "0001_initial.py"
    arquivo.write_text('dependencies = [("operations", "0001")]\n', encoding="utf-8")
    resultado = reescrever_imports.reescrever_arquivo(arquivo, MAPA, aplicar=True)
    assert not resultado.mudou


def test_arquivo_com_pendencia_aplica_o_resto_e_deixa_o_ambiguo(tmp_path):
    arquivo = tmp_path / "a.py"
    arquivo.write_text("from core import x\nfrom notion_starter import client\n", encoding="utf-8")
    resultado = reescrever_imports.reescrever_arquivo(arquivo, MAPA, aplicar=True)
    assert [p.linha for p in resultado.pendencias] == [2]
    assert arquivo.read_text(encoding="utf-8") == (
        "from felixo_notion_mcp.core import x\nfrom notion_starter import client\n"
    )


def test_arquivo_que_nao_e_python_valido_vira_erro_sem_ser_gravado(tmp_path):
    arquivo = tmp_path / "a.py"
    arquivo.write_text("def f(:\n  x = (\n", encoding="utf-8")
    resultado = reescrever_imports.reescrever_arquivo(arquivo, MAPA, aplicar=True)
    assert resultado.erro


def test_coletar_ignora_a_propria_ferramenta_e_pastas_de_cache(tmp_path):
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "__pycache__" / "x.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / "ok.py").write_text("x = 1\n", encoding="utf-8")
    achados = reescrever_imports.coletar_arquivos([tmp_path])
    assert [a.name for a in achados] == ["ok.py"]
    ferramenta = RAIZ_DO_REPOSITORIO / "scripts" / "migracao"
    assert reescrever_imports.coletar_arquivos([ferramenta]) == []
    assert reescrever_imports.coletar_arquivos([RAIZ_DO_REPOSITORIO / "tests" / "scripts"]) == []


def test_cli_simular_nao_grava_e_aplicar_grava(tmp_path, capsys):
    arquivo = tmp_path / "a.py"
    arquivo.write_text("from cli.notion_tasks import main\n", encoding="utf-8")
    assert reescrever_imports.main(["--simular", str(arquivo)]) == 0
    assert arquivo.read_text(encoding="utf-8") == "from cli.notion_tasks import main\n"
    assert "felixo_notion_mcp.api.cli.notion_tasks" in capsys.readouterr().out
    assert reescrever_imports.main(["--aplicar", str(arquivo)]) == 0
    assert arquivo.read_text(encoding="utf-8") == (
        "from felixo_notion_mcp.api.cli.notion_tasks import main\n"
    )


def test_cli_com_pendencia_sai_com_1_e_lista_arquivo_e_linha(tmp_path, capsys):
    arquivo = tmp_path / "a.py"
    arquivo.write_text("import os\nfrom notion_starter import client\n", encoding="utf-8")
    assert reescrever_imports.main(["--simular", str(arquivo)]) == 1
    assert f"{arquivo.as_posix()}:2" in capsys.readouterr().out


def test_cli_exige_simular_ou_aplicar(tmp_path):
    with pytest.raises(SystemExit):
        reescrever_imports.main([str(tmp_path)])
