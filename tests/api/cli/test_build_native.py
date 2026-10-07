"""Testes puros do contrato de empacotamento nativo."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest
from scripts.empacotamento import build_native, native_entrypoint

from felixo_notion_mcp.api.cli import unificada, versao


def test_normaliza_apenas_tags_staveis():
    assert build_native.normalizar_versao("v0.4.0") == "0.4.0"
    assert build_native.normalizar_versao("0.4.1") == "0.4.1"
    with pytest.raises(ValueError, match="Versão inválida"):
        build_native.normalizar_versao("v0.4.0-rc1")


def test_matriz_tem_os_quatro_assets_do_updater():
    assert [alvo.asset for alvo in build_native.ALVOS.values()] == [
        "notion-automacoes-windows-x64.exe",
        "notion-automacoes-macos-x64",
        "notion-automacoes-macos-arm64",
        "notion-automacoes-linux-x64",
    ]


def _argumento_de(comando: list[str], opcao: str) -> list[str]:
    """Valores que seguem cada ocorrência de ``opcao`` no comando do PyInstaller."""

    return [comando[i + 1] for i, item in enumerate(comando) if item == opcao]


def test_comando_embute_versao_e_metadata(tmp_path):
    alvo = build_native.obter_alvo("linux-x64")
    comando = build_native.construir_comando(
        alvo, "0.4.0", tmp_path / "dist", tmp_path / "work"
    )
    assert "--onefile" in comando
    assert _argumento_de(comando, "--copy-metadata") == ["felixo-notion-mcp"]
    assert _argumento_de(comando, "--collect-submodules") == ["felixo_notion_mcp"]
    arquivo_versao = tmp_path / "work" / "felixo-notion-mcp-version.txt"
    assert _argumento_de(comando, "--add-data") == [
        f"{arquivo_versao}{os.pathsep}felixo_notion_mcp/api/cli"
    ]


def test_comando_nao_aponta_mais_para_o_layout_antigo(tmp_path):
    alvo = build_native.obter_alvo("linux-x64")
    comando = build_native.construir_comando(
        alvo, "0.4.0", tmp_path / "dist", tmp_path / "work"
    )
    texto = " ".join(comando)
    assert "notion_starter" not in texto
    assert "notion-automacoes-version" not in texto
    assert "--copy-metadata notion-automacoes" not in texto
    assert not any(item.endswith(f"{os.pathsep}cli") for item in comando)


def test_comando_mantem_o_nome_dos_assets_do_updater(tmp_path):
    """O nome do asset publicado não muda nesta etapa: o updater nativo o procura."""

    alvo = build_native.obter_alvo("linux-x64")
    comando = build_native.construir_comando(
        alvo, "0.4.0", tmp_path / "dist", tmp_path / "work"
    )
    assert _argumento_de(comando, "--name") == ["notion-automacoes-linux-x64"]


def test_arquivo_de_versao_usa_o_mesmo_nome_que_o_executavel_le():
    """O builder grava e o binário lê o mesmo arquivo: um nome só, sem cópia no script."""

    assert versao.NOME_ARQUIVO_VERSAO_NATIVA == "felixo-notion-mcp-version.txt"
    assert build_native.NOME_ARQUIVO_VERSAO_NATIVA == versao.NOME_ARQUIVO_VERSAO_NATIVA


def test_raiz_do_build_e_a_raiz_do_repositorio():
    """O script mora em ``scripts/empacotamento/``: a raiz do repositório está dois níveis acima."""

    assert (build_native.RAIZ / "pyproject.toml").is_file()
    assert (build_native.RAIZ / "src" / "felixo_notion_mcp").is_dir()
    assert build_native.ENTRADA.is_file()
    assert build_native.ENTRADA.parent == build_native.RAIZ / "scripts" / "empacotamento"


def test_entrada_do_pyinstaller_chama_a_cli_unificada():
    assert native_entrypoint.main is unificada.main


def test_construir_roda_o_pyinstaller_na_raiz_e_grava_a_versao(monkeypatch, tmp_path):
    """Sem PyInstaller de verdade: confere cwd, arquivo de versão e checksum do asset."""

    chamadas = []

    def falso_run(comando, cwd=None, check=False, **_):
        chamadas.append((comando, cwd))
        nome = _argumento_de(comando, "--name")[0]
        dist = Path(_argumento_de(comando, "--distpath")[0])
        dist.mkdir(parents=True, exist_ok=True)
        (dist / nome).write_bytes(b"binario")
        arquivo = Path(_argumento_de(comando, "--add-data")[0].split(os.pathsep)[0])
        assert arquivo.read_text(encoding="utf-8") == "0.6.0\n"

    monkeypatch.setattr(build_native.subprocess, "run", falso_run)

    manifesto = build_native.construir("linux-x64", "v0.6.0", tmp_path / "saida")

    (comando, cwd), = chamadas
    assert cwd == build_native.RAIZ
    assert manifesto["versao"] == "0.6.0"
    assert Path(manifesto["executavel"]).name == "notion-automacoes-linux-x64"
    assert (tmp_path / ".native-build-linux-x64" / "felixo-notion-mcp-version.txt").is_file()


def test_sha256_e_checksum_irmão(tmp_path):
    arquivo = tmp_path / "notion-automacoes-linux-x64"
    arquivo.write_bytes(b"binario")
    esperado = hashlib.sha256(b"binario").hexdigest()
    assert build_native.sha256(arquivo) == esperado
    assert build_native.caminho_checksum(arquivo).name == f"{arquivo.name}.sha256"
