"""Testes das f-strings e dos avisos de string pulada no reescritor de imports.

Valem igual em Python 3.10 e 3.11 (f-string é um token só) e em 3.12+ (f-string em vários
tokens): o reescritor lê a f-string pelo texto de ponta a ponta nas duas formas.
"""

from __future__ import annotations

import pytest
from scripts.migracao import reescrever_imports
from scripts.migracao.mapa_modulos import RAIZES, TABELA_MOVIMENTOS, montar_mapa
from scripts.migracao.reescrever_imports import analisar_codigo, reescrever_codigo

MAPA = montar_mapa(TABELA_MOVIMENTOS, RAIZES)


def _analisar(texto, mapa=MAPA):
    return analisar_codigo(texto, mapa, em_migracao_django=False)


# --------------------------------------------------------------------------------------
# f-strings
# --------------------------------------------------------------------------------------


def test_f_string_com_nome_antigo_antes_do_campo_e_reescrita():
    src = 'modulo = importlib.import_module(f"notion_starter.services.{nome}")\n'
    novo, trocas = reescrever_codigo(src, MAPA, em_migracao_django=False)
    assert novo == 'modulo = importlib.import_module(f"felixo_notion_mcp.services.{nome}")\n'
    assert trocas == ["linha 1: string notion_starter.services -> felixo_notion_mcp.services"]


def test_f_string_raw_e_com_aspas_simples_ou_triplas():
    src = "a = rf'cli.notion_tasks.{x}'\nb = f'''notion_starter.services.{y}\nmais'''\n"
    novo, _ = reescrever_codigo(src, MAPA, em_migracao_django=False)
    assert novo == (
        "a = rf'felixo_notion_mcp.api.cli.notion_tasks.{x}'\n"
        "b = f'''felixo_notion_mcp.services.{y}\nmais'''\n"
    )


def test_f_string_sem_campo_e_um_nome_completo():
    novo, _ = reescrever_codigo('x = f"notion_starter"\n', MAPA, em_migracao_django=False)
    assert novo == 'x = f"felixo_notion_mcp"\n'


def test_f_string_em_que_o_nome_continua_no_campo_nao_muda():
    # `notion_starter{sufixo}` é outro identificador, não o nome antigo.
    src = 'x = f"notion_starter{sufixo}"\ny = f"{base}.notion_starter.client"\n'
    assert reescrever_codigo(src, MAPA, em_migracao_django=False)[0] == src


def test_f_string_so_reescreve_a_parte_literal_antes_do_primeiro_campo():
    src = 'm = f"notion_starter.client.{a} e notion_starter.services.{b}"\n'
    novo, _ = reescrever_codigo(src, MAPA, em_migracao_django=False)
    assert novo == (
        'm = f"felixo_notion_mcp.integrations.notion_client.{a} e notion_starter.services.{b}"\n'
    )


def test_f_string_de_frase_com_nome_no_meio_nao_muda():
    src = "m = f\"'{comando}' precisa do serviço notion_starter.services.{nome}, que falta\"\n"
    assert reescrever_codigo(src, MAPA, em_migracao_django=False)[0] == src


def test_f_string_dentro_de_migracao_do_django_nao_muda():
    src = 'x = f"notion_starter.services.{n}"\n'
    assert reescrever_codigo(src, MAPA, em_migracao_django=True)[0] == src


def test_texto_literal_em_campo_de_f_string_nao_e_reescrito_em_nenhuma_versao():
    # Mesma decisão no 3.10 (o campo nem é um token) e no 3.12+ (o campo tem tokens próprios).
    src = "x = f\"{d['cli.notion_tasks']} e {e['notion_starter']}\"\n"
    analise = _analisar(src)
    assert analise.texto == src
    assert analise.trocas == []


def test_texto_literal_em_campo_de_f_string_que_casaria_vira_aviso():
    src = "x = f\"{d['cli.notion_tasks']}\"\ny = f\"{d['qualquer.coisa']}\"\n"
    analise = _analisar(src)
    assert [aviso.linha for aviso in analise.avisos] == [1]
    assert "campo de f-string" in analise.avisos[0].mensagem


