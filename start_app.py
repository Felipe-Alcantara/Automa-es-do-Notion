#!/usr/bin/env python3
"""Menu de entrada do hub Automações do Notion — a porta de entrada única.

Rode ``python start_app.py`` para abrir um menu interativo onde você instala a
CLI, sincroniza os módulos de desenvolvimento, configura o token do Notion, vê o
estado do ambiente e opera o Notion pela CLI. Não é preciso decorar comando.

Este repositório é o **hub** do ecossistema: ele roteia pedidos de *uso* (via a
CLI ``notion-tasks``) e de *desenvolvimento* (os módulos em ``modules/``). O menu
reflete essas duas frentes, seguindo o contrato de menu de entrada do Felixo
System Design: interativo, colorido e descritivo, com no mínimo Iniciar/Rodar,
Instalar/Setup, Configurar e Status/Sair. Cross-platform (Windows, Linux, macOS),
sem segredo no script — o token vive em ``.env`` ignorado pelo git.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
ENV_FILE = RAIZ / ".env"
BOOTSTRAP = RAIZ / "bootstrap.py"
CHECK_DEV = RAIZ / "check-dev.py"
MODULES_DIR = RAIZ / "modules"

# Pacote pip que expõe a CLI e o módulo importável usado para rodá-la de qualquer
# diretório (``python -m cli.notion_tasks``).
CLI_PACOTE = "notion-tasks-cli"
CLI_MODULO = "cli.notion_tasks"
CLI_INSTALL_URL = "git+https://github.com/Felipe-Alcantara/notion-tasks-cli.git"

# Variáveis que o menu ajuda a preencher no .env. GITHUB_CONTAS alimenta o
# comando `atualizar-github` (sincroniza a database GITHUB do Notion).
VARS_ENV = {
    "NOTION_TOKEN": "Credencial da integração do Notion (começa com ntn_).",
    "NOTION_DATABASE_ID": "ID do database padrão de tarefas.",
    "GITHUB_CONTAS": "Contas do GitHub (CSV) para o comando atualizar-github.",
}

# As deps de TUI são do próprio menu; o passo de Instalar/Setup garante que
# existem. Antes disso, caímos num fallback em texto puro para nunca quebrar.
_DEPS_TUI = ("questionary", "rich")


# --------------------------------------------------------------------------- #
# Infraestrutura: TUI, subprocessos e leitura/escrita de .env                 #
# --------------------------------------------------------------------------- #
def _tui_disponivel() -> bool:
    """Indica se as bibliotecas do menu interativo estão instaladas."""

    return all(importlib.util.find_spec(dep) is not None for dep in _DEPS_TUI)


def _instalar_deps_tui() -> bool:
    """Instala as dependências de TUI do menu. Retorna sucesso."""

    print(f"Instalando dependências do menu ({', '.join(_DEPS_TUI)})...")
    codigo = subprocess.call([sys.executable, "-m", "pip", "install", *_DEPS_TUI])
    if codigo != 0:
        print(
            "Não consegui instalar as dependências do menu. Rode manualmente:\n"
            f"  {sys.executable} -m pip install {' '.join(_DEPS_TUI)}"
        )
        return False
    return True


def _rodar(comando: list[str], *, descricao: str = "") -> int:
    """Executa um comando mostrando o que roda e devolve o exit code."""

    if descricao:
        print(f"\n{descricao}")
    print(f"$ {' '.join(comando)}\n")
    try:
        return subprocess.call(comando)
    except FileNotFoundError as exc:
        print(f"[ERRO] Comando não encontrado: {exc}")
        return 127


def _cli_instalada() -> bool:
    """A CLI notion-tasks está importável neste Python?"""

    return importlib.util.find_spec(CLI_MODULO) is not None


def _cmd_cli(*args: str) -> list[str]:
    """Monta a invocação portátil da CLI (funciona de qualquer diretório)."""

    return [sys.executable, "-m", CLI_MODULO, *args]


def _ler_env() -> dict[str, str]:
    """Lê pares CHAVE=valor do .env (sem expandir, sem dependências externas)."""

    valores: dict[str, str] = {}
    if not ENV_FILE.exists():
        return valores
    for linha in ENV_FILE.read_text(encoding="utf-8").splitlines():
        limpa = linha.strip()
        if not limpa or limpa.startswith("#") or "=" not in limpa:
            continue
        chave, _, valor = limpa.partition("=")
        valores[chave.strip()] = valor.strip().strip('"').strip("'")
    return valores


def _gravar_env(nome: str, valor: str) -> None:
    """Grava/atualiza uma variável no .env, preservando as demais linhas."""

    linhas: list[str] = []
    if ENV_FILE.exists():
        linhas = ENV_FILE.read_text(encoding="utf-8").splitlines()

    prefixo = f"{nome}="
    substituida = False
    for i, linha in enumerate(linhas):
        if linha.strip().startswith(prefixo):
            linhas[i] = f"{nome}={valor}"
            substituida = True
            break
    if not substituida:
        linhas.append(f"{nome}={valor}")
    ENV_FILE.write_text("\n".join(linhas) + "\n", encoding="utf-8")


# --------------------------------------------------------------------------- #
# Ações do menu                                                               #
# --------------------------------------------------------------------------- #
def acao_usar(console) -> None:
    """Iniciar/Rodar (uso): operar o Notion pela CLI notion-tasks."""

    import questionary

    if not _cli_instalada():
        console.print(
            "[yellow]A CLI notion-tasks ainda não está instalada.[/yellow] "
            "Use a opção [bold]Instalar / Setup[/bold] primeiro."
        )
        return

    comandos = [
        ("guia", "Guia completo dos comandos (para IA e humanos)", []),
        ("listar", "Listar tarefas do database configurado", []),
        ("opcoes", "Ver status/durações/áreas válidas", []),
        ("mapear", "Resumir o inventário do workspace", []),
        ("atualizar-github", "Sincronizar a database GITHUB (repos + README)", ["--contas"]),
    ]
    escolhas = [
        questionary.Choice(f"{nome} — {desc}", value=(nome, extra))
        for nome, desc, extra in comandos
    ]
    escolhas.append(questionary.Choice("Outro comando (digitar) …", value=("__livre__", [])))
    escolhas.append(questionary.Choice("← Voltar", value=None))

    escolha = questionary.select("O que você quer fazer no Notion?", choices=escolhas).ask()
    if not escolha:
        return
    nome, extra = escolha

    if nome == "__livre__":
        bruto = questionary.text("Argumentos da CLI (ex.: buscar \"reunião\"):").ask()
        if not bruto:
            return
        import shlex

        _rodar(_cmd_cli(*shlex.split(bruto)), descricao="Executando comando…")
        return

    args = [nome]
    if "--contas" in extra:
        padrao = _ler_env().get("GITHUB_CONTAS", "")
        contas = questionary.text(
            "Contas do GitHub (CSV):", default=padrao
        ).ask()
        if contas:
            args += ["--contas", contas]
    _rodar(_cmd_cli(*args), descricao=f"Executando: notion-tasks {nome}")


def acao_desenvolver(console) -> None:
    """Iniciar/Rodar (dev): sincronizar os módulos e validar o workspace."""

    codigo = _rodar(
        [sys.executable, str(BOOTSTRAP)],
        descricao="[1/2] Sincronizando módulos (bootstrap.py)…",
    )
    if codigo != 0:
        console.print("[red]Falha no bootstrap.[/red] Veja a saída acima.")
        return
    _rodar(
        [sys.executable, str(CHECK_DEV)],
        descricao="[2/2] Validando o workspace (check-dev.py)…",
    )


def acao_instalar(console) -> None:
    """Instalar / Setup: CLI notion-tasks, deps do menu e módulos de dev."""

    import questionary

    opcoes = questionary.checkbox(
        "O que instalar/preparar?",
        choices=[
            questionary.Choice(
                f"CLI notion-tasks ({CLI_PACOTE})", value="cli", checked=not _cli_instalada()
            ),
            questionary.Choice("Dependências do menu (rich, questionary)", value="tui"),
            questionary.Choice("Módulos de desenvolvimento (bootstrap.py)", value="modulos"),
        ],
    ).ask()
    if not opcoes:
        return

    if "cli" in opcoes:
        _rodar(
            [sys.executable, "-m", "pip", "install", CLI_INSTALL_URL],
            descricao="Instalando a CLI notion-tasks…",
        )
    if "tui" in opcoes:
        _instalar_deps_tui()
    if "modulos" in opcoes:
        _rodar([sys.executable, str(BOOTSTRAP)], descricao="Clonando/atualizando módulos…")


def acao_configurar(console) -> None:
    """Configurar: preencher o .env sem editar arquivo na mão."""

    import questionary
    from rich.panel import Panel

    atuais = _ler_env()
    escolha = questionary.select(
        "Qual variável configurar?",
        choices=[
            questionary.Choice(
                f"{nome} — {'definida' if atuais.get(nome) else 'vazia'}", value=nome
            )
            for nome in VARS_ENV
        ]
        + [questionary.Choice("← Voltar", value=None)],
    ).ask()
    if not escolha:
        return

    console.print(Panel(VARS_ENV[escolha], title=escolha, border_style="cyan"))
    secreto = escolha == "NOTION_TOKEN"
    prompt = questionary.password if secreto else questionary.text
    valor = prompt(f"Novo valor para {escolha}:").ask()
    if not valor:
        console.print("[dim]Nada alterado.[/dim]")
        return
    _gravar_env(escolha, valor.strip())
    console.print(f"[green]✓[/green] {escolha} gravado em .env")


def acao_status(console) -> None:
    """Status / Sair: estado real do ambiente (sem chutar)."""

    from rich.table import Table

    tabela = Table(title="Status do hub", show_header=True, header_style="bold")
    tabela.add_column("Item")
    tabela.add_column("Estado")

    def marca(ok: bool) -> str:
        return "[green]OK[/green]" if ok else "[red]falta[/red]"

    tabela.add_row("CLI notion-tasks instalada", marca(_cli_instalada()))
    tabela.add_row("Módulos clonados (modules/)", marca(MODULES_DIR.exists()))
    tabela.add_row(".env presente", marca(ENV_FILE.exists()))

    env = _ler_env()
    for nome in VARS_ENV:
        tabela.add_row(f"  {nome}", marca(bool(env.get(nome))))
    console.print(tabela)

    if CHECK_DEV.exists():
        console.print("\n[dim]Detalhe do workspace (check-dev.py):[/dim]")
        _rodar([sys.executable, str(CHECK_DEV)])


# --------------------------------------------------------------------------- #
# Loop principal                                                              #
# --------------------------------------------------------------------------- #
def _menu(console) -> None:
    import questionary

    acoes = {
        "usar": ("🚀  Usar o Notion (CLI) — operar tarefas, buscar, atualizar GITHUB", acao_usar),
        "dev": ("🛠️   Desenvolver — sincronizar módulos e validar o workspace", acao_desenvolver),
        "instalar": ("📦  Instalar / Setup — CLI, deps do menu, módulos", acao_instalar),
        "configurar": ("⚙️   Configurar — token do Notion, database, contas GitHub", acao_configurar),
        "status": ("📊  Status — estado real do ambiente", acao_status),
    }

    while True:
        console.print()
        escolha = questionary.select(
            "Automações do Notion — o que você quer fazer?",
            choices=[questionary.Choice(rotulo, value=chave) for chave, (rotulo, _) in acoes.items()]
            + [questionary.Choice("❌  Sair", value=None)],
        ).ask()
        if not escolha:
            console.print("[dim]Até logo![/dim]")
            return
        try:
            acoes[escolha][1](console)
        except KeyboardInterrupt:
            console.print("\n[dim]Ação cancelada.[/dim]")
        except Exception as exc:  # noqa: BLE001 — o menu nunca deve quebrar
            console.print(f"[red]Erro na ação:[/red] {exc}")


def main() -> int:
    print("=" * 60)
    print(" Automações do Notion — menu de entrada do hub")
    print("=" * 60)

    if not _tui_disponivel():
        print(
            "\nO menu interativo usa as bibliotecas: "
            f"{', '.join(_DEPS_TUI)}.\n"
        )
        try:
            resposta = input("Instalar agora? [S/n] ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            resposta = "n"
        if resposta in ("", "s", "sim", "y", "yes"):
            if not _instalar_deps_tui():
                return 1
        else:
            print(
                "Sem as dependências não dá para abrir o menu. "
                f"Instale com:\n  {sys.executable} -m pip install {' '.join(_DEPS_TUI)}"
            )
            return 1

    from rich.console import Console

    console = Console()
    try:
        _menu(console)
    except KeyboardInterrupt:
        console.print("\n[dim]Saindo…[/dim]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
