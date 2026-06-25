"""Testes do despacho de ações do menu em terminais dedicados."""

from __future__ import annotations

import importlib.util
import io
from pathlib import Path

from rich.console import Console

_START_APP = Path(__file__).resolve().parents[1] / "start_app.py"
_SPEC = importlib.util.spec_from_file_location("start_app", _START_APP)
assert _SPEC and _SPEC.loader
start_app = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(start_app)


def test_comando_acao_reabre_start_app_com_acao():
    comando = start_app._comando_acao("servidor")

    assert comando[0] == start_app.sys.executable
    assert comando[1] == str(start_app.Path(start_app.__file__).resolve())
    assert comando[2:] == ["--action", "servidor"]


def test_terminal_linux_prefere_terminal_configurado(monkeypatch):
    monkeypatch.setenv("TERMINAL", "terminal-personalizado --nova-janela")
    monkeypatch.setattr(
        start_app.shutil,
        "which",
        lambda nome: f"/usr/bin/{nome}" if nome == "terminal-personalizado" else None,
    )

    comando = start_app._comando_terminal_linux(["python", "app.py"], "Minha ação")

    assert comando == [
        "/usr/bin/terminal-personalizado",
        "--nova-janela",
        "-e",
        "python",
        "app.py",
    ]


def test_terminal_linux_faz_fallback_para_konsole(monkeypatch):
    monkeypatch.delenv("TERMINAL", raising=False)
    monkeypatch.setattr(
        start_app.shutil,
        "which",
        lambda nome: "/usr/bin/konsole" if nome == "konsole" else None,
    )

    comando = start_app._comando_terminal_linux(["python", "app.py"], "Status")

    assert comando == [
        "/usr/bin/konsole",
        "--separate",
        "-p",
        "tabtitle=Status",
        "-e",
        "python",
        "app.py",
    ]


def test_abrir_terminal_linux_inicia_processo_independente(monkeypatch):
    chamadas = []
    monkeypatch.setattr(start_app.sys, "platform", "linux")
    monkeypatch.setattr(
        start_app,
        "_comando_terminal_linux",
        lambda comando, titulo: ["terminal", "--", *comando],
    )
    monkeypatch.setattr(
        start_app.subprocess,
        "Popen",
        lambda comando, **kwargs: chamadas.append((comando, kwargs)),
    )

    abriu, mensagem = start_app._abrir_terminal_dedicado("status", "Status")

    assert abriu is True
    assert "Status" in mensagem
    comando, kwargs = chamadas[0]
    assert comando[:2] == ["terminal", "--"]
    assert comando[-2:] == ["--action", "status"]
    assert kwargs["cwd"] == start_app.RAIZ
    assert kwargs["start_new_session"] is True


def test_abrir_terminal_informa_quando_nao_ha_emulador(monkeypatch):
    monkeypatch.setattr(start_app.sys, "platform", "linux")
    monkeypatch.setattr(start_app, "_comando_terminal_linux", lambda comando, titulo: None)
    monkeypatch.setattr(
        start_app.subprocess,
        "Popen",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("não deve abrir processo")),
    )

    abriu, mensagem = start_app._abrir_terminal_dedicado("status", "Status")

    assert abriu is False
    assert "Nenhum emulador de terminal" in mensagem


def test_abrir_terminal_windows_usa_novo_console(monkeypatch):
    chamadas = []
    monkeypatch.setattr(start_app.sys, "platform", "win32")
    monkeypatch.setattr(start_app.subprocess, "CREATE_NEW_CONSOLE", 1234, raising=False)
    monkeypatch.setattr(
        start_app.subprocess,
        "Popen",
        lambda comando, **kwargs: chamadas.append((comando, kwargs)),
    )

    abriu, _ = start_app._abrir_terminal_dedicado("configurar", "Configurar")

    assert abriu is True
    _, kwargs = chamadas[0]
    assert kwargs["creationflags"] == 1234
    assert "start_new_session" not in kwargs


def test_abrir_terminal_trata_falha_do_sistema(monkeypatch):
    monkeypatch.setattr(start_app.sys, "platform", "win32")

    def falhar(*args, **kwargs):
        raise OSError("terminal indisponível")

    monkeypatch.setattr(start_app.subprocess, "Popen", falhar)

    abriu, mensagem = start_app._abrir_terminal_dedicado("status", "Status")

    assert abriu is False
    assert "terminal indisponível" in mensagem


