"""Retrato (snapshot) do contrato de linha de comando de um parser `argparse`.

O retrato descreve o que a linha de comando **aceita**: subcomandos (com apelidos),
opções, destinos, ações, aridade, obrigatoriedade, escolhas e valores padrão. Textos de
ajuda ficam de fora de propósito, porque redação não é contrato. O resultado é um
dicionário só com tipos JSON, determinístico, que serve para gravar o contrato da CLI e
compará-lo depois da reorganização do código.
"""

from __future__ import annotations

import argparse
from typing import Any


def _retratar_acao(acao: argparse.Action) -> dict[str, Any]:
    """Descreve uma ação (argumento posicional ou opção) do parser."""
    escolhas = None if acao.choices is None else sorted(str(c) for c in acao.choices)
    padrao = None if acao.default is argparse.SUPPRESS else repr(acao.default)
    return {
        "opcoes": sorted(acao.option_strings),
        "destino": acao.dest,
        "acao": type(acao).__name__,
        "nargs": str(acao.nargs),
        "obrigatorio": bool(acao.required),
        "escolhas": escolhas,
        "padrao": padrao,
    }


def retratar_parser(parser: argparse.ArgumentParser) -> dict[str, Any]:
    """Devolve o retrato do parser e, recursivamente, de todos os seus subcomandos.

    O retrato tem sempre duas chaves: `argumentos` (lista, na ordem em que o parser os
    declarou) e `subcomandos` (nome -> retrato). Apelidos de subcomando aparecem como
    entradas próprias em `subcomandos`, cada uma com o retrato completo.
    """
    argumentos: list[dict[str, Any]] = []
    subcomandos: dict[str, Any] = {}
    for acao in parser._actions:
        if isinstance(acao, argparse._SubParsersAction):
            for nome, subparser in acao.choices.items():
                subcomandos[nome] = retratar_parser(subparser)
        else:
            argumentos.append(_retratar_acao(acao))
    return {"argumentos": argumentos, "subcomandos": subcomandos}
