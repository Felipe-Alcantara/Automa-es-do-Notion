import zipfile

from scripts.empacotamento.conferir_wheel import (
    ARQUIVOS_OBRIGATORIOS,
    faltando_no_wheel,
    main,
)


def test_aponta_arquivos_de_dados_ausentes(tmp_path):
    whl = tmp_path / "x.whl"
    with zipfile.ZipFile(whl, "w") as z:
        z.writestr("felixo_notion_mcp/__init__.py", "")
    assert faltando_no_wheel(whl) == list(ARQUIVOS_OBRIGATORIOS)


def test_wheel_completo_nao_falta_nada(tmp_path):
    whl = tmp_path / "x.whl"
    with zipfile.ZipFile(whl, "w") as z:
        for nome in ARQUIVOS_OBRIGATORIOS:
            z.writestr(nome, "")
    assert faltando_no_wheel(whl) == []


def _wheel(caminho, nomes):
    with zipfile.ZipFile(caminho, "w") as z:
        for nome in nomes:
            z.writestr(nome, "")
    return caminho


def test_cli_sai_com_1_e_lista_o_que_falta(tmp_path, capsys):
    whl = _wheel(tmp_path / "x.whl", ARQUIVOS_OBRIGATORIOS[:-1])
    assert main([str(whl)]) == 1
    erro = capsys.readouterr().err
    assert ARQUIVOS_OBRIGATORIOS[-1] in erro
    assert ARQUIVOS_OBRIGATORIOS[0] not in erro


def test_cli_sai_com_0_quando_o_wheel_esta_completo(tmp_path, capsys):
    whl = _wheel(tmp_path / "x.whl", ARQUIVOS_OBRIGATORIOS)
    assert main([str(whl)]) == 0
    assert "ok" in capsys.readouterr().out


def test_cli_expande_curinga_que_o_shell_nao_expandiu(tmp_path):
    _wheel(tmp_path / "x-0.1-py3-none-any.whl", ARQUIVOS_OBRIGATORIOS)
    assert main([str(tmp_path / "*.whl")]) == 0


def test_cli_sem_wheel_encontrado_falha(tmp_path, capsys):
    assert main([str(tmp_path / "*.whl")]) == 1
    assert "Nenhum wheel encontrado" in capsys.readouterr().err


# --- app.js do template e assets que o index.html da SPA referencia ---

RAIZ_SPA = "felixo_notion_mcp/api/http/static/frontend/"
INDEX_DA_SPA = RAIZ_SPA + "index.html"
INDEX_COM_ASSETS = (
    "<!doctype html><html><head>"
    '<script type="module" crossorigin src="/static/frontend/assets/index-AAA.js"></script>'
    '<link rel="stylesheet" crossorigin href="/static/frontend/assets/index-BBB.css">'
    '</head><body><div id="root"></div></body></html>'
)
ASSET_JS = RAIZ_SPA + "assets/index-AAA.js"
ASSET_CSS = RAIZ_SPA + "assets/index-BBB.css"


def _wheel_com_spa(caminho, index_html, assets=(), sem=()):
    """Wheel falso: todos os obrigatórios, o `index.html` dado e só os `assets` listados."""
    with zipfile.ZipFile(caminho, "w") as z:
        for nome in ARQUIVOS_OBRIGATORIOS:
            if nome in sem:
                continue
            z.writestr(nome, index_html if nome == INDEX_DA_SPA else "")
        for nome in assets:
            z.writestr(nome, "")
    return caminho


def test_app_js_do_template_e_obrigatorio(tmp_path):
    app_js = "felixo_notion_mcp/api/http/static/js/app.js"
    assert app_js in ARQUIVOS_OBRIGATORIOS
    whl = _wheel_com_spa(tmp_path / "x.whl", INDEX_COM_ASSETS, [ASSET_JS, ASSET_CSS], sem=[app_js])
    assert faltando_no_wheel(whl) == [app_js]


def test_asset_da_spa_referenciado_e_ausente_e_apontado(tmp_path):
    whl = _wheel_com_spa(tmp_path / "x.whl", INDEX_COM_ASSETS, [ASSET_CSS])
    assert faltando_no_wheel(whl) == [ASSET_JS]


def test_index_sem_nenhum_asset_presente_aponta_todos_na_ordem_do_html(tmp_path):
    whl = _wheel_com_spa(tmp_path / "x.whl", INDEX_COM_ASSETS)
    assert faltando_no_wheel(whl) == [ASSET_JS, ASSET_CSS]


def test_index_com_todos_os_assets_presentes_nao_falta_nada(tmp_path):
    whl = _wheel_com_spa(tmp_path / "x.whl", INDEX_COM_ASSETS, [ASSET_JS, ASSET_CSS])
    assert faltando_no_wheel(whl) == []


def test_sem_index_html_so_o_index_e_apontado(tmp_path):
    whl = _wheel_com_spa(tmp_path / "x.whl", INDEX_COM_ASSETS, [ASSET_JS], sem=[INDEX_DA_SPA])
    assert faltando_no_wheel(whl) == [INDEX_DA_SPA]


def test_obrigatorios_ausentes_vem_antes_dos_assets(tmp_path):
    migracao = ARQUIVOS_OBRIGATORIOS[0]
    whl = _wheel_com_spa(tmp_path / "x.whl", INDEX_COM_ASSETS, [ASSET_CSS], sem=[migracao])
    assert faltando_no_wheel(whl) == [migracao, ASSET_JS]


def test_referencia_repetida_aparece_uma_vez_so(tmp_path):
    repetida = '<link rel="modulepreload" href="/static/frontend/assets/index-AAA.js">'
    html = INDEX_COM_ASSETS + repetida
    whl = _wheel_com_spa(tmp_path / "x.whl", html, [ASSET_CSS])
    assert faltando_no_wheel(whl) == [ASSET_JS]


def test_ignora_query_fragmento_url_externa_e_o_que_nao_e_da_spa(tmp_path):
    html = (
        '<script src="/static/frontend/assets/index-AAA.js?v=3#x"></script>'
        '<link href="https://cdn.exemplo.com/static/frontend/assets/de-fora.css">'
        '<link href="/static/css/app.css">'
        '<img src="data:image/png;base64,AAAA">'
        '<a href="#topo">topo</a>'
    )
    whl = _wheel_com_spa(tmp_path / "x.whl", html)
    assert faltando_no_wheel(whl) == [ASSET_JS]


def test_cli_lista_o_asset_da_spa_que_falta(tmp_path, capsys):
    whl = _wheel_com_spa(tmp_path / "x.whl", INDEX_COM_ASSETS, [ASSET_CSS])
    assert main([str(whl)]) == 1
    assert ASSET_JS in capsys.readouterr().err