def test_menu_oferece_iniciar_tudo_como_primeira_opcao():
    acoes = start_app._acoes_menu()

    assert next(iter(acoes)) == "tudo"
    assert acoes["tudo"][1] is start_app.acao_iniciar_tudo


def test_instala_extra_servidor_quando_necessario(monkeypatch):
    chamadas = []
    monkeypatch.setattr(start_app, "_django_disponivel", lambda: True)
    monkeypatch.setattr(
        start_app.subprocess,
        "call",
        lambda comando, **kwargs: chamadas.append((comando, kwargs)) or 0,
    )
    console = Console(file=io.StringIO(), force_terminal=False)

    assert start_app._instalar_extra_servidor(console) is True
    comando, kwargs = chamadas[0]
    assert comando[-3:] == ["install", "-e", ".[server]"]
    assert kwargs["cwd"] == start_app.RAIZ


def test_app_web_ativo_valida_health_do_projeto(monkeypatch):
    class Resposta:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def read(self):
            return b'{"status": "ok", "service": "automacoes-notion"}'

    monkeypatch.setattr(start_app.urllib.request, "urlopen", lambda *args, **kwargs: Resposta())

    assert start_app._app_web_ativo() is True


def test_abre_navegador_assim_que_health_responde(monkeypatch):
    estados = iter((False, True))
    aberturas = []
    monkeypatch.setattr(start_app, "_app_web_ativo", lambda: next(estados))
    monkeypatch.setattr(start_app.time, "sleep", lambda intervalo: None)
    monkeypatch.setattr(
        start_app.webbrowser,
        "open",
        lambda url: aberturas.append(url) or True,
    )
    console = Console(file=io.StringIO(), force_terminal=False)

    start_app._abrir_navegador_quando_pronto(console, tentativas=2, intervalo=0)

    assert aberturas == [start_app.APP_URL]


def test_iniciar_tudo_usa_defaults_e_sobe_front_api(monkeypatch):
    chamadas = []
    agendamentos = []
    monkeypatch.setattr(start_app, "_django_disponivel", lambda: True)
    monkeypatch.setattr(start_app, "_token_configurado", lambda: (True, ".env local"))
    monkeypatch.setattr(start_app, "_app_web_ativo", lambda: False)
    monkeypatch.setattr(start_app, "_ambiente_servidor", lambda: {"DJANGO_DEBUG": "1"})
    monkeypatch.setattr(start_app, "_aplicar_migracoes", lambda console, ambiente: True)
    monkeypatch.setattr(
        start_app,
        "_agendar_abertura_navegador",
        lambda console: agendamentos.append(True),
    )
    monkeypatch.setattr(
        start_app.subprocess,
        "call",
        lambda comando, **kwargs: chamadas.append((comando, kwargs)) or 0,
    )
    console = Console(file=io.StringIO(), force_terminal=False)

    start_app.acao_iniciar_tudo(console)

    assert agendamentos == [True]
    comando, kwargs = chamadas[0]
    assert comando[-2:] == ["runserver", start_app.APP_ENDERECO_PADRAO]
    assert kwargs["cwd"] == start_app.SERVIDOR
    assert kwargs["env"] == {"DJANGO_DEBUG": "1"}


def test_iniciar_tudo_reabre_app_que_ja_esta_rodando(monkeypatch):
    aberturas = []
    monkeypatch.setattr(start_app, "_django_disponivel", lambda: True)
    monkeypatch.setattr(start_app, "_token_configurado", lambda: (True, ".env local"))
    monkeypatch.setattr(start_app, "_app_web_ativo", lambda: True)
    monkeypatch.setattr(
        start_app.webbrowser,
        "open",
        lambda url: aberturas.append(url) or True,
    )
    monkeypatch.setattr(
        start_app.subprocess,
        "call",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("não deve iniciar outro servidor")
        ),
    )
    console = Console(file=io.StringIO(), force_terminal=False)

    start_app.acao_iniciar_tudo(console)

    assert aberturas == [start_app.APP_URL]


def test_main_rejeita_acao_desconhecida():
    try:
        start_app.main(["--action", "inexistente"])
    except SystemExit as exc:
        assert "Ação desconhecida" in str(exc)
    else:
        raise AssertionError("main deveria rejeitar uma ação inexistente")
