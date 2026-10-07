"""Testes do mover: planejamento e aplicação dos movimentos com `git mv` e `git rm`."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest
from scripts.migracao import mover_para_camadas
from scripts.migracao.mapa_modulos import CLI, STARTER, Movimento

pytestmark = pytest.mark.skipif(shutil.which("git") is None, reason="precisa do git")

NOVO = "src/felixo_notion_mcp"
PASTA_STARTER = f"_importado/{STARTER}"
PASTA_CLI = f"_importado/{CLI}"


def _git(raiz: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@t", *args],
        cwd=raiz,
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def _repo(raiz: Path, arquivos: dict[str, str]) -> Path:
    """Cria um repositório de teste com os arquivos já commitados."""
    _git(raiz, "init", "-q")
    for caminho, conteudo in arquivos.items():
        destino = raiz / caminho
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(conteudo, encoding="utf-8")
    _git(raiz, "add", "-A")
    _git(raiz, "commit", "-q", "-m", "inicial")
    return raiz


def _tabela() -> tuple[Movimento, ...]:
    return (
        Movimento(
            f"{PASTA_STARTER}/src/notion_starter/__init__.py", f"{NOVO}/__init__.py", STARTER
        ),
        Movimento(
            f"{PASTA_STARTER}/src/notion_starter/client.py",
            f"{NOVO}/integrations/notion_client.py",
            STARTER,
        ),
        Movimento(f"{PASTA_STARTER}/src/notion_starter/utils.py", f"{NOVO}/core/utils.py", STARTER),
        Movimento(f"{PASTA_STARTER}/examples", "examples", STARTER),
        Movimento(f"{PASTA_STARTER}/LICENSE", "", STARTER),
        Movimento(f"{PASTA_STARTER}/.github", "", STARTER),
        Movimento(f"{PASTA_CLI}/core/utils.py", f"{NOVO}/core/utils.py", CLI, apenas_mapear=True),
        Movimento(f"{PASTA_CLI}/core/__init__.py", f"{NOVO}/core/__init__.py", CLI, True),
        Movimento(f"{PASTA_CLI}/scripts/build.py", "scripts/empacotamento/build.py", CLI),
    )


ARQUIVOS = {
    f"{PASTA_STARTER}/src/notion_starter/__init__.py": "# pacote\n",
    f"{PASTA_STARTER}/src/notion_starter/client.py": "cliente\n",
    f"{PASTA_STARTER}/src/notion_starter/utils.py": "utils\n",
    f"{PASTA_STARTER}/examples/a.py": "exemplo\n",
    f"{PASTA_STARTER}/LICENSE": "mit\n",
    f"{PASTA_STARTER}/.github/workflows/ci.yml": "ci\n",
    f"{PASTA_CLI}/core/utils.py": "utils da cli\n",
    f"{PASTA_CLI}/core/__init__.py": '"""core"""\n',
    f"{PASTA_CLI}/scripts/build.py": "build\n",
    f"{NOVO}/__init__.py": "",
    "scripts/__init__.py": "",
}


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    return _repo(tmp_path, ARQUIVOS)


def _tipos(plano: mover_para_camadas.Plano) -> list[str]:
    return [acao.tipo for acao in plano.acoes]


def test_simular_nao_altera_nada(repo, capsys):
    antes = _git(repo, "status", "--porcelain")
    codigo = mover_para_camadas.main(
        ["--modulo", STARTER, "--simular"], raiz=repo, movimentos=_tabela()
    )
    assert codigo == 0
    assert _git(repo, "status", "--porcelain") == antes == ""
    saida = capsys.readouterr().out
    assert "notion_client.py" in saida and "simulação" in saida


def test_planejar_classifica_cada_movimento(repo):
    plano = mover_para_camadas.planejar(STARTER, repo, _tabela())
    assert plano.erros == []
    por_origem = {acao.origem: acao.tipo for acao in plano.acoes if acao.origem}
    assert por_origem[f"{PASTA_STARTER}/src/notion_starter/__init__.py"] == "substituir"
    assert por_origem[f"{PASTA_STARTER}/src/notion_starter/client.py"] == "mover"
    assert por_origem[f"{PASTA_STARTER}/LICENSE"] == "remover"
    assert por_origem[f"{PASTA_STARTER}/examples"] == "mover"
    criados = [acao.destino for acao in plano.acoes if acao.tipo == "criar_pacote"]
    assert f"{NOVO}/integrations/__init__.py" in criados
    assert f"{NOVO}/core/__init__.py" in criados
    assert f"{NOVO}/__init__.py" not in criados  # já existe


def test_aplicar_move_remove_e_cria_pacotes(repo):
    assert (
        mover_para_camadas.main(["--modulo", STARTER, "--aplicar"], raiz=repo, movimentos=_tabela())
        == 0
    )
    cliente = repo / f"{NOVO}/integrations/notion_client.py"
    assert cliente.read_text(encoding="utf-8") == "cliente\n"
    assert (repo / f"{NOVO}/core/utils.py").is_file()
    assert (repo / "examples/a.py").is_file()
    assert (repo / f"{NOVO}/__init__.py").read_text(encoding="utf-8") == "# pacote\n"
    assert not (repo / f"{PASTA_STARTER}/LICENSE").exists()
    assert not (repo / f"{PASTA_STARTER}/.github").exists()
    # Pacotes novos criados e já na área de preparo do git.
    assert (repo / f"{NOVO}/integrations/__init__.py").is_file()
    assert (repo / f"{NOVO}/core/__init__.py").is_file()
    preparados = _git(repo, "diff", "--cached", "--name-only")
    assert f"{NOVO}/integrations/__init__.py" in preparados
    # O módulo inteiro foi esvaziado: a pasta vazia não fica para trás.
    assert not (repo / PASTA_STARTER).exists()


def test_aplicar_preserva_o_historico_com_git_mv(repo):
    mover_para_camadas.main(["--modulo", STARTER, "--aplicar"], raiz=repo, movimentos=_tabela())
    renomeados = _git(repo, "diff", "--cached", "--name-status", "-M")
    esperado = (
        f"R100\t{PASTA_STARTER}/src/notion_starter/client.py\t{NOVO}/integrations/notion_client.py"
    )
    assert esperado in renomeados


def test_aplicar_e_idempotente(repo):
    argv = ["--modulo", STARTER, "--aplicar"]
    mover_para_camadas.main(argv, raiz=repo, movimentos=_tabela())
    estado = _git(repo, "status", "--porcelain")
    plano = mover_para_camadas.planejar(STARTER, repo, _tabela())
    assert set(_tipos(plano)) == {"pular"}
    assert mover_para_camadas.main(argv, raiz=repo, movimentos=_tabela()) == 0
    assert _git(repo, "status", "--porcelain") == estado


def test_apenas_mapear_remove_a_origem_e_exige_o_destino_real(repo):
    mover_para_camadas.main(["--modulo", STARTER, "--aplicar"], raiz=repo, movimentos=_tabela())
    codigo = mover_para_camadas.main(
        ["--modulo", CLI, "--aplicar"], raiz=repo, movimentos=_tabela()
    )
    assert codigo == 0
    assert not (repo / PASTA_CLI / "core/utils.py").exists()
    assert not (repo / PASTA_CLI / "core/__init__.py").exists()
    assert (repo / "scripts/empacotamento/build.py").read_text(encoding="utf-8") == "build\n"
    assert (repo / "scripts/empacotamento/__init__.py").is_file()
    # O arquivo real não foi tocado pela remoção do shim.
    assert (repo / f"{NOVO}/core/utils.py").read_text(encoding="utf-8") == "utils\n"


def test_apenas_mapear_sem_o_destino_falha_com_mensagem_clara_e_nao_altera_nada(repo, capsys):
    antes = _git(repo, "status", "--porcelain")
    codigo = mover_para_camadas.main(
        ["--modulo", CLI, "--aplicar"], raiz=repo, movimentos=_tabela()
    )
    assert codigo == 1
    assert _git(repo, "status", "--porcelain") == antes
    erro = capsys.readouterr().err
    assert "core/utils.py" in erro and "ainda não existe" in erro


def test_simular_do_apenas_mapear_aceita_destino_que_outro_modulo_vai_criar(repo):
    plano = mover_para_camadas.planejar(CLI, repo, _tabela())
    assert plano.erros == []
    shim = next(a for a in plano.acoes if a.origem.endswith("core/utils.py"))
    assert shim.tipo == "mapear_e_remover"


def test_apenas_mapear_com_destino_que_ninguem_cria_e_erro_ate_na_simulacao(repo):
    tabela = (Movimento(f"{PASTA_CLI}/core/utils.py", f"{NOVO}/core/fantasma.py", CLI, True),)
    plano = mover_para_camadas.planejar(CLI, repo, tabela)
    assert len(plano.erros) == 1 and "fantasma.py" in plano.erros[0]


def test_destino_existente_com_conteudo_e_conflito_e_nada_e_aplicado(repo, capsys):
    (repo / f"{NOVO}/core").mkdir(parents=True)
    (repo / f"{NOVO}/core/utils.py").write_text("outro\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "conflito")
    codigo = mover_para_camadas.main(
        ["--modulo", STARTER, "--aplicar"], raiz=repo, movimentos=_tabela()
    )
    assert codigo == 1
    assert (repo / PASTA_STARTER / "src/notion_starter/client.py").is_file()  # nada foi movido
    assert "já existe" in capsys.readouterr().err


def test_origem_e_destino_ausentes_e_erro(repo):
    tabela = (Movimento(f"{PASTA_STARTER}/nao_existe.py", f"{NOVO}/x.py", STARTER),)
    plano = mover_para_camadas.planejar(STARTER, repo, tabela)
    assert len(plano.erros) == 1 and "nao_existe.py" in plano.erros[0]


def test_origem_removida_que_nao_existe_mais_e_so_pulada(repo):
    tabela = (Movimento(f"{PASTA_STARTER}/ja_removido.md", "", STARTER),)
    plano = mover_para_camadas.planejar(STARTER, repo, tabela)
    assert plano.erros == [] and _tipos(plano) == ["pular"]


def test_modulo_invalido_e_rejeitado(repo):
    with pytest.raises(SystemExit):
        mover_para_camadas.main(["--modulo", "outro", "--simular"], raiz=repo)


def test_exige_simular_ou_aplicar(repo):
    with pytest.raises(SystemExit):
        mover_para_camadas.main(["--modulo", STARTER], raiz=repo)
