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

import json
import os
import shlex
import shutil
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
ENV_FILE = RAIZ / ".env"
ENV_EXEMPLO = RAIZ / ".env.example"
EXEMPLOS = RAIZ / "examples"
SERVIDOR = RAIZ / "server"
MANAGE_PY = SERVIDOR / "manage.py"
TOKEN_ENV = "NOTION_TOKEN"
DATABASE_ENV = "NOTION_DATABASE_ID"
TOKEN_PREFIXO = "ntn_"
APP_ENDERECO_PADRAO = "127.0.0.1:8000"
APP_URL = f"http://{APP_ENDERECO_PADRAO}/"
APP_HEALTH_URL = f"{APP_URL}api/health"

# As deps de TUI são do próprio menu; o passo de Instalar/Setup garante que
# existem. Antes disso, caímos num fallback em texto puro para nunca quebrar.
_DEPS_TUI = ("questionary", "rich")


# --------------------------------------------------------------------------- #
# Terminais dedicados                                                        #
# --------------------------------------------------------------------------- #
def _comando_acao(chave: str) -> list[str]:
    """Monta o comando que executa uma única ação fora do menu principal."""

    return [sys.executable, str(Path(__file__).resolve()), "--action", chave]


def _comando_terminal_linux(
    comando: list[str],
    titulo: str,
) -> list[str] | None:
    """Escolhe um emulador de terminal Linux disponível."""

    terminal_configurado = os.environ.get("TERMINAL", "").strip()
    if terminal_configurado:
        partes = shlex.split(terminal_configurado)
        executavel = shutil.which(partes[0])
        if executavel:
            return [executavel, *partes[1:], "-e", *comando]

    candidatos = (
        ("konsole", lambda exe: [exe, "--separate", "-p", f"tabtitle={titulo}", "-e", *comando]),
        ("gnome-terminal", lambda exe: [exe, f"--title={titulo}", "--", *comando]),
        ("kgx", lambda exe: [exe, "--title", titulo, "--", *comando]),
        (
            "xfce4-terminal",
            lambda exe: [exe, f"--title={titulo}", f"--command={shlex.join(comando)}"],
        ),
        ("mate-terminal", lambda exe: [exe, f"--title={titulo}", "--", *comando]),
        ("kitty", lambda exe: [exe, "--title", titulo, *comando]),
        ("alacritty", lambda exe: [exe, "--title", titulo, "-e", *comando]),
        (
            "wezterm",
            lambda exe: [
                exe,
                "start",
                "--always-new-process",
                "--cwd",
                str(RAIZ),
                "--",
                *comando,
            ],
        ),
        ("foot", lambda exe: [exe, f"--title={titulo}", "--", *comando]),
        ("xterm", lambda exe: [exe, "-T", titulo, "-e", *comando]),
        ("x-terminal-emulator", lambda exe: [exe, "-T", titulo, "-e", *comando]),
    )
    for nome, montar in candidatos:
        executavel = shutil.which(nome)
        if executavel:
            return montar(executavel)
    return None


def _abrir_terminal_dedicado(chave: str, titulo: str) -> tuple[bool, str]:
    """Abre uma ação em outro terminal, sem bloquear o menu atual."""

    comando = _comando_acao(chave)
    kwargs: dict[str, object] = {
        "cwd": RAIZ,
        "start_new_session": True,
    }

    try:
        if sys.platform == "win32":
            kwargs.pop("start_new_session")
            kwargs["creationflags"] = getattr(
                subprocess,
                "CREATE_NEW_CONSOLE",
                0x00000010,
            )
            subprocess.Popen(comando, **kwargs)
        elif sys.platform == "darwin":
            comando_shell = f"cd {shlex.quote(str(RAIZ))} && {shlex.join(comando)}"
            comando_apple = comando_shell.replace("\\", "\\\\").replace('"', '\\"')
            script = f'tell application "Terminal" to do script "{comando_apple}"'
            subprocess.Popen(["osascript", "-e", script], **kwargs)
        else:
            comando_terminal = _comando_terminal_linux(comando, titulo)
            if comando_terminal is None:
                return (
                    False,
                    "Nenhum emulador de terminal compatível foi encontrado. "
                    "Configure a variável TERMINAL ou instale Konsole, GNOME Terminal, "
                    "Kitty, Alacritty, XTerm ou equivalente.",
                )
            subprocess.Popen(comando_terminal, **kwargs)
    except OSError as exc:
        return False, f"Não foi possível abrir o terminal dedicado: {exc}"

    return True, f"Terminal dedicado aberto para: {titulo}"


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
    codigo = subprocess.call([sys.executable, "-m", "pip", "install", *_DEPS_TUI])
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


