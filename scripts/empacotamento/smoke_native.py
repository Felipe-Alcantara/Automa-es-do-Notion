"""Executa comandos básicos diretamente no binário, sem importar o pacote."""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path

#: Nome do check do ``doctor`` que informa de onde o pacote está sendo carregado.
CHECK_DO_PACOTE = "felixo-notion-mcp"


def executar(executavel: Path, *argumentos: str) -> str:
    """Executa o binário e transforma uma falha em erro legível."""

    resultado = subprocess.run(
        [str(executavel), *argumentos],
        capture_output=True,
        text=True,
        check=False,
    )
    if resultado.returncode:
        raise RuntimeError(
            f"Smoke falhou em {' '.join(argumentos)} (código {resultado.returncode}): "
            f"{resultado.stdout}\n{resultado.stderr}"
        )
    return resultado.stdout


def conferir_diagnostico(diagnostico: dict) -> None:
    """Exige ``ok`` e que o pacote seja reconhecido como binário nativo, não como checkout.

    O binário carrega o pacote de uma pasta temporária de extração. Se o ``doctor`` o
    descrevesse como "checkout editável" ou como instalação comum, a origem congelada
    estaria sendo mal lida e quem edita o código seria enganado sobre o que executa.
    """

    if diagnostico.get("ok") is not True:
        raise RuntimeError(f"Doctor do binário retornou erro: {diagnostico!r}")
    check = next(
        (c for c in diagnostico.get("checks", []) if c.get("nome") == CHECK_DO_PACOTE),
        None,
    )
    if check is None:
        raise RuntimeError(f"Doctor do binário sem o check {CHECK_DO_PACOTE!r}: {diagnostico!r}")
    detalhe = str(check.get("detalhe", ""))
    if "binário nativo" not in detalhe or "checkout editável" in detalhe:
        raise RuntimeError(
            f"Doctor não reconheceu o binário nativo (esperado 'binário nativo'): {detalhe!r}"
        )


def conferir_modulo_sob_demanda(executavel: Path) -> None:
    """Roda um comando cujo serviço só é importado quando ele executa.

    ``buscar-conteudo`` carrega ``felixo_notion_mcp.services.busca_conteudo`` por
    ``importlib.import_module``, que o PyInstaller não enxerga sozinho: sem o
    ``--collect-submodules`` o módulo falta e o ``doctor`` continua verde.
    """

    with tempfile.TemporaryDirectory() as pasta:
        (Path(pasta) / "pagina.md").write_text(
            "Plano da publicação do artigo.\n", encoding="utf-8"
        )
        resposta = json.loads(
            executar(executavel, "--json", "tasks", "buscar-conteudo", pasta, "publicacao")
        )
    if resposta.get("ok") is not True or resposta.get("dados", {}).get("total_paginas") != 1:
        raise RuntimeError(f"buscar-conteudo não achou a página de teste no binário: {resposta!r}")


def main(argv: list[str] | None = None) -> int:
    """Confere versão, ajuda, diagnóstico e um serviço carregado sob demanda."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--executable", type=Path, required=True)
    parser.add_argument("--version", required=True)
    args = parser.parse_args(argv)
    executavel = args.executable.resolve()
    if not executavel.is_file():
        raise FileNotFoundError(f"Executável não encontrado: {executavel}")

    versao = executar(executavel, "--version")
    versao_esperada = args.version.removeprefix("v")
    if versao_esperada not in versao:
        raise RuntimeError(
            f"Versão inesperada: {versao!r}; esperado {versao_esperada!r}."
        )
    executar(executavel, "--help")
    executar(executavel, "tasks", "--help")
    conferir_diagnostico(json.loads(executar(executavel, "--json", "doctor")))
    conferir_modulo_sob_demanda(executavel)
    print(f"Smoke nativo aprovado: {executavel.name} ({args.version})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
