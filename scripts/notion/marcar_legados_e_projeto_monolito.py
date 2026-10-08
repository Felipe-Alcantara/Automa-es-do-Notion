#!/usr/bin/env python3
"""Põe em dia, no Notion, os nomes novos e legados do monolito Felixo-Notion-MCP.

Uso:
    python3 scripts/notion/marcar_legados_e_projeto_monolito.py --simular
    python3 scripts/notion/marcar_legados_e_projeto_monolito.py

Faz três coisas, todas idempotentes:

1. Na database GITHUB, a linha do hub (``Felipe-Alcantara/Automa-es-do-Notion``) passa a
   se chamar ``Felipe-Alcantara/Felixo-Notion-MCP``, com a URL e a descrição novas. Assim
   o ``atualizar-github`` (que casa linhas pela URL) continua atualizando a mesma linha.
2. As linhas dos forks e do boilerplate que deram origem ao monolito ganham o prefixo
   ``[LEGADO]`` na descrição.
3. No To Do List da HOME, a relação ``Projeto`` das tasks que apontam para uma dessas linhas
   legadas — ou que já têm ``Repositório = Felixo-Notion-MCP`` sem o projeto canônico —
   passa a apontar para a linha canônica do Felixo-Notion-MCP, preservando os outros
   projetos da task.

``--simular`` só lista o que mudaria.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from typing import Any

PERFIL = "home-pessoal"
DATABASE_TASKS = "30296e2d-cd39-4cf3-8bbd-3fb2f53c0195"

LINHA_CANONICA = "38e91f95-497e-8165-a222-d9a5c1bf6467"
NOME_CANONICO = "Felipe-Alcantara/Felixo-Notion-MCP"
URL_CANONICA = "https://github.com/Felipe-Alcantara/Felixo-Notion-MCP"
DESCRICAO_CANONICA = (
    "Felixo Notion MCP: pacote único para operar o Notion por MCP, CLI (notion-tasks) e app "
    "local, organizado por camadas."
)
PREFIXO_LEGADO = "[LEGADO] "
AVISO_LEGADO = "Incorporado ao Felipe-Alcantara/Felixo-Notion-MCP em 07/10/2026. "

# Linhas da database GITHUB que deram origem ao monolito (forks e boilerplate).
LINHAS_LEGADAS = {
    "39f91f95-497e-8100-8d80-e97b027c75d6": "flaviavs-commits/Automa-es-do-Notion",
    "39f91f95-497e-81f3-b87d-f49bd57867a5": "flaviavs-commits/notion-starter",
    "39f91f95-497e-81d9-bf07-c854ae780481": "flaviavs-commits/notion-tasks-cli",
    "38e91f95-497e-81e8-b23f-f0ccc1e6baf8": "flaviavs-commits/notion-starter-boilerplate",
}


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


def propriedades(identificador: str) -> dict[str, Any]:
    dados = executar("conteudo", identificador).get("dados", {})
    return dados.get("propriedades", {}) if isinstance(dados, dict) else {}


def ajustar_linha_canonica(simular: bool) -> None:
    atuais = propriedades(LINHA_CANONICA)
    desejado = {"Nome": NOME_CANONICO, "URL": URL_CANONICA, "Descrição": DESCRICAO_CANONICA}
    diferentes = {k: v for k, v in desejado.items() if atuais.get(k) != v}
    if not diferentes:
        print(f"[ok] {NOME_CANONICO} já está em dia")
        return
    print(f"[{'simula' if simular else 'muda'}] linha canônica: {sorted(diferentes)}")
    if not simular:
        argumentos = ["editar-linha", LINHA_CANONICA]
        for coluna, valor in diferentes.items():
            argumentos += ["--set", f"{coluna}={valor}"]
        executar(*argumentos)


def marcar_legadas(simular: bool) -> None:
    for identificador, nome in LINHAS_LEGADAS.items():
        descricao = propriedades(identificador).get("Descrição") or ""
        if descricao.startswith(PREFIXO_LEGADO):
            print(f"[ok] {nome} já marcada como legado")
            continue
        nova = PREFIXO_LEGADO + AVISO_LEGADO + descricao
        print(f"[{'simula' if simular else 'muda'}] {nome}: descrição com [LEGADO]")
        if not simular:
            executar("editar-linha", identificador, "--set", f"Descrição={nova}")


def repontar_projetos(simular: bool) -> int:
    dados = executar("linhas", DATABASE_TASKS, "--completo").get("dados", {})
    linhas = dados.get("linhas", []) if isinstance(dados, dict) else []
    mudadas = 0
    for linha in linhas:
        props = linha.get("propriedades") or {}
        projetos = list(props.get("Projeto") or [])
        tem_legado = any(p in LINHAS_LEGADAS for p in projetos)
        do_monolito_sem_projeto = (
            props.get("Repositório") == "Felixo-Notion-MCP" and LINHA_CANONICA not in projetos
        )
        if not (tem_legado or do_monolito_sem_projeto):
            continue
        novos = [p for p in projetos if p not in LINHAS_LEGADAS]
        if LINHA_CANONICA not in novos:
            novos.append(LINHA_CANONICA)
        titulo = (props.get("Tarefa") or "")[:90]
        print(f"[{'simula' if simular else 'muda'}] Projeto -> canônico: {titulo}")
        if not simular:
            # ``relacionar`` (e não ``editar-linha --set Projeto=``): o preflight do
            # editar-linha separa o Projeto e a edição fica sem propriedades.
            if LINHA_CANONICA not in projetos:
                executar("relacionar", linha["id"], LINHA_CANONICA, "--coluna", "Projeto")
            for legado in (p for p in projetos if p in LINHAS_LEGADAS):
                executar("relacionar", linha["id"], legado, "--coluna", "Projeto", "--desfazer")
        mudadas += 1
    return mudadas


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--simular", action="store_true", help="só lista o que mudaria")
    args = parser.parse_args(argv)

    ajustar_linha_canonica(args.simular)
    marcar_legadas(args.simular)
    total = repontar_projetos(args.simular)
    print(f"{total} task(s) com Projeto {'a repontar' if args.simular else 'repontado'}.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as erro:
        print(f"Erro: {erro}", file=sys.stderr)
        raise SystemExit(1) from erro
