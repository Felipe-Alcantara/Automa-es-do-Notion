"""Retrato (snapshot) do contrato de linha de comando de um parser `argparse`.

O retrato descreve o que a linha de comando **aceita**: subcomandos (com apelidos e se são
obrigatórios), opções, destinos, ações, tipos, aridade, obrigatoriedade, escolhas, valores
padrão e grupos mutuamente exclusivos. Textos de ajuda e `metavar` ficam de fora de
propósito, porque redação não é contrato. O resultado é um dicionário só com tipos JSON,
determinístico, que serve para gravar o contrato da CLI e compará-lo depois da
reorganização do código.
"""

from __future__ import annotations

import argparse
from collections.abc import Callable
from typing import Any


def _nome_do_tipo(tipo: Callable[[str], Any] | None) -> str | None:
    """Nome do conversor `type=` de um argumento, ou `None` quando não há conversor."""
    if tipo is None:
        return None
    return getattr(tipo, "__name__", type(tipo).__name__)


def _retratar_acao(acao: argparse.Action) -> dict[str, Any]:
    """Descreve uma ação (argumento posicional ou opção) do parser."""
    escolhas = None if acao.choices is None else sorted(str(c) for c in acao.choices)
    padrao = None if acao.default == argparse.SUPPRESS else repr(acao.default)
    return {
        "opcoes": sorted(acao.option_strings),
        "destino": acao.dest,
        "acao": type(acao).__name__,
        "nargs": str(acao.nargs),
        "obrigatorio": bool(acao.required),
        "escolhas": escolhas,
        "padrao": padrao,
        "tipo": _nome_do_tipo(acao.type),
    }


def _retratar_exclusivos(parser: argparse.ArgumentParser) -> list[dict[str, Any]]:
    """Descreve os grupos mutuamente exclusivos, em ordem estável (por destinos)."""
    grupos = [
        {
            "obrigatorio": bool(grupo.required),
            "destinos": sorted(acao.dest for acao in grupo._group_actions),
        }
        for grupo in parser._mutually_exclusive_groups
    ]
    return sorted(grupos, key=lambda g: (g["destinos"], g["obrigatorio"]))


def retratar_parser(parser: argparse.ArgumentParser) -> dict[str, Any]:
    """Devolve o retrato do parser e, recursivamente, de todos os seus subcomandos.

    O retrato tem sempre as chaves:

    - `argumentos`: lista, na ordem em que o parser os declarou;
    - `exclusivos`: grupos mutuamente exclusivos (`obrigatorio` e `destinos`);
    - `subcomandos`: nome -> retrato; apelidos aparecem como entradas próprias, cada uma
      com o retrato completo;
    - `subcomandos_obrigatorio`: se o parser exige um subcomando (`False` sem subcomandos);
    - `subcomandos_destino`: `dest` do subparser, ou `None` quando não há ou não foi dado.
    """
    argumentos: list[dict[str, Any]] = []
    subcomandos: dict[str, Any] = {}
    obrigatorio = False
    destino: str | None = None
    for acao in parser._actions:
        if isinstance(acao, argparse._SubParsersAction):
            obrigatorio = bool(acao.required)
            destino = None if acao.dest == argparse.SUPPRESS else acao.dest
            for nome, subparser in acao.choices.items():
                subcomandos[nome] = retratar_parser(subparser)
        else:
            argumentos.append(_retratar_acao(acao))
    return {
        "argumentos": argumentos,
        "exclusivos": _retratar_exclusivos(parser),
        "subcomandos": subcomandos,
        "subcomandos_obrigatorio": obrigatorio,
        "subcomandos_destino": destino,
    }
