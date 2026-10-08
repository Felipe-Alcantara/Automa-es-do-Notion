#!/usr/bin/env python3
"""Aponta para ``Felixo-Notion-MCP`` as tasks dos repositórios do Notion que viraram o monolito.

Uso:
    python3 scripts/notion/atualizar_repositorio_tasks_monolito.py --simular
    python3 scripts/notion/atualizar_repositorio_tasks_monolito.py

Na etapa 1 do monolito (07/10/2026), o hub ``Automa-es-do-Notion`` e os módulos
``notion-starter``, ``notion-tasks-cli`` e ``notion-workspace-app`` viraram um repositório
só, renomeado para ``Felixo-Notion-MCP``. Este script troca a coluna ``Repositório`` das
tasks do To Do List da HOME que ainda apontam para um desses nomes legados e também das
tasks sem repositório cujo título mostra que são do ecossistema do Notion.

É idempotente: task que já aponta para ``Felixo-Notion-MCP`` é pulada, então pode rodar de
novo depois de uma falha de rede. ``--simular`` só lista o que mudaria.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from typing import Any

PERFIL = "home-pessoal"
DATABASE_ID = "30296e2d-cd39-4cf3-8bbd-3fb2f53c0195"
REPOSITORIO_NOVO = "Felixo-Notion-MCP"
REPOSITORIOS_LEGADOS = frozenset(
    {"Automa-es-do-Notion", "notion-starter", "notion-tasks-cli", "notion-workspace-app"}
)
# Prefixos de título que identificam tasks do ecossistema do Notion sem repositório preenchido.
PREFIXOS_DO_NOTION = (
    "Automações do Notion/",
    "Automações/Distribuição",
    "Felixo Notion MCP/",
)


@dataclass(frozen=True)
class Mudanca:
    identificador: str
    titulo: str
    de: str | None


def executar(*argumentos: str) -> dict[str, Any]:
    """Roda ``notion-tasks --json`` no perfil da HOME e devolve o envelope."""

    resultado = subprocess.run(
        ["notion-tasks", "--json", "--perfil", PERFIL, *argumentos],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    try:
        resposta = json.loads(resultado.stdout)
    except json.JSONDecodeError as erro:
        detalhe = resultado.stderr.strip() or resultado.stdout.strip()
        raise RuntimeError(f"Saída não JSON de {argumentos[0]}: {detalhe}") from erro
    if resultado.returncode != 0 or not resposta.get("ok"):
        raise RuntimeError(json.dumps(resposta.get("erro", resposta), ensure_ascii=False))
    return resposta


def planejar(linhas: list[dict[str, Any]]) -> list[Mudanca]:
    """Escolhe as tasks a mudar: repositório legado, ou vazio com título do Notion."""

    mudancas: list[Mudanca] = []
    for linha in linhas:
        propriedades = linha.get("propriedades") or {}
        repositorio = propriedades.get("Repositório")
        titulo = propriedades.get("Tarefa") or ""
        legado = repositorio in REPOSITORIOS_LEGADOS
        sem_repositorio_do_notion = not repositorio and titulo.startswith(PREFIXOS_DO_NOTION)
        if legado or sem_repositorio_do_notion:
            mudancas.append(Mudanca(linha["id"], titulo, repositorio))
    return mudancas


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--simular", action="store_true", help="só lista o que mudaria")
    args = parser.parse_args(argv)

    dados = executar("linhas", DATABASE_ID, "--completo").get("dados", {})
    mudancas = planejar(dados.get("linhas", []) if isinstance(dados, dict) else [])
    for mudanca in mudancas:
        rotulo = mudanca.de or "(vazio)"
        print(f"[{'simula' if args.simular else 'muda'}] {rotulo} -> {REPOSITORIO_NOVO}: "
              f"{mudanca.titulo[:90]}")
        if not args.simular:
            executar("editar-linha", mudanca.identificador, "--set",
                     f"Repositório={REPOSITORIO_NOVO}")
    print(f"{len(mudancas)} task(s) {'a mudar' if args.simular else 'mudada(s)'}.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as erro:
        print(f"Erro: {erro}", file=sys.stderr)
        raise SystemExit(1) from erro
