"""Executa comandos básicos diretamente no binário, sem importar o pacote."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
from pathlib import Path

#: Nome do check do ``doctor`` que informa de onde o pacote está sendo carregado.
CHECK_DO_PACOTE = "felixo-notion-mcp"


def ambiente_isolado(base: Path) -> dict[str, str]:
    """Variáveis que isolam o binário da conta de quem roda o smoke.

    O smoke roda em máquina de dev e na CI de release, com o executável de verdade. Sem
    isto, um comando que não seja ``--help``/``doctor`` dispararia o auto-update nativo
    (consulta ao GitHub, escrita no cache do usuário e, havendo Release mais nova, troca
    do binário em teste). As pastas do usuário apontam para dentro de ``base`` nos três
    sistemas: ``HOME``/``USERPROFILE``, ``XDG_*`` (Linux e macOS) e ``APPDATA``/
    ``LOCALAPPDATA`` (Windows); perfis e cache vão para lá e nunca para os reais.
    """

    pastas = {
        "HOME": base,
        "USERPROFILE": base,
        "XDG_CONFIG_HOME": base / "config",
        "XDG_CACHE_HOME": base / "cache",
        "APPDATA": base / "AppData" / "Roaming",
        "LOCALAPPDATA": base / "AppData" / "Local",
    }
    for pasta in pastas.values():
        pasta.mkdir(parents=True, exist_ok=True)
    return {
        "NOTION_AUTOMACOES_NO_UPDATE": "1",
        **{nome: str(pasta) for nome, pasta in pastas.items()},
    }


def executar(executavel: Path, *argumentos: str) -> str:
    """Executa o binário isolado (sem auto-update, pasta do usuário descartável).

    Mantém o resto do ambiente de quem chama (``PATH`` e afins). A pasta temporária some
    ao fim de cada comando, com o cache e os perfis que o binário tenha gravado nela.
    """

    with tempfile.TemporaryDirectory(prefix="smoke-nativo-", ignore_cleanup_errors=True) as pasta:
        resultado = subprocess.run(
            [str(executavel), *argumentos],
            capture_output=True,
            # O binário escreve UTF-8 (acentos da CLI em português); sem isto, no Windows o
            # pai decodificaria com a codepage da localidade (cp1252) e a saída quebraria.
            encoding="utf-8",
            errors="replace",
            check=False,
            env={
                **os.environ,
                "PYTHONIOENCODING": "utf-8",
                "PYTHONUTF8": "1",
                **ambiente_isolado(Path(pasta)),
            },
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