def _django_disponivel() -> bool:
    """Indica se o Django (extra de servidor) está instalado."""

    try:
        import django  # noqa: F401
    except ImportError:
        return False
    return True


def _mcp_disponivel() -> bool:
    """Indica se o SDK MCP está instalado."""

    try:
        import mcp  # noqa: F401
    except ImportError:
        return False
    return True


def _ler_valor_env_file(nome: str) -> str | None:
    """Lê uma variável do arquivo ``.env`` local, se existir."""

    if not ENV_FILE.exists():
        return None
    for linha in ENV_FILE.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if linha.startswith(f"{nome}="):
            return linha.split("=", 1)[1].strip()
    return None


def _ler_token_env_file() -> str | None:
    """Lê ``NOTION_TOKEN`` do arquivo ``.env`` local, se existir."""

    return _ler_valor_env_file(TOKEN_ENV)


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
    console.print(
        f"Instalando o pacote em modo editável com extras de dev "
        f'(pip install -e ".[dev]") usando {sys.executable}...'
    )
    codigo = subprocess.call([sys.executable, "-m", "pip", "install", "-e", ".[dev]"], cwd=RAIZ)
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
    codigo = subprocess.call([sys.executable, str(script), *args], cwd=RAIZ, env=ambiente)
    if codigo == 0:
        console.print("\n[green]✓[/green] Exemplo concluído.")
    else:
        console.print(
            f"\n[red]✗[/red] O exemplo terminou com código {codigo}. "
            "Confira o token, o ID do database e a mensagem acima."
        )


def _instalar_extra_servidor(console) -> bool:
    """Instala o extra Django e confirma que ele ficou importável."""

    console.print("Instalando os componentes do servidor web...")
    codigo = subprocess.call(
        [sys.executable, "-m", "pip", "install", "-e", ".[server]"],
        cwd=RAIZ,
    )
    if codigo == 0 and _django_disponivel():
        console.print("[green]✓[/green] Componentes do servidor instalados.")
        return True

    console.print(
        "[red]✗[/red] Não consegui instalar o Django. Instale manualmente:\n"
        f'  {sys.executable} -m pip install -e ".[server]"'
    )
    return False


def _ambiente_servidor() -> dict[str, str]:
    """Monta o ambiente local do Django sem expor o token."""

    ambiente = dict(os.environ)
    ambiente.setdefault("DJANGO_DEBUG", "1")
    token_arquivo = _ler_token_env_file()
    if token_arquivo and not ambiente.get(TOKEN_ENV):
        ambiente[TOKEN_ENV] = token_arquivo
    return ambiente


def _aplicar_migracoes(console, ambiente: dict[str, str]) -> bool:
    """Aplica as migrações operacionais antes de iniciar o app."""

    console.print("Aplicando migrações do estado operacional (SQLite)...")
    codigo = subprocess.call(
        [sys.executable, str(MANAGE_PY), "migrate", "--noinput"],
        cwd=SERVIDOR,
        env=ambiente,
    )
    if codigo == 0:
        return True
    console.print(f"[red]✗[/red] Falha ao migrar (código {codigo}).")
    return False


def _app_web_ativo(url: str = APP_HEALTH_URL) -> bool:
    """Confirma que a porta responde como este projeto, não apenas que está ocupada."""

    try:
        with urllib.request.urlopen(url, timeout=0.5) as resposta:  # noqa: S310 - URL local fixa
            corpo = json.loads(resposta.read().decode("utf-8"))
    except (json.JSONDecodeError, OSError, UnicodeError, urllib.error.URLError):
        return False
    return (
        isinstance(corpo, dict)
        and corpo.get("status") == "ok"
        and corpo.get("service") == "automacoes-notion"
    )


def _abrir_navegador_quando_pronto(
    console,
    *,
    tentativas: int = 40,
    intervalo: float = 0.25,
) -> None:
    """Espera o health check responder e abre o front no navegador padrão."""

    for _ in range(tentativas):
        if _app_web_ativo():
            if webbrowser.open(APP_URL):
                console.print(f"[green]✓[/green] Navegador aberto em [bold]{APP_URL}[/bold].")
            else:
                console.print(
                    "[yellow]•[/yellow] O navegador não abriu automaticamente. "
                    f"Acesse [bold]{APP_URL}[/bold]."
                )
            return
        time.sleep(intervalo)

    console.print(
        "[yellow]•[/yellow] O servidor demorou para responder. "
        f"Quando estiver pronto, acesse [bold]{APP_URL}[/bold]."
    )


def _agendar_abertura_navegador(console) -> None:
    """Inicia em background a espera pelo servidor e a abertura do navegador."""

    threading.Thread(
        target=_abrir_navegador_quando_pronto,
        args=(console,),
        daemon=True,
        name="abrir-navegador-notion",
    ).start()


