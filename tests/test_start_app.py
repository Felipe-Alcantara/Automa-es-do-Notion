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


def test_database_compativel_exige_schema_completo():
    database = {
        "properties": {
            "Nome": {"type": "title"},
            "Status": {"type": "status"},
            "Próximo prazo": {"type": "date"},
        }
    }

    assert start_app._database_compativel(database) is True
    del database["properties"]["Próximo prazo"]
    assert start_app._database_compativel(database) is False


def test_garantir_database_sempre_pergunta_ao_subir(monkeypatch, tmp_path):
    # Mesmo com um database já salvo, "Iniciar tudo" pergunta (com o atual
    # pré-selecionado) — ele NÃO reusa em silêncio.
    import questionary

    capturado = {}

    class Pergunta:
        def ask(self):
            return "db-trocado"

    def fake_select(mensagem, choices, *args, **kwargs):
        capturado["default"] = kwargs.get("default")
        return Pergunta()

    env_file = tmp_path / ".env"
    env_file.write_text("NOTION_TOKEN=ntn_teste\nNOTION_DATABASE_ID=db-atual\n", encoding="utf-8")
    monkeypatch.setattr(start_app, "ENV_FILE", env_file)
    monkeypatch.setenv(start_app.DATABASE_ENV, "db-atual")
    monkeypatch.delenv(start_app.TOKEN_ENV, raising=False)
    monkeypatch.setattr(
        start_app,
        "_buscar_databases_compativeis",
        lambda token: [("Atual", "db-atual"), ("Outro", "db-trocado")],
    )
    monkeypatch.setattr(questionary, "select", fake_select)
    console = Console(file=io.StringIO(), force_terminal=False)

    assert start_app._garantir_database_tarefas(console) is True
    # O atual entra pré-selecionado e a troca é gravada.
    assert capturado["default"] == "db-atual"
    assert start_app.os.environ[start_app.DATABASE_ENV] == "db-trocado"


def test_garantir_database_cancelar_mantem_o_atual_e_sobe(monkeypatch, tmp_path):
    # Ao subir, cancelar a escolha mantém o database já salvo e segue (True).
    import questionary

    class Pergunta:
        def ask(self):
            return None  # usuário escolheu "Manter o atual"

    env_file = tmp_path / ".env"
    env_file.write_text("NOTION_TOKEN=ntn_teste\nNOTION_DATABASE_ID=db-atual\n", encoding="utf-8")
    monkeypatch.setattr(start_app, "ENV_FILE", env_file)
    monkeypatch.setenv(start_app.DATABASE_ENV, "db-atual")
    monkeypatch.delenv(start_app.TOKEN_ENV, raising=False)
    monkeypatch.setattr(
        start_app,
        "_buscar_databases_compativeis",
        lambda token: [("Atual", "db-atual"), ("Outro", "db-outro")],
    )
    monkeypatch.setattr(questionary, "select", lambda *args, **kwargs: Pergunta())
    console = Console(file=io.StringIO(), force_terminal=False)

    assert start_app._garantir_database_tarefas(console) is True
    assert start_app.os.environ[start_app.DATABASE_ENV] == "db-atual"


def test_garantir_database_pergunta_e_salva_na_primeira_vez(monkeypatch, tmp_path):
    # Sem database salvo, "Iniciar tudo" pergunta (mesmo com um único
    # compatível) e grava a escolha no .env.
    import questionary

    class Pergunta:
        def ask(self):
            return "database-selecionado"

    env_file = tmp_path / ".env"
    env_file.write_text("NOTION_TOKEN=ntn_teste\n", encoding="utf-8")
    monkeypatch.setattr(start_app, "ENV_FILE", env_file)
    # setenv (em vez de delenv) faz o monkeypatch "adotar" a chave: a escrita
    # que a produção faz em os.environ é revertida no teardown, sem vazar para
    # outros testes (ex.: test_api_tarefas, que lê NOTION_DATABASE_ID).
    monkeypatch.setenv(start_app.DATABASE_ENV, "")
    monkeypatch.delenv(start_app.DATABASE_ENV, raising=False)
    monkeypatch.delenv(start_app.TOKEN_ENV, raising=False)
    monkeypatch.setattr(
        start_app,
        "_buscar_databases_compativeis",
        lambda token: [("Tarefas", "database-selecionado")],
    )
    monkeypatch.setattr(questionary, "select", lambda *args, **kwargs: Pergunta())
    console = Console(file=io.StringIO(), force_terminal=False)

    assert start_app._garantir_database_tarefas(console) is True
    assert "NOTION_DATABASE_ID=database-selecionado" in env_file.read_text()
    assert start_app.os.environ[start_app.DATABASE_ENV] == "database-selecionado"


