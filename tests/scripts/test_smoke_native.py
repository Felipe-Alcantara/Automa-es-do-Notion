"""O smoke do binário confere o que o build real provou: origem congelada e módulos sob demanda."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
from scripts.empacotamento import smoke_native


def _diagnostico(detalhe: str, *, ok: bool = True, nome: str = "felixo-notion-mcp") -> dict:
    return {"ok": ok, "checks": [{"nome": nome, "estado": "ok", "detalhe": detalhe}]}


def test_diagnostico_de_binario_nativo_passa():
    smoke_native.conferir_diagnostico(
        _diagnostico("0.6.0 · /tmp/_MEI123/felixo_notion_mcp · binário nativo")
    )


def test_diagnostico_com_ok_falso_falha():
    with pytest.raises(RuntimeError, match="Doctor do binário"):
        smoke_native.conferir_diagnostico(
            _diagnostico("0.6.0 · /tmp/_MEI123/felixo_notion_mcp · binário nativo", ok=False)
        )


def test_diagnostico_que_se_diz_checkout_editavel_falha():
    """Um binário congelado nunca é um checkout, mesmo com ``pyproject.toml`` por perto."""

    with pytest.raises(RuntimeError, match="binário nativo"):
        smoke_native.conferir_diagnostico(
            _diagnostico("0.6.0 · /repo/src/felixo_notion_mcp · checkout editável")
        )


def test_diagnostico_de_instalacao_comum_nao_vale_para_o_binario():
    with pytest.raises(RuntimeError, match="binário nativo"):
        smoke_native.conferir_diagnostico(
            _diagnostico("0.6.0 · /venv/lib/site-packages/felixo_notion_mcp")
        )


def test_diagnostico_sem_o_check_do_pacote_falha():
    with pytest.raises(RuntimeError, match="felixo-notion-mcp"):
        smoke_native.conferir_diagnostico(_diagnostico("3.13.0", nome="Python"))


def test_modulo_sob_demanda_roda_a_busca_de_conteudo(monkeypatch):
    chamadas = []

    def falso_executar(executavel, *argumentos):
        chamadas.append(argumentos)
        pasta = Path(argumentos[argumentos.index("buscar-conteudo") + 1])
        assert [arquivo.name for arquivo in pasta.iterdir()] == ["pagina.md"]
        return json.dumps({"ok": True, "dados": {"total_paginas": 1}})

    monkeypatch.setattr(smoke_native, "executar", falso_executar)

    smoke_native.conferir_modulo_sob_demanda(Path("binario"))

    (argumentos,) = chamadas
    assert argumentos[:3] == ("--json", "tasks", "buscar-conteudo")


def test_modulo_sob_demanda_que_nao_acha_nada_falha(monkeypatch):
    monkeypatch.setattr(
        smoke_native,
        "executar",
        lambda executavel, *argumentos: json.dumps({"ok": True, "dados": {"total_paginas": 0}}),
    )

    with pytest.raises(RuntimeError, match="buscar-conteudo"):
        smoke_native.conferir_modulo_sob_demanda(Path("binario"))


def test_main_roda_os_comandos_basicos_e_as_duas_conferencias(monkeypatch, tmp_path, capsys):
    executavel = tmp_path / "notion-automacoes-linux-x64"
    executavel.write_bytes(b"binario")
    comandos = []

    def falso_executar(_, *argumentos):
        comandos.append(argumentos)
        if argumentos == ("--version",):
            return "notion-automacoes 0.6.0\n"
        if argumentos == ("--json", "doctor"):
            return json.dumps(
                _diagnostico("0.6.0 · /tmp/_MEI9/felixo_notion_mcp · binário nativo")
            )
        if "buscar-conteudo" in argumentos:
            return json.dumps({"ok": True, "dados": {"total_paginas": 1}})
        return ""

    monkeypatch.setattr(smoke_native, "executar", falso_executar)

    assert smoke_native.main(["--executable", str(executavel), "--version", "v0.6.0"]) == 0

    assert ("--help",) in comandos
    assert ("tasks", "--help") in comandos
    assert ("--json", "doctor") in comandos
    assert any("buscar-conteudo" in argumentos for argumentos in comandos)
    assert "Smoke nativo aprovado" in capsys.readouterr().out


# --------------------------------------------------------------------------------------
# Isolamento: o smoke roda em máquina de dev e na CI de release. Nunca pode disparar o
# auto-update (rede, cache do usuário, troca do binário em teste) nem tocar nos perfis reais.
# --------------------------------------------------------------------------------------

VARIAVEIS_DE_PASTA = (
    "HOME",
    "USERPROFILE",
    "XDG_CONFIG_HOME",
    "XDG_CACHE_HOME",
    "APPDATA",
    "LOCALAPPDATA",
)


class _Execucoes:
    """Dublê de ``subprocess.run`` que guarda o ambiente de cada chamada."""

    def __init__(self) -> None:
        self.chamadas: list[tuple[list[str], dict[str, str]]] = []

    def __call__(self, comando, **opcoes):
        env = opcoes["env"]
        self.chamadas.append((list(comando), dict(env)))
        argumentos = comando[1:]
        # O binário de verdade grava o cache do auto-update na pasta do usuário.
        cache = Path(env["XDG_CACHE_HOME"]) / "notion-automacoes"
        cache.mkdir(parents=True, exist_ok=True)
        (cache / "ultima-verificacao.json").write_text("{}", encoding="utf-8")
        if argumentos == ["--version"]:
            saida = "notion-automacoes 0.6.0\n"
        elif argumentos == ["--json", "doctor"]:
            saida = json.dumps(
                _diagnostico("0.6.0 · /tmp/_MEI9/felixo_notion_mcp · binário nativo")
            )
        elif "buscar-conteudo" in argumentos:
            saida = json.dumps({"ok": True, "dados": {"total_paginas": 1}})
        else:
            saida = ""
        return subprocess.CompletedProcess(comando, 0, stdout=saida, stderr="")


@pytest.fixture
def execucoes(monkeypatch, tmp_path):
    """Roda ``smoke_native`` sem binário: o ``subprocess.run`` é o dublê acima.

    O ``tempfile`` aponta para dentro de ``tmp_path`` e o ambiente "real" do chamador é
    marcado, para que o teste distinga a pasta isolada do que o usuário tem de verdade.
    """

    temporaria = tmp_path / "tmp-do-sistema"
    temporaria.mkdir()
    monkeypatch.setattr(smoke_native.tempfile, "tempdir", str(temporaria))
    for nome in VARIAVEIS_DE_PASTA:
        monkeypatch.setenv(nome, str(tmp_path / "pasta-real-do-usuario" / nome))
    monkeypatch.delenv("NOTION_AUTOMACOES_NO_UPDATE", raising=False)
    monkeypatch.setenv("PATH_DO_CHAMADOR", "preservado")
    dubles = _Execucoes()
    monkeypatch.setattr(smoke_native.subprocess, "run", dubles)
    dubles.temporaria = temporaria
    dubles.pasta_real = tmp_path / "pasta-real-do-usuario"
    return dubles


def _rodar_o_smoke(tmp_path) -> None:
    executavel = tmp_path / "notion-automacoes-linux-x64"
    executavel.write_bytes(b"binario")
    assert smoke_native.main(["--executable", str(executavel), "--version", "v0.6.0"]) == 0


def test_todo_comando_do_smoke_desliga_o_auto_update(execucoes, tmp_path):
    _rodar_o_smoke(tmp_path)

    assert len(execucoes.chamadas) >= 5  # versão, ajuda, tasks --help, doctor, buscar-conteudo
    for comando, env in execucoes.chamadas:
        assert env["NOTION_AUTOMACOES_NO_UPDATE"] == "1", comando


def test_todo_comando_do_smoke_usa_uma_pasta_do_usuario_temporaria(execucoes, tmp_path):
    _rodar_o_smoke(tmp_path)

    for comando, env in execucoes.chamadas:
        base = Path(env["HOME"])
        assert base.is_relative_to(execucoes.temporaria), comando
        for nome in VARIAVEIS_DE_PASTA:
            valor = Path(env[nome])
            assert valor.is_relative_to(base), (comando, nome)
            assert not valor.is_relative_to(execucoes.pasta_real), (comando, nome)
            assert valor != Path.home(), (comando, nome)


def test_a_pasta_temporaria_some_depois_do_comando(execucoes, tmp_path):
    """O cache que o binário grava durante o smoke não sobra no disco."""

    _rodar_o_smoke(tmp_path)

    for _, env in execucoes.chamadas:
        assert not Path(env["HOME"]).exists()
    assert list(execucoes.temporaria.iterdir()) == []


def test_o_resto_do_ambiente_do_chamador_continua_valendo(execucoes, tmp_path):
    _rodar_o_smoke(tmp_path)

    for _, env in execucoes.chamadas:
        assert env["PATH_DO_CHAMADOR"] == "preservado"
        assert env.get("PATH") is not None or sys.platform == "win32"


def test_o_ambiente_chega_de_verdade_ao_processo_filho(monkeypatch, tmp_path):
    """Sem dublê: um Python filho enxerga o mesmo isolamento que o binário enxergaria."""

    monkeypatch.delenv("NOTION_AUTOMACOES_NO_UPDATE", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path / "real"))
    codigo = (
        "import json, os; "
        "print(json.dumps({k: os.environ.get(k) for k in "
        "('NOTION_AUTOMACOES_NO_UPDATE', 'HOME', 'XDG_CACHE_HOME', 'LOCALAPPDATA')}))"
    )

    visto = json.loads(smoke_native.executar(Path(sys.executable), "-c", codigo))

    assert visto["NOTION_AUTOMACOES_NO_UPDATE"] == "1"
    assert visto["HOME"] != str(tmp_path / "real")
    assert visto["XDG_CACHE_HOME"].startswith(visto["HOME"])
    assert visto["LOCALAPPDATA"].startswith(visto["HOME"])