def acao_iniciar_tudo(console) -> None:
    """Inicia front + API com defaults locais e abre o navegador."""

    console.rule("[bold]Iniciar tudo")

    if not _django_disponivel() and not _instalar_extra_servidor(console):
        return

    configurado, origem = _token_configurado()
    if not configurado:
        console.print(
            f"[yellow]•[/yellow] Token {origem}. O app abre normalmente, mas as tarefas "
            "do Notion só carregam depois de configurar o token."
        )

    if _app_web_ativo():
        console.print("[green]✓[/green] O app já está rodando.")
        if not webbrowser.open(APP_URL):
            console.print(f"Acesse [bold]{APP_URL}[/bold] no navegador.")
        return

    ambiente = _ambiente_servidor()
    if not _aplicar_migracoes(console, ambiente):
        return

    console.print(
        f"Subindo front + API em [bold]{APP_URL}[/bold]. O navegador abrirá automaticamente."
    )
    _agendar_abertura_navegador(console)
    try:
        codigo = subprocess.call(
            [sys.executable, str(MANAGE_PY), "runserver", APP_ENDERECO_PADRAO],
            cwd=SERVIDOR,
            env=ambiente,
        )
        if codigo != 0:
            console.print(
                f"[red]✗[/red] O servidor terminou com código {codigo}. "
                f"Verifique se {APP_ENDERECO_PADRAO} já está sendo usado."
            )
    except KeyboardInterrupt:
        console.print("\n[dim]Aplicação encerrada.[/dim]")


def acao_servidor(console) -> None:
    """Subir servidor: aplica as migrações e sobe o servidor Django local."""

    import questionary

    console.rule("[bold]Subir servidor")

    if not _django_disponivel():
        console.print("[yellow]•[/yellow] O Django (extra de servidor) não está instalado.")
        if questionary.confirm("Instalar os extras de servidor agora?").ask():
            if not _instalar_extra_servidor(console):
                return
        else:
            console.print(
                "[dim]Sem o Django o servidor não sobe. Instale quando quiser:\n"
                f'  {sys.executable} -m pip install -e ".[server]"[/dim]'
            )
            return

    configurado, origem = _token_configurado()
    if not configurado:
        console.print(
            f"[yellow]•[/yellow] Token {origem}. O servidor sobe, mas as rotas que falam "
            "com o Notion vão falhar até o token ser configurado em [bold]Configurar[/bold]."
        )

    endereco = questionary.text(
        "Endereço do servidor (host:porta):", default="127.0.0.1:8000"
    ).ask()
    if not endereco:
        console.print("[dim]Cancelado.[/dim]")
        return
    endereco = endereco.strip()

    ambiente = _ambiente_servidor()
    if not _aplicar_migracoes(console, ambiente):
        return

    console.print(
        f"Subindo o servidor em [bold]http://{endereco}/[/bold] — health em "
        "[bold]/api/health[/bold]. Pressione [bold]Ctrl+C[/bold] para encerrar este servidor."
    )
    try:
        subprocess.call(
            [sys.executable, str(MANAGE_PY), "runserver", endereco], cwd=SERVIDOR, env=ambiente
        )
    except KeyboardInterrupt:
        console.print("\n[dim]Servidor encerrado.[/dim]")


