"""Confere se o wheel carrega os arquivos de dados que o pacote precisa em tempo de execução.

O `hatchling` empacota os módulos Python sozinho, mas migrações, templates, estáticos e o
bundle da SPA são dados: se saírem do wheel, o pacote instala sem erro e quebra só quando o
app sobe. Esta conferência roda no CI depois do `uv build` e também à mão.

Duas camadas de conferência:

1. `ARQUIVOS_OBRIGATORIOS`: os arquivos de dados que o código carrega por nome fixo;
2. os assets da SPA: o nome de cada `assets/index-<hash>.js|css` muda a cada build, então a
   lista vem do próprio `index.html` de dentro do wheel. Um wheel que leva o `index.html`
   sem os assets passaria na camada 1 e serviria uma página em branco.

Uso: `python -m scripts.empacotamento.conferir_wheel dist/*.whl`
"""

from __future__ import annotations

import argparse
import glob
import sys
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

PASTA_DA_SPA = "felixo_notion_mcp/api/http/static/frontend/"
INDEX_DA_SPA = PASTA_DA_SPA + "index.html"
# O Vite (`base` em `front/vite.config.js`) grava as referências do index.html com este prefixo.
PREFIXO_URL_DA_SPA = "/static/frontend/"

ARQUIVOS_OBRIGATORIOS: tuple[str, ...] = (
    "felixo_notion_mcp/repositories/operations/migrations/0001_initial.py",
    "felixo_notion_mcp/api/http/templates/tarefas.html",
    INDEX_DA_SPA,
    "felixo_notion_mcp/api/http/static/css/app.css",
    "felixo_notion_mcp/api/http/static/js/app.js",
)


class _ReferenciasDaSpa(HTMLParser):
    """Coleta, na ordem em que aparecem, os `src`/`href` locais que apontam para a SPA."""

    def __init__(self) -> None:
        super().__init__()
        self.arquivos: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for nome, valor in attrs:
            if nome not in ("src", "href") or not valor:
                continue
            partes = urlsplit(valor)
            if partes.scheme or partes.netloc:
                continue  # URL externa ou `data:`: não é arquivo do wheel
            if not partes.path.startswith(PREFIXO_URL_DA_SPA):
                continue
            nome_no_wheel = PASTA_DA_SPA + unquote(partes.path[len(PREFIXO_URL_DA_SPA) :])
            if nome_no_wheel not in self.arquivos:
                self.arquivos.append(nome_no_wheel)


def _assets_referenciados(html: str) -> list[str]:
    """Nomes dentro do wheel dos arquivos que o `index.html` carrega, sem repetição."""

    analisador = _ReferenciasDaSpa()
    analisador.feed(html)
    analisador.close()
    return analisador.arquivos


def assets_da_spa(caminho_wheel: Path) -> list[str]:
    """Assets que o `index.html` do wheel referencia; vazio quando não há `index.html`."""

    with zipfile.ZipFile(caminho_wheel) as wheel:
        if INDEX_DA_SPA not in wheel.namelist():
            return []
        html = wheel.read(INDEX_DA_SPA).decode("utf-8", errors="replace")
    return _assets_referenciados(html)


def faltando_no_wheel(caminho_wheel: Path) -> list[str]:
    """Lista o que não está dentro do wheel.

    Primeiro os `ARQUIVOS_OBRIGATORIOS` na ordem da constante, depois os assets que o
    `index.html` referencia na ordem em que ele os cita.
    """

    with zipfile.ZipFile(caminho_wheel) as wheel:
        presentes = set(wheel.namelist())
    faltando = [nome for nome in ARQUIVOS_OBRIGATORIOS if nome not in presentes]
    faltando += [nome for nome in assets_da_spa(caminho_wheel) if nome not in presentes]
    return faltando


def _expandir(padrao: str) -> list[Path]:
    """Expande `*` e `?` quando o shell não o fez (o `cmd` e o PowerShell não expandem)."""

    if Path(padrao).exists():
        return [Path(padrao)]
    return [Path(achado) for achado in sorted(glob.glob(padrao))]


def main(argv: list[str] | None = None) -> int:
    """Confere cada wheel informado; sai com 1 e lista o que falta se algum estiver incompleto."""

    parser = argparse.ArgumentParser(
        description="Confere se o wheel contém os arquivos de dados obrigatórios."
    )
    parser.add_argument("wheels", nargs="+", help="caminho(s) do wheel, aceita curingas")
    args = parser.parse_args(argv)

    caminhos = [caminho for padrao in args.wheels for caminho in _expandir(padrao)]
    if not caminhos:
        print(f"Nenhum wheel encontrado em: {' '.join(args.wheels)}", file=sys.stderr)
        return 1

    incompleto = False
    for caminho in caminhos:
        faltando = faltando_no_wheel(caminho)
        if faltando:
            incompleto = True
            print(f"{caminho.name}: faltam {len(faltando)} arquivo(s) de dados:", file=sys.stderr)
            for nome in faltando:
                print(f"  - {nome}", file=sys.stderr)
        else:
            print(
                f"{caminho.name}: ok ({len(ARQUIVOS_OBRIGATORIOS)} arquivos de dados e "
                f"{len(assets_da_spa(caminho))} assets da SPA presentes)"
            )
    return 1 if incompleto else 0


if __name__ == "__main__":
    raise SystemExit(main())
