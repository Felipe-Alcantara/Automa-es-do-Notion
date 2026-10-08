"""Aplica a tabela de movimentos de um módulo importado, com `git mv` e `git rm`.

Para cada `Movimento` do módulo escolhido:

- com destino: `git mv` (criando as pastas); se o destino já é um arquivo vazio (os `__init__.py`
  em branco que o monólito criou de partida), o arquivo importado o substitui;
- sem destino: `git rm`;
- `apenas_mapear`: `git rm` da origem, exigindo que o módulo real (o destino) já exista;
- itens já movidos (origem ausente e destino presente) são pulados, então rodar de novo é seguro.

Depois dos movimentos, cria (e passa ao `git add`) os `__init__.py` que as pastas novas precisam.
Tudo é planejado antes: havendo qualquer conflito, nada é alterado.

Uso:
    python -m scripts.migracao.mover_para_camadas --modulo NOME (--simular | --aplicar)
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path

from scripts.migracao.mapa_modulos import (
    MODULOS,
    RAIZ_IMPORTADO,
    TABELA_MOVIMENTOS,
    UNIFICADOS,
    Movimento,
    destinos_conhecidos,
    movimentos_do_modulo,
    pacotes_a_criar,
)

RAIZ = Path(__file__).resolve().parents[2]

MOVER = "mover"
SUBSTITUIR = "substituir"
REMOVER = "remover"
MAPEAR_E_REMOVER = "mapear_e_remover"
CRIAR_PACOTE = "criar_pacote"
PULAR = "pular"


class ErroDeGit(RuntimeError):
    """Um comando `git` falhou durante a aplicação."""


@dataclass(frozen=True)
class Acao:
    """Um passo do plano: o que fazer com `origem` e/ou `destino`."""

    tipo: str
    origem: str = ""
    destino: str = ""
    nota: str = ""


@dataclass
class Plano:
    """Passos planejados para um módulo e os conflitos que impedem aplicá-los."""

    modulo: str
    acoes: list[Acao] = field(default_factory=list)
    erros: list[str] = field(default_factory=list)

    def contar(self, tipo: str) -> int:
        return sum(1 for acao in self.acoes if acao.tipo == tipo)


# --------------------------------------------------------------------------------------
# Planejamento (só lê o disco)
# --------------------------------------------------------------------------------------


def _eh_arquivo_vazio(caminho: Path) -> bool:
    return caminho.is_file() and caminho.stat().st_size == 0


def _planejar_apenas_mapear(
    mov: Movimento,
    raiz: Path,
    produzidos_aqui: set[str],
    conhecidos: frozenset[str],
    plano: Plano,
    *,
    para_aplicar: bool,
) -> None:
    if not (raiz / mov.origem).exists():
        plano.acoes.append(Acao(PULAR, mov.origem, nota="já removido"))
        return
    nota = "módulo real: " + mov.destino
    if mov.destino in UNIFICADOS:
        nota += " (unificado: confira o diff com o destino antes de aplicar)"
    existe = (raiz / mov.destino).exists()
    if not existe and mov.destino not in produzidos_aqui:
        if mov.destino not in conhecidos:
            plano.erros.append(
                f"{mov.origem}: o módulo real '{mov.destino}' não é criado por nenhum movimento "
                "da tabela."
            )
            return
        if para_aplicar:
            plano.erros.append(
                f"{mov.origem}: o módulo real '{mov.destino}' ainda não existe; aplique antes o "
                "módulo que o cria."
            )
            return
        nota += " (será criado por outro módulo)"
    plano.acoes.append(Acao(MAPEAR_E_REMOVER, mov.origem, mov.destino, nota))


def _planejar_movimento(mov: Movimento, raiz: Path, plano: Plano) -> None:
    origem, destino = raiz / mov.origem, raiz / mov.destino
    if not mov.destino:
        if origem.exists():
            plano.acoes.append(Acao(REMOVER, mov.origem))
        else:
            plano.acoes.append(Acao(PULAR, mov.origem, nota="já removido"))
        return
    if not origem.exists():
        if destino.exists():
            plano.acoes.append(Acao(PULAR, mov.origem, mov.destino, "já movido"))
        else:
            plano.erros.append(f"{mov.origem}: nem a origem nem o destino '{mov.destino}' existem.")
        return
    if not destino.exists():
        plano.acoes.append(Acao(MOVER, mov.origem, mov.destino))
    elif origem.is_file() and _eh_arquivo_vazio(destino):
        plano.acoes.append(Acao(SUBSTITUIR, mov.origem, mov.destino, "destino é um arquivo vazio"))
    else:
        plano.erros.append(
            f"{mov.origem}: o destino '{mov.destino}' já existe e não está vazio; "
            "resolva o conflito antes de mover."
        )


def planejar(
    modulo: str,
    raiz: Path,
    movimentos: Sequence[Movimento] = TABELA_MOVIMENTOS,
    *,
    para_aplicar: bool = False,
) -> Plano:
    """Lê o disco e diz o que `--aplicar` faria com o módulo, e o que o impediria.

    Um movimento `apenas_mapear` exige que o módulo real exista. Ao simular, basta que algum
    outro módulo da tabela vá criá-lo; ao aplicar, ele tem de existir (ou ser criado aqui).
    """
    plano = Plano(modulo)
    do_modulo = movimentos_do_modulo(modulo, movimentos)
    conhecidos = destinos_conhecidos(movimentos)
    # `__init__.py` que outro módulo traz de verdade (o `services/` do starter) não é criado aqui.
    trazidos_por_algum = {m.destino for m in movimentos if m.destino and not m.apenas_mapear}
    pacotes = [
        p
        for p in pacotes_a_criar(do_modulo)
        if p not in trazidos_por_algum and not (raiz / p).exists()
    ]
    produzidos_aqui = {m.destino for m in do_modulo if m.destino and not m.apenas_mapear}
    produzidos_aqui.update(pacotes)
    for mov in do_modulo:
        if mov.apenas_mapear:
            _planejar_apenas_mapear(
                mov, raiz, produzidos_aqui, conhecidos, plano, para_aplicar=para_aplicar
            )
        else:
            _planejar_movimento(mov, raiz, plano)
    plano.acoes.extend(Acao(CRIAR_PACOTE, destino=pacote) for pacote in pacotes)
    return plano


# --------------------------------------------------------------------------------------
# Execução
# --------------------------------------------------------------------------------------


def _git(raiz: Path, *argumentos: str) -> None:
    resultado = subprocess.run(
        ["git", *argumentos],
        cwd=raiz,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if resultado.returncode != 0:
        detalhe = (resultado.stderr or resultado.stdout).strip()
        raise ErroDeGit(f"git {' '.join(argumentos)}: {detalhe}")


def _limpar_pastas_vazias(pasta: Path) -> None:
    """Remove as pastas que ficaram vazias depois dos movimentos (o git não guarda pastas)."""
    if not pasta.is_dir():
        return
    for atual, _, _ in os.walk(pasta, topdown=False):
        try:
            Path(atual).rmdir()
        except OSError:
            continue


def executar(plano: Plano, raiz: Path) -> None:
    """Aplica o plano: movimentos e remoções, depois os pacotes novos, depois os shims."""
    for acao in plano.acoes:
        if acao.tipo in (MOVER, SUBSTITUIR):
            (raiz / acao.destino).parent.mkdir(parents=True, exist_ok=True)
            forcar = ["-f"] if acao.tipo == SUBSTITUIR else []
            _git(raiz, "mv", *forcar, "--", acao.origem, acao.destino)
        elif acao.tipo == REMOVER:
            _git(raiz, "rm", "-r", "-q", "--", acao.origem)
    for acao in plano.acoes:
        if acao.tipo == CRIAR_PACOTE:
            arquivo = raiz / acao.destino
            arquivo.parent.mkdir(parents=True, exist_ok=True)
            arquivo.touch()
            _git(raiz, "add", "--", acao.destino)
    for acao in plano.acoes:
        if acao.tipo == MAPEAR_E_REMOVER:
            if not (raiz / acao.destino).exists():
                raise ErroDeGit(f"{acao.origem}: o módulo real '{acao.destino}' ainda não existe.")
            _git(raiz, "rm", "-r", "-q", "--", acao.origem)
    _limpar_pastas_vazias(raiz / RAIZ_IMPORTADO / plano.modulo)


# --------------------------------------------------------------------------------------
# Linha de comando
# --------------------------------------------------------------------------------------

_ROTULOS = {
    MOVER: "mover",
    SUBSTITUIR: "substituir",
    REMOVER: "remover",
    MAPEAR_E_REMOVER: "mapear+remover",
    CRIAR_PACOTE: "criar pacote",
    PULAR: "pular",
}


def _imprimir(plano: Plano) -> None:
    for acao in plano.acoes:
        rotulo = _ROTULOS[acao.tipo]
        if acao.tipo in (MOVER, SUBSTITUIR):
            texto = f"{acao.origem} -> {acao.destino}"
        elif acao.tipo == CRIAR_PACOTE:
            texto = acao.destino
        else:
            texto = acao.origem
        sufixo = f"  ({acao.nota})" if acao.nota else ""
        print(f"  {rotulo:<15} {texto}{sufixo}")


def resumo(plano: Plano) -> str:
    """Uma linha com a contagem de cada tipo de passo."""
    return (
        f"{plano.contar(MOVER)} movimento(s), {plano.contar(SUBSTITUIR)} substituição(ões) de "
        f"arquivo vazio, {plano.contar(REMOVER)} remoção(ões), "
        f"{plano.contar(MAPEAR_E_REMOVER)} apenas_mapear, "
        f"{plano.contar(CRIAR_PACOTE)} pacote(s) novo(s), {plano.contar(PULAR)} já feito(s)"
    )


def _argumentos(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Move os arquivos de um módulo importado para as camadas do monólito."
    )
    parser.add_argument("--modulo", required=True, choices=MODULOS)
    modo = parser.add_mutually_exclusive_group(required=True)
    modo.add_argument("--simular", action="store_true", help="só mostra o plano")
    modo.add_argument("--aplicar", action="store_true", help="aplica com git mv/git rm")
    return parser.parse_args(argv)


def main(
    argv: Sequence[str] | None = None,
    *,
    raiz: Path = RAIZ,
    movimentos: Sequence[Movimento] = TABELA_MOVIMENTOS,
) -> int:
    """Ponto de entrada: planeja, mostra e (com `--aplicar`) executa. Conflito sai com 1."""
    args = _argumentos(argv)
    plano = planejar(args.modulo, raiz, movimentos, para_aplicar=args.aplicar)
    modo = "aplicação" if args.aplicar else "simulação"
    print(f"[{args.modulo}] {modo}")
    _imprimir(plano)
    print(f"\n{resumo(plano)}.")
    if plano.erros:
        print(f"\nConflitos ({len(plano.erros)}); nada foi alterado:", file=sys.stderr)
        for erro in plano.erros:
            print(f"  {erro}", file=sys.stderr)
        return 1
    if args.aplicar:
        try:
            executar(plano, raiz)
        except ErroDeGit as erro:
            print(f"\nFalha ao aplicar: {erro}", file=sys.stderr)
            return 1
        print("Aplicado. Confira com `git status` e rode `reescrever_imports --simular`.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
