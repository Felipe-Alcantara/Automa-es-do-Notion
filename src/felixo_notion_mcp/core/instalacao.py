"""Como instalar um extra do pacote enquanto a distribuição não está no PyPI.

O nome ``felixo-notion-mcp`` ainda não é do projeto no PyPI: ele só é publicado numa
etapa posterior. Uma mensagem (ou um comando) que mandasse instalar a distribuição por
nome daria a quem registrar o nome antes a execução de código em quem a seguisse. Por
isso toda orientação de instalação do código passa por aqui: aponta o checkout do
código-fonte e o extra, e nunca a distribuição.

Só usa a biblioteca padrão, para poder ser importada por ``start_app.py`` e pelo launcher
antes de qualquer dependência estar instalada.
"""

from __future__ import annotations


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
