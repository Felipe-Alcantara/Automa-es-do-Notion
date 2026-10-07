"""O smoke do binário confere o que o build real provou: origem congelada e módulos sob demanda."""

from __future__ import annotations

import json
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