def test_garantir_database_pede_escolha_quando_ha_mais_de_um(monkeypatch, tmp_path):
    import questionary

    class Pergunta:
        def ask(self):
            return "db-2"

    env_file = tmp_path / ".env"
    env_file.write_text("NOTION_TOKEN=ntn_teste\n", encoding="utf-8")
    monkeypatch.setattr(start_app, "ENV_FILE", env_file)
    # setenv adota a chave para que a escrita da produção em os.environ seja
    # revertida no teardown (ver test_garantir_database_unico_salva_no_env).
    monkeypatch.setenv(start_app.DATABASE_ENV, "")
    monkeypatch.delenv(start_app.DATABASE_ENV, raising=False)
    monkeypatch.delenv(start_app.TOKEN_ENV, raising=False)
    monkeypatch.setattr(
        start_app,
        "_buscar_databases_compativeis",
        lambda token: [("Tarefas", "db-1"), ("Tarefas (1)", "db-2")],
    )
    monkeypatch.setattr(questionary, "select", lambda *args, **kwargs: Pergunta())
    console = Console(file=io.StringIO(), force_terminal=False)

    assert start_app._garantir_database_tarefas(console) is True
    assert start_app.os.environ[start_app.DATABASE_ENV] == "db-2"


def test_garantir_database_falha_sem_compativel(monkeypatch, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("NOTION_TOKEN=ntn_teste\n", encoding="utf-8")
    monkeypatch.setattr(start_app, "ENV_FILE", env_file)
    monkeypatch.delenv(start_app.DATABASE_ENV, raising=False)
    monkeypatch.delenv(start_app.TOKEN_ENV, raising=False)
    monkeypatch.setattr(start_app, "_buscar_databases_compativeis", lambda token: [])
    saida = io.StringIO()
    console = Console(file=saida, force_terminal=False)

    assert start_app._garantir_database_tarefas(console) is False
    assert "Nenhum database compatível" in saida.getvalue()


def test_selecionar_database_pergunta_para_trocar_o_atual(monkeypatch, tmp_path):
    # Mesmo com um único database compatível, se já houver um selecionado a
    # opção "Configurar → Escolher database" deve perguntar (para poder trocar),
    # não reusar em silêncio. Marca o atual na lista de escolhas.
    import questionary

    capturado = {}

    class Pergunta:
        def ask(self):
            return "db-novo"

    def fake_select(mensagem, choices, *args, **kwargs):
        capturado["choices"] = choices
        return Pergunta()

    env_file = tmp_path / ".env"
    env_file.write_text("NOTION_TOKEN=ntn_teste\nNOTION_DATABASE_ID=db-antigo\n", encoding="utf-8")
    monkeypatch.setattr(start_app, "ENV_FILE", env_file)
    monkeypatch.setenv(start_app.DATABASE_ENV, "db-antigo")
    monkeypatch.delenv(start_app.TOKEN_ENV, raising=False)
    monkeypatch.setattr(
        start_app,
        "_buscar_databases_compativeis",
        lambda token: [("Tarefas (atual)", "db-antigo"), ("Tarefas nova", "db-novo")],
    )
    monkeypatch.setattr(questionary, "select", fake_select)
    console = Console(file=io.StringIO(), force_terminal=False)

    assert start_app._selecionar_database_tarefas(console) is True
    assert start_app.os.environ[start_app.DATABASE_ENV] == "db-novo"
    assert "NOTION_DATABASE_ID=db-novo" in env_file.read_text()
    # O database atualmente em uso aparece marcado para o usuário se orientar.
    assert any("[atual]" in str(c.title) for c in capturado["choices"])


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
    monkeypatch.setattr(start_app, "_garantir_database_tarefas", lambda console: True)
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
    monkeypatch.setattr(start_app, "_garantir_database_tarefas", lambda console: True)
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
