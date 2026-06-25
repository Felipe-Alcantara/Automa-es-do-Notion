#!/usr/bin/env python3
"""Menu de entrada do notion-starter-boilerplate — a porta de entrada única do projeto.

Rode ``python start_app.py`` para abrir um menu interativo onde você instala
as dependências, configura o token do Notion, vê o estado do ambiente e roda
os exemplos. Não é preciso decorar comando nenhum.

Segue o contrato de menu de entrada do Felixo System Design: menu interativo,
colorido e descritivo, com no mínimo Iniciar/Rodar, Instalar/Setup, Configurar
e Status/Sair. Cross-platform (Windows, Linux, macOS), sem segredo no script —
o token continua em variável de ambiente / ``.env`` ignorado pelo git.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
ENV_FILE = RAIZ / ".env"
ENV_EXEMPLO = RAIZ / ".env.example"
EXEMPLOS = RAIZ / "examples"
TOKEN_ENV = "NOTION_TOKEN"
TOKEN_PREFIXO = "ntn_"

# As deps de TUI são do próprio menu; o passo de Instalar/Setup garante que
# existem. Antes disso, caímos num fallback em texto puro para nunca quebrar.
_DEPS_TUI = ("questionary", "rich")


# --------------------------------------------------------------------------- #
# Bootstrap das dependências de TUI                                           #
# --------------------------------------------------------------------------- #
def _tui_disponivel() -> bool:
    """Indica se as bibliotecas do menu interativo estão instaladas."""

    try:
        import questionary  # noqa: F401
        import rich  # noqa: F401
    except ImportError:
        return False
    return True


def _instalar_deps_tui() -> bool:
    """Tenta instalar as dependências de TUI do menu. Retorna sucesso."""

    print(f"Instalando dependências do menu ({', '.join(_DEPS_TUI)})...")
    codigo = subprocess.call(
        [sys.executable, "-m", "pip", "install", *_DEPS_TUI]
    )
    if codigo != 0:
        print(
            "Não consegui instalar as dependências do menu. "
            "Instale manualmente com:\n"
            f"  {sys.executable} -m pip install {' '.join(_DEPS_TUI)}"
        )
        return False
    return True


# --------------------------------------------------------------------------- #
# Estado real do ambiente                                                     #
# --------------------------------------------------------------------------- #
def _pacote_instalado() -> bool:
    """Indica se o pacote ``notion_starter`` está importável."""

    try:
        import notion_starter  # noqa: F401
    except ImportError:
        return False
    return True


def _ler_token_env_file() -> str | None:
    """Lê ``NOTION_TOKEN`` do arquivo ``.env`` local, se existir."""

    if not ENV_FILE.exists():
        return None
    for linha in ENV_FILE.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if linha.startswith(f"{TOKEN_ENV}="):
            return linha.split("=", 1)[1].strip()
    return None


def _token_configurado() -> tuple[bool, str]:
    """Resolve a origem do token sem expor o valor.

    Returns:
        ``(configurado, origem)`` — origem é uma descrição legível, nunca o token.
    """

    do_ambiente = os.environ.get(TOKEN_ENV, "").strip()
    if do_ambiente:
        valido = do_ambiente.startswith(TOKEN_PREFIXO)
        return valido, f"variável de ambiente {TOKEN_ENV}" + (
            "" if valido else " (prefixo inesperado)"
        )

    do_arquivo = _ler_token_env_file()
    if do_arquivo and do_arquivo != f"{TOKEN_PREFIXO}xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx":
        valido = do_arquivo.startswith(TOKEN_PREFIXO)
        return valido, ".env local" + ("" if valido else " (prefixo inesperado)")

    return False, "não configurado"


# --------------------------------------------------------------------------- #
# Ações do menu                                                               #
# --------------------------------------------------------------------------- #
def acao_instalar(console) -> None:
    """Instala/Setup: dependências da lib (modo dev) e cria o ``.env``."""

    console.rule("[bold]Instalar / Setup")
    console.print(f"Instalando o pacote em modo editável com extras de dev "
                  f"(pip install -e \".[dev]\") usando {sys.executable}...")
    codigo = subprocess.call(
        [sys.executable, "-m", "pip", "install", "-e", ".[dev]"], cwd=RAIZ
    )
    if codigo == 0:
        console.print("[green]✓[/green] Pacote e dependências de dev instalados.")
    else:
        console.print(
            "[red]✗[/red] Falha ao instalar. Verifique sua conexão e o pip e "
            "tente de novo por aqui."
        )

    if not ENV_FILE.exists() and ENV_EXEMPLO.exists():
        ENV_FILE.write_text(ENV_EXEMPLO.read_text(encoding="utf-8"), encoding="utf-8")
        console.print(
            "[green]✓[/green] Criado [bold].env[/bold] a partir de .env.example — "
            "edite-o (Configurar) e coloque seu token."
        )
    elif ENV_FILE.exists():
        console.print("[yellow]•[/yellow] .env já existe — mantido como está.")


def acao_configurar(console) -> None:
    """Configurar: orienta como apontar o token do Notion (sem editar à mão)."""

    import questionary
    from rich.panel import Panel

    console.rule("[bold]Configurar")
    configurado, origem = _token_configurado()
    console.print(f"Token atual: [bold]{origem}[/bold].")
    console.print(
        "O token nunca é gravado neste script. Ele vive na variável de ambiente "
        f"[bold]{TOKEN_ENV}[/bold] ou no arquivo [bold].env[/bold] (ignorado pelo git).\n"
    )

    console.print(
        Panel(
            "[bold]1.[/bold] Acesse [cyan]https://www.notion.so/my-integrations[/cyan] "
            "e clique em [bold]New integration[/bold].\n"
            "[bold]2.[/bold] Dê um nome, escolha o workspace e salve. Em "
            "[bold]Configuration[/bold], copie o [bold]Internal Integration Secret[/bold] "
            f"(começa com [bold]{TOKEN_PREFIXO}[/bold]) — é o token que você vai colar aqui.\n"
            "[bold]3.[/bold] Abra no Notion a página ou o database que quer usar, clique no "
            "menu [bold]•••[/bold] (canto superior direito) → [bold]Conexões[/bold] / "
            "[bold]Connections[/bold] e selecione a integração que você acabou de criar.\n"
            "   [dim]Sem este passo o token é válido, mas não enxerga nada — o Notion só "
            "expõe à integração o que foi explicitamente compartilhado com ela.[/dim]\n"
            "[bold]4.[/bold] Volte aqui e cole o token abaixo. Depois, em "
            "[bold]Status[/bold], confira se ele foi reconhecido.",
            title="[bold]Como obter o token do Notion (passo a passo)",
            border_style="cyan",
            padding=(1, 2),
        )
    )

    if not questionary.confirm("Já tem o token em mãos para colar agora?").ask():
        console.print(
            "[dim]Sem problema. Siga os passos acima e volte em "
            "[bold]Configurar[/bold] quando tiver o token.[/dim]"
        )
        return

    if not ENV_FILE.exists() and ENV_EXEMPLO.exists():
        if questionary.confirm("Criar um .env a partir do .env.example agora?").ask():
            ENV_FILE.write_text(ENV_EXEMPLO.read_text(encoding="utf-8"), encoding="utf-8")
            console.print("[green]✓[/green] .env criado.")

    novo = questionary.password(
        f"Cole um token do Notion para gravar no .env (começa com '{TOKEN_PREFIXO}'), "
        "ou deixe em branco para não alterar:"
    ).ask()
    if novo:
        novo = novo.strip()
        if not novo.startswith(TOKEN_PREFIXO):
            console.print(
                f"[yellow]Aviso:[/yellow] o token não começa com '{TOKEN_PREFIXO}'. "
                "Gravando assim mesmo — confira se está correto."
            )
        _gravar_token_env_file(novo)
        console.print(
            "[green]✓[/green] Token gravado em .env. "
            "Ele não aparece nos logs nem no histórico do git."
        )
    else:
        console.print("[dim]Token inalterado.[/dim]")
        console.print(
            f"Dica: você também pode exportar no shell — "
            f"[bold]export {TOKEN_ENV}={TOKEN_PREFIXO}...[/bold]"
        )


def _gravar_token_env_file(token: str) -> None:
    """Grava/atualiza ``NOTION_TOKEN`` no ``.env`` preservando o resto."""

    linhas: list[str] = []
    achou = False
    if ENV_FILE.exists():
        linhas = ENV_FILE.read_text(encoding="utf-8").splitlines()
    for i, linha in enumerate(linhas):
        if linha.strip().startswith(f"{TOKEN_ENV}="):
            linhas[i] = f"{TOKEN_ENV}={token}"
            achou = True
            break
    if not achou:
        linhas.append(f"{TOKEN_ENV}={token}")
    ENV_FILE.write_text("\n".join(linhas) + "\n", encoding="utf-8")


def acao_rodar(console) -> None:
    """Iniciar / Rodar: submenu com os exemplos executáveis da biblioteca."""

    import questionary

    console.rule("[bold]Iniciar / Rodar")

    if not _pacote_instalado():
        console.print(
            "[yellow]•[/yellow] O pacote notion_starter ainda não está importável. "
            "Use [bold]Instalar / Setup[/bold] primeiro "
            "(o menu não obriga, mas os exemplos vão falhar sem ele)."
        )
    configurado, origem = _token_configurado()
    if not configurado:
        console.print(
            f"[yellow]•[/yellow] Token {origem}. Os exemplos chamam a API do Notion "
            "e vão falhar sem um token válido — ajuste em [bold]Configurar[/bold]."
        )

    escolha = questionary.select(
        "O que você quer rodar?",
        choices=[
            questionary.Choice(
                "export_rows.py — cria uma página por linha de exemplo num database",
                value="export_rows",
            ),
            questionary.Choice(
                "check_schema.py — valida o schema de um database contra o esperado",
                value="check_schema",
            ),
            questionary.Choice(
                "sync_from_csv.py — valida o schema e cria uma página por linha de um CSV",
                value="sync_from_csv",
            ),
            questionary.Choice(
                "gerenciar_tarefas.py — lista, cria e conclui tarefas via TaskList",
                value="gerenciar_tarefas",
            ),
            questionary.Choice("Voltar", value=None),
        ],
    ).ask()

    if not escolha:
        return

    database_id = questionary.text(
        "ID do database do Notion (deixe em branco para cancelar):"
    ).ask()
    if not database_id:
        console.print("[dim]Cancelado.[/dim]")
        return

    args = [database_id.strip()]
    if escolha == "sync_from_csv":
        caminho_csv = questionary.text(
            "Caminho do arquivo CSV (deixe em branco para cancelar):"
        ).ask()
        if not caminho_csv:
            console.print("[dim]Cancelado.[/dim]")
            return
        args.append(caminho_csv.strip())

    script = EXEMPLOS / f"{escolha}.py"
    console.print(f"Executando [bold]{script.name}[/bold]...\n")
    ambiente = dict(os.environ)
    token_arquivo = _ler_token_env_file()
    if token_arquivo and not ambiente.get(TOKEN_ENV):
        ambiente[TOKEN_ENV] = token_arquivo  # passa o token do .env só ao subprocesso
    codigo = subprocess.call(
        [sys.executable, str(script), *args], cwd=RAIZ, env=ambiente
    )
    if codigo == 0:
        console.print("\n[green]✓[/green] Exemplo concluído.")
    else:
        console.print(
            f"\n[red]✗[/red] O exemplo terminou com código {codigo}. "
            "Confira o token, o ID do database e a mensagem acima."
        )


def acao_mapear(console) -> None:
    """Mapear workspace: coleta o mapa e gera o relatório HTML navegável."""

    console.rule("[bold]Mapear workspace")

    if not _pacote_instalado():
        console.print(
            "[yellow]•[/yellow] O pacote notion_starter não está importável. "
            "Use [bold]Instalar / Setup[/bold] primeiro."
        )
        return
    configurado, origem = _token_configurado()
    if not configurado:
        console.print(
            f"[yellow]•[/yellow] Token {origem}. O mapeamento chama a API do Notion "
            "e vai falhar sem um token válido — ajuste em [bold]Configurar[/bold]."
        )
        return

    ambiente = dict(os.environ)
    token_arquivo = _ler_token_env_file()
    if token_arquivo and not ambiente.get(TOKEN_ENV):
        ambiente[TOKEN_ENV] = token_arquivo

    console.print("Coletando o mapa do workspace (pode levar ~1 min)...")
    codigo = subprocess.call(
        [sys.executable, str(EXEMPLOS / "coletar_mapa.py")], cwd=RAIZ, env=ambiente
    )
    if codigo != 0:
        console.print(f"[red]✗[/red] Falha na coleta (código {codigo}).")
        return

    console.print("Gerando o relatório HTML...")
    codigo = subprocess.call(
        [sys.executable, str(EXEMPLOS / "gerar_arvore_html.py")], cwd=RAIZ, env=ambiente
    )
    if codigo == 0:
        console.print(
            "[green]✓[/green] Pronto: [bold]mapa.json[/bold] e [bold]mapa.html[/bold] "
            "na raiz do projeto. Abra o HTML no navegador."
        )
    else:
        console.print(f"[red]✗[/red] Falha ao gerar o HTML (código {codigo}).")


def acao_status(console) -> None:
    """Status: mostra o estado real do ambiente, sem expor segredo."""

    from rich.table import Table

    console.rule("[bold]Status")
    tabela = Table(show_header=True, header_style="bold")
    tabela.add_column("Item")
    tabela.add_column("Estado")

    py = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    py_ok = sys.version_info >= (3, 10)
    tabela.add_row(
        "Python", f"[green]{py}[/green]" if py_ok else f"[red]{py} (requer 3.10+)[/red]"
    )

    if _pacote_instalado():
        import notion_starter

        tabela.add_row(
            "Pacote notion_starter",
            f"[green]instalado[/green] (v{getattr(notion_starter, '__version__', '?')})",
        )
    else:
        tabela.add_row(
            "Pacote notion_starter", "[yellow]não instalado[/yellow] (use Instalar/Setup)"
        )

    tabela.add_row(
        "Deps do menu (rich/questionary)",
        "[green]ok[/green]" if _tui_disponivel() else "[yellow]faltando[/yellow]",
    )
    tabela.add_row(
        "Arquivo .env",
        "[green]existe[/green]" if ENV_FILE.exists() else "[yellow]ausente[/yellow]",
    )
    configurado, origem = _token_configurado()
    tabela.add_row(
        f"Token ({TOKEN_ENV})",
        f"[green]{origem}[/green]" if configurado else f"[yellow]{origem}[/yellow]",
    )

    console.print(tabela)


# --------------------------------------------------------------------------- #
# Loop do menu                                                                #
# --------------------------------------------------------------------------- #
def _menu_loop() -> None:
    """Desenha o menu interativo e despacha as ações até a pessoa sair."""

    import questionary
    from rich.console import Console
    from rich.panel import Panel

    console = Console()
    console.print(
        Panel.fit(
            "[bold cyan]notion-starter-boilerplate[/bold cyan]\n"
            "Ponto de partida tipado para construir projetos sobre a API do Notion.\n"
            "[dim]Instale, configure o token, veja o status e rode os exemplos.[/dim]",
            border_style="cyan",
        )
    )

    acoes = {
        "rodar": ("▶  Iniciar / Rodar — executa um exemplo da biblioteca", acao_rodar),
        "mapear": ("🗺  Mapear workspace — gera mapa.json e mapa.html navegável", acao_mapear),
        "instalar": ("⬇  Instalar / Setup — instala deps e cria o .env", acao_instalar),
        "configurar": ("⚙  Configurar — aponta o token do Notion", acao_configurar),
        "status": ("ℹ  Status — mostra o estado real do ambiente", acao_status),
    }

    while True:
        escolha = questionary.select(
            "O que você quer fazer?",
            choices=[
                *(questionary.Choice(texto, value=chave) for chave, (texto, _) in acoes.items()),
                questionary.Choice("⏿  Sair", value="sair"),
            ],
        ).ask()

        if escolha in (None, "sair"):
            console.print("[dim]Até mais![/dim]")
            return

        try:
            acoes[escolha][1](console)
        except KeyboardInterrupt:
            console.print("\n[dim]Ação interrompida.[/dim]")
        except Exception as exc:  # noqa: BLE001 - o menu nunca quebra com stack trace cru
            console.print(f"[red]Erro:[/red] {exc}")
            console.print("[dim]Voltando ao menu.[/dim]")

        console.print()


def main() -> None:
    """Ponto de entrada: garante a TUI e abre o menu (ou um fallback claro)."""

    if not _tui_disponivel():
        print(
            "O menu interativo precisa de 'questionary' e 'rich'.\n"
            "Posso instalá-los agora neste ambiente Python."
        )
        resposta = input("Instalar agora? [S/n] ").strip().lower()
        if resposta in ("", "s", "sim", "y", "yes"):
            if not _instalar_deps_tui() or not _tui_disponivel():
                raise SystemExit(1)
        else:
            print(
                "Sem as dependências do menu não dá para abrir a TUI. "
                f"Instale quando quiser:\n  {sys.executable} -m pip install "
                f"{' '.join(_DEPS_TUI)}"
            )
            raise SystemExit(1)

    try:
        _menu_loop()
    except KeyboardInterrupt:
        print("\nAté mais!")


if __name__ == "__main__":
    main()
