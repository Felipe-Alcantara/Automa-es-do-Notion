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
