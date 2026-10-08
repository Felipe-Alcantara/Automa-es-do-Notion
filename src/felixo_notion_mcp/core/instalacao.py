"""Como instalar e atualizar o pacote enquanto a distribuição não está no PyPI.

O nome ``felixo-notion-mcp`` ainda não é do projeto no PyPI: ele só é publicado numa
etapa posterior. Uma mensagem (ou um comando) que mandasse instalar ou atualizar a
distribuição por nome daria a quem registrar o nome antes a execução de código em quem a
seguisse. Por isso toda orientação de instalação e de atualização do código passa por
aqui: aponta o checkout do código-fonte e o extra, e nunca a distribuição.

Só usa a biblioteca padrão, para poder ser importada por ``start_app.py`` e pelo launcher
antes de qualquer dependência estar instalada.
"""

from __future__ import annotations

from pathlib import Path


def raiz_e_checkout(raiz: Path) -> bool:
    """Só é checkout a raiz que tem o ``pyproject.toml`` do projeto.

    Wheel, pipx e binário não têm esse arquivo na raiz: ali não há ``.venv`` do projeto,
    ``front/`` nem ``pull`` a fazer.
    """

    return (raiz / "pyproject.toml").is_file()


def instrucao_de_instalacao(extras: str) -> str:
    """Texto puro que diz como instalar os extras pedidos a partir do checkout.

    Args:
        extras: Um extra do ``pyproject.toml`` ou vários separados por vírgula
            (``"app"``, ``"app,dev"``, ``"planilha"``).
    """

    return (
        "Instale a partir do checkout do código-fonte, de dentro dele: "
        f'`uv sync --all-extras` ou `pip install -e ".[{extras}]"`. '
        "A distribuição ainda não está publicada no PyPI "
        "(a publicação é de uma etapa posterior)."
    )


def instrucao_de_atualizacao(*, em_checkout: bool) -> str:
    """Texto puro que diz como atualizar o código enquanto a distribuição não está no PyPI.

    Nenhum ``pip``/``pipx``/``uv`` que atualize a distribuição por nome: o índice resolveria
    o nome para quem o registrasse (ver o topo deste módulo). No checkout, atualizar é
    atualizar o próprio repositório; fora dele não há o que atualizar daqui, e a orientação
    é instalar a partir do código-fonte.

    Args:
        em_checkout: ``True`` quando o pacote roda de um checkout do código-fonte
            (ver ``raiz_e_checkout``).
    """

    if em_checkout:
        return (
            "Atualize o checkout do código-fonte, de dentro dele: `git pull` e depois "
            '`uv sync --all-extras` ou `pip install -e ".[app]"`. '
            "A distribuição ainda não está publicada no PyPI "
            "(a publicação é de uma etapa posterior)."
        )
    return f"Esta instalação não se atualiza por aqui. {instrucao_de_instalacao('app')}"