def acao_mcp(console) -> None:
    """Subir o servidor MCP para o Felixo-AI-Core."""

    import questionary

    console.rule("[bold]Subir servidor MCP")

    if not _mcp_disponivel():
        console.print("[yellow]•[/yellow] O SDK MCP não está instalado.")
        if questionary.confirm("Instalar os extras de MCP agora?").ask():
            codigo = subprocess.call(
                [sys.executable, "-m", "pip", "install", "-e", ".[mcp]"], cwd=RAIZ
            )
            if codigo != 0 or not _mcp_disponivel():
                console.print(
                    "[red]✗[/red] Não consegui instalar o MCP. Instale manualmente:\n"
                    f'  {sys.executable} -m pip install -e ".[mcp]"'
                )
                return
        else:
            console.print(
                "[dim]Sem o SDK MCP o servidor não sobe. Instale quando quiser:\n"
                f'  {sys.executable} -m pip install -e ".[mcp]"[/dim]'
            )
            return

    configurado, origem = _token_configurado()
    if not configurado:
        console.print(
            f"[yellow]•[/yellow] Token {origem}. As ferramentas MCP que falam "
            "com o Notion vão falhar até o token ser configurado em [bold]Configurar[/bold]."
        )

    database_id = os.environ.get(DATABASE_ENV, "").strip() or _ler_valor_env_file(DATABASE_ENV)
    if not database_id:
        console.print(
            f"[yellow]•[/yellow] {DATABASE_ENV} não configurado. As ferramentas MCP "
            "vão falhar até o database de tarefas ser definido no ambiente ou no .env."
        )

    modo = questionary.select(
        "Modo de transporte:",
        choices=[
            questionary.Choice(
                "stdio (padrão — o Felixo-AI-Core spawna assim)",
                value="stdio",
            ),
            questionary.Choice(
                "Streamable HTTP (debug local — endpoint /mcp)",
                value="streamable-http",
            ),
        ],
    ).ask()
    if not modo:
        console.print("[dim]Cancelado.[/dim]")
        return

    mcp_script = SERVIDOR / "mcp_server.py"
    ambiente = dict(os.environ)
    token_arquivo = _ler_token_env_file()
    if token_arquivo and not ambiente.get(TOKEN_ENV):
        ambiente[TOKEN_ENV] = token_arquivo

    args = [sys.executable, str(mcp_script)]
    if modo == "streamable-http":
        args.extend(["--transport", "streamable-http"])
        console.print(
            "Subindo servidor MCP em [bold]http://127.0.0.1:8000/mcp[/bold] — "
            "Pressione [bold]Ctrl+C[/bold] para encerrar este servidor."
        )
    else:
        console.print(
            "Subindo servidor MCP em modo stdio — "
            "Pressione [bold]Ctrl+C[/bold] para encerrar este servidor."
        )

    try:
        subprocess.call(args, cwd=SERVIDOR, env=ambiente)
    except KeyboardInterrupt:
        console.print("\n[dim]Servidor MCP encerrado.[/dim]")


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
    tabela.add_row("Python", f"[green]{py}[/green]" if py_ok else f"[red]{py} (requer 3.10+)[/red]")

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


def _acoes_menu():
    """Retorna as ações disponíveis e seus rótulos públicos."""

    return {
        "tudo": (
            "🚀  Iniciar tudo — abre front + API no navegador",
            acao_iniciar_tudo,
        ),
        "rodar": ("▶  Iniciar / Rodar — executa um exemplo da biblioteca", acao_rodar),
        "servidor": ("🌐  Subir servidor — sobe a API web (Django) local", acao_servidor),
        "mcp": ("🔗  Subir servidor MCP — ponte para o Felixo-AI-Core", acao_mcp),
        "mapear": ("🗺  Mapear workspace — gera mapa.json e mapa.html navegável", acao_mapear),
        "instalar": ("⬇  Instalar / Setup — instala deps e cria o .env", acao_instalar),
        "configurar": ("⚙  Configurar — aponta o token do Notion", acao_configurar),
        "status": ("ℹ  Status — mostra o estado real do ambiente", acao_status),
    }


def _executar_acao_dedicada(chave: str) -> None:
    """Executa uma ação no processo filho e mantém o terminal legível ao final."""

    from rich.console import Console

    acoes = _acoes_menu()
    console = Console()
    texto, acao = acoes[chave]
    console.print(f"[bold cyan]{texto}[/bold cyan]\n")

    try:
        acao(console)
    except KeyboardInterrupt:
        console.print("\n[dim]Ação interrompida.[/dim]")
    except Exception as exc:  # noqa: BLE001 - mostra erro amigável no terminal dedicado
        console.print(f"\n[red]Erro:[/red] {exc}")
    finally:
        if sys.stdin.isatty():
            try:
                input("\nPressione Enter para fechar este terminal...")
            except (EOFError, KeyboardInterrupt):
                pass


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

    acoes = _acoes_menu()

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

        abriu, mensagem = _abrir_terminal_dedicado(escolha, acoes[escolha][0])
        estilo = "green" if abriu else "red"
        simbolo = "✓" if abriu else "✗"
        console.print(f"[{estilo}]{simbolo}[/{estilo}] {mensagem}")
        if abriu:
            console.print("[dim]O menu continua disponível para iniciar outras ações.[/dim]")

        console.print()


def main(argv: list[str] | None = None) -> None:
    """Ponto de entrada: garante a TUI e abre o menu (ou um fallback claro)."""

    argumentos = sys.argv[1:] if argv is None else argv
    acao_solicitada: str | None = None
    if argumentos:
        if len(argumentos) != 2 or argumentos[0] != "--action":
            opcoes = ", ".join(_acoes_menu())
            raise SystemExit(f"Uso: {Path(__file__).name} [--action {{{opcoes}}}]")
        acao_solicitada = argumentos[1]
        if acao_solicitada not in _acoes_menu():
            opcoes = ", ".join(_acoes_menu())
            raise SystemExit(f"Ação desconhecida: {acao_solicitada}. Opções: {opcoes}")

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

    if acao_solicitada:
        _executar_acao_dedicada(acao_solicitada)
        return

    try:
        _menu_loop()
    except KeyboardInterrupt:
        print("\nAté mais!")


if __name__ == "__main__":
    main()
