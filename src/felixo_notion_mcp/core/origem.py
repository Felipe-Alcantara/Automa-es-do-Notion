"""De onde o pacote ``felixo_notion_mcp`` está sendo carregado.

É a pergunta que o antigo ``check-dev.py`` fazia: "o código que roda é o que eu edito?".
Com o código em três pacotes, uma cópia antiga em ``site-packages`` podia mascarar as
edições locais sem nenhum aviso. No pacote único a pergunta ficou mais simples: o Python
está lendo o checkout (``src/`` com ``pyproject.toml`` dois níveis acima) ou uma instalação?

O ``doctor`` e o Status do menu usam esta mesma resposta. Só biblioteca padrão: o menu a
consulta antes de qualquer dependência estar instalada.
"""

from __future__ import annotations

import importlib.util
import sys
from dataclasses import dataclass
from pathlib import Path

PACOTE = "felixo_notion_mcp"


@dataclass(frozen=True)
class OrigemDoPacote:
    """Onde o pacote está e que tipo de instalação isso indica."""

    pasta: Path
    checkout_editavel: bool
    binario_nativo: bool

    def descricao(self) -> str:
        """Texto curto para o ``doctor`` e o Status: a pasta e, se houver, o tipo."""

        if self.binario_nativo:
            return f"{self.pasta} · binário nativo"
        if self.checkout_editavel:
            return f"{self.pasta} · checkout editável"
        return str(self.pasta)


def _tem_pyproject_dois_niveis_acima(pasta: Path) -> bool:
    """``<checkout>/src/felixo_notion_mcp`` tem o ``pyproject.toml`` em ``<checkout>``."""

    if len(pasta.parents) < 2:
        return False
    return (pasta.parents[1] / "pyproject.toml").is_file()


def origem_do_pacote() -> OrigemDoPacote | None:
    """Localiza o pacote sem importá-lo; ``None`` quando o Python não o enxerga."""

    try:
        spec = importlib.util.find_spec(PACOTE)
    except (ImportError, ValueError):
        return None
    if spec is None or not spec.origin:
        return None

    pasta = Path(spec.origin).resolve().parent
    # No binário congelado o pacote vive numa pasta temporária de extração; um
    # ``pyproject.toml`` solto ao lado dela não faz daquilo um checkout.
    binario = bool(getattr(sys, "frozen", False))
    return OrigemDoPacote(
        pasta=pasta,
        checkout_editavel=not binario and _tem_pyproject_dois_niveis_acima(pasta),
        binario_nativo=binario,
    )