def test_f_string_com_nome_comum_antes_do_campo_vira_aviso_e_nao_muda():
    src = 'url = f"api.{host}"\npasta = f"cli.{nome}"\nok = f"x.{y}"\n'
    analise = _analisar(src)
    assert analise.texto == src
    assert [aviso.linha for aviso in analise.avisos] == [1, 2]
    assert all("nome comum" in aviso.mensagem for aviso in analise.avisos)


def test_codigo_dentro_da_parte_literal_de_f_string_tambem_e_reescrito():
    src = 'cmd = f"from core import workspaces; print({x})"\n'
    novo, _ = reescrever_codigo(src, MAPA, em_migracao_django=False)
    assert novo == 'cmd = f"from felixo_notion_mcp.core import workspaces; print({x})"\n'


def test_f_string_concatenada_a_uma_string_comum():
    src = 'm = ("notion_starter.services." f"{nome}")\n'
    novo, _ = reescrever_codigo(src, MAPA, em_migracao_django=False)
    assert novo == 'm = ("felixo_notion_mcp.services." f"{nome}")\n'


def test_f_string_acentuada_e_em_varias_linhas_nao_desloca_a_troca():
    src = 'a = "ação"; b = f"ção {x}"; c = f"notion_starter.services.{n}"\n'
    novo, _ = reescrever_codigo(src, MAPA, em_migracao_django=False)
    assert novo.endswith('c = f"felixo_notion_mcp.services.{n}"\n')
    src2 = 'x = (\n    f"ação {a}"\n    f"{b}"\n    f"notion_starter.services.{n}"\n)\n'
    assert (
        "felixo_notion_mcp.services.{n}"
        in reescrever_codigo(src2, MAPA, em_migracao_django=False)[0]
    )


def test_bytes_continuam_intocados_e_sem_aviso():
    analise = _analisar('x = b"core"\ny = b"mcp_server.py"\n')
    assert analise.texto == 'x = b"core"\ny = b"mcp_server.py"\n'
    assert analise.avisos == []


def test_f_string_reescrita_e_idempotente():
    src = 'm = f"notion_starter.services.{nome}"\n'
    uma, _ = reescrever_codigo(src, MAPA, em_migracao_django=False)
    assert reescrever_codigo(uma, MAPA, em_migracao_django=False)[0] == uma


# --------------------------------------------------------------------------------------
# Avisos
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "literal", ["mcp_server.py", "start_app.py", "manage.py", "api.notion.com"]
)
def test_string_com_extensao_de_arquivo_nao_muda_mas_avisa(literal):
    mapa = {**MAPA, "api": "n.api"}
    src = f'x = RAIZ / "{literal}"\n'
    analise = _analisar(src, mapa)
    assert analise.texto == src
    assert [aviso.linha for aviso in analise.avisos] == [1]
    assert literal in analise.avisos[0].mensagem


def test_string_com_extensao_sem_nome_do_mapa_nao_avisa():
    analise = _analisar('x = "relatorio.py"\ny = "dados.json"\nz = "outro.com"\n')
    assert analise.avisos == []


def test_aviso_de_nome_comum_continua_com_a_linha():
    analise = _analisar('a = 1\nb = "core"\n')
    assert [aviso.linha for aviso in analise.avisos] == [2]
    assert "nome comum" in analise.avisos[0].mensagem


def test_aviso_tem_texto_legivel():
    aviso = _analisar('x = "manage.py"\n').avisos[0]
    assert str(aviso).startswith("linha 1:")


def test_cli_lista_cada_aviso_com_arquivo_e_linha(tmp_path, capsys):
    arquivo = tmp_path / "a.py"
    arquivo.write_text(
        'import os\nx = RAIZ / "mcp_server.py"\ny = f"cli.{nome}"\nz = "core"\n', encoding="utf-8"
    )
    assert reescrever_imports.main(["--simular", str(arquivo)]) == 0
    saida = capsys.readouterr().out
    for linha in (2, 3, 4):
        assert f"{arquivo.as_posix()}:{linha}:" in saida
    assert "NÃO foram alteradas" in saida


def test_cli_sem_aviso_nao_imprime_a_secao(tmp_path, capsys):
    arquivo = tmp_path / "a.py"
    arquivo.write_text("x = 1\n", encoding="utf-8")
    assert reescrever_imports.main(["--simular", str(arquivo)]) == 0
    assert "NÃO foram alteradas" not in capsys.readouterr().out
