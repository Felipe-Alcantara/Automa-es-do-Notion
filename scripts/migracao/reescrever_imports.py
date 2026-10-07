"""Reescreve imports e nomes pontuados do código antigo para os nomes do monólito.

Usa o mapa antigo → novo de `mapa_modulos.montar_mapa`. O que reescreve:

1. `import a.b[ as c]` e `from a.b import ...`. Imports relativos só mudam em arquivo que está
   na tabela de movimentos (como destino já movido ou como origem ainda no lugar): o nome
   antigo do arquivo sai da consulta reversa à tabela, o import é resolvido contra o pacote
   antigo e vira absoluto já com o nome novo. Em arquivo fora da tabela, ou quando o nome
   resolvido não está no mapa, o import relativo fica como está;
2. literais de string cujo conteúdo é um nome antigo ou começa com `nome_antigo.` (alvos de
   `monkeypatch.setattr("cli.notion_tasks.main", ...)`, `os.environ[...] = "config.settings"`,
   `import_module("start_app")`), e o código de exemplo dentro de strings e docstrings
   (`python -c "from core import x"`). Não se aplica a migrações do Django, cujas strings são
   rótulos de app, não módulos. Duas guardas evitam trocar o que não é módulo: nome de arquivo
   (`"mcp_server.py"`) e nome comum sozinho (`"config"`, `"api.notion.com"`), que ficam como
   estão e saem na lista de avisos para conferência manual;
3. `from P import x`, quando `P.x` está no mapa: o import só troca o pai (`from <pai novo> import
   x`) se o último nome do destino continua `x`; se o módulo foi renomeado ou se os nomes
   importados juntos vão para pais diferentes, o import fica como está e vira pendência
   (`ImportAmbiguo`) para correção manual.

A leitura é por `tokenize`, então comentários, f-strings e bytes nunca são tocados, e o nome mais
longo do mapa vence (`cli.notion_tasks` antes de `cli`). A reescrita é idempotente. Com pendências,
o resto do arquivo é reescrito e o import ambíguo fica como estava. A própria ferramenta e os
testes dela (`IGNORADOS`) nunca são reescritos, porque citam nomes antigos de propósito.

Uso:
    python -m scripts.migracao.reescrever_imports (--simular | --aplicar) CAMINHO...
"""

from __future__ import annotations

import argparse
import io
import re
import sys
import tokenize
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path

from scripts.migracao.mapa_modulos import (
    RAIZES,
    TABELA_MOVIMENTOS,
    Movimento,
    mapa_da_tabela,
    modulo_antigo_do_arquivo,
)

RAIZ = Path(__file__).resolve().parents[2]

#: Marca de ordem de bytes (U+FEFF) que alguns arquivos antigos trazem no início.
BOM = chr(0xFEFF)

#: Caminhos (relativos à raiz do repositório) que a ferramenta nunca reescreve: ela mesma e os
#: testes dela citam nomes antigos de propósito.
IGNORADOS = ("scripts/migracao", "tests/scripts")

#: Nomes antigos de um só componente que também são palavras comuns (`api.notion.com`,
#: `tmp_path / "config"`, argumentos de linha de comando). Numa string, só são trocados dentro de
#: um nome mais longo que o mapa conhece (`config.settings`); sozinhos, ou seguidos de algo que o
#: mapa não conhece, a string fica como está e entra na lista de avisos para conferência manual.
NOMES_COMUNS = frozenset(
    {"api", "cli", "config", "core", "integrations", "manage", "server", "services"}
)

#: Extensões que denunciam nome de arquivo ou de site, não de módulo (`"mcp_server.py"`).
EXTENSOES_DE_ARQUIVO = frozenset(
    {
        "py", "pyi", "json", "md", "txt", "toml", "html", "css", "js", "jsx", "yml", "yaml",
        "cfg", "ini", "lock", "sh", "png", "svg", "com", "org", "net", "io", "dev", "br",
    }
)  # fmt: skip

#: Pastas que a varredura de diretórios não percorre.
PASTAS_PULADAS = frozenset(
    {"__pycache__", ".git", ".venv", "venv", "node_modules", ".ruff_cache", ".pytest_cache"}
)

_NOME = r"[A-Za-z_]\w*"
_NOME_PONTUADO = rf"{_NOME}(?:\.{_NOME})*"
_PREFIXO_DE_NOME_NA_STRING = re.compile(_NOME_PONTUADO)
# `from X import` / `import X` dentro de uma string que carrega código (`python -c "..."`); o
# `\n` escrito no fonte também separa instruções. O `from X import` é lido por inteiro para que
# o nome importado depois dele não seja tomado por um `import X`.
_CODIGO_EM_STRING = re.compile(
    rf"(?:(?<![\w.])|(?<=\\n))"
    rf"(?:from[ \t]+(?P<de>{_NOME_PONTUADO})[ \t]+import\b|import[ \t]+(?P<nome>{_NOME_PONTUADO}))"
)
_STRING = re.compile(
    r"""^(?P<prefixo>[A-Za-z]{0,3})(?P<aspas>'''|\"\"\"|'|")(?P<conteudo>.*)(?P=aspas)$""",
    re.DOTALL,
)
_NAO_SIGNIFICATIVOS = frozenset(
    {tokenize.NL, tokenize.COMMENT, tokenize.INDENT, tokenize.DEDENT, tokenize.ENCODING}
)


class ImportAmbiguo(Exception):
    """Um `from P import x` que não dá para reescrever sozinho; exige correção manual."""

    def __init__(self, arquivo: str, linha: int, trecho: str, motivo: str = "") -> None:
        self.arquivo = arquivo
        self.linha = linha
        self.trecho = trecho
        self.motivo = motivo
        detalhe = f" ({motivo})" if motivo else ""
        super().__init__(f"{arquivo}:{linha}: import ambíguo{detalhe}: {trecho}")


@dataclass
class _Edicao:
    inicio: int
    fim: int
    novo: str


@dataclass
class _Analise:
    edicoes: list[_Edicao] = field(default_factory=list)
    trocas: list[str] = field(default_factory=list)
    pendencias: list[ImportAmbiguo] = field(default_factory=list)
    avisos: list[str] = field(default_factory=list)


@dataclass
class ResultadoDaAnalise:
    """O que a reescrita de um texto produziu, sem levantar exceção."""

    texto: str
    trocas: list[str]
    pendencias: list[ImportAmbiguo]
    avisos: list[str]


def trocar_prefixo(nome: str, mapa: Mapping[str, str]) -> str:
    """Troca o prefixo mais longo de `nome` presente no mapa; devolve `nome` se não houver."""
    partes = nome.split(".")
    for tamanho in range(len(partes), 0, -1):
        prefixo = ".".join(partes[:tamanho])
        if prefixo in mapa:
            resto = ".".join(partes[tamanho:])
            return mapa[prefixo] + (f".{resto}" if resto else "")
    return nome


def _pai_e_ultimo(nome: str) -> tuple[str, str]:
    pai, _, ultimo = nome.rpartition(".")
    return pai, ultimo


def _significativo(tokens: Sequence[tokenize.TokenInfo], i: int) -> int:
    """Índice do próximo token que importa a partir de `i` (pula NL, comentário e recuo)."""
    while i < len(tokens) and tokens[i].type in _NAO_SIGNIFICATIVOS:
        i += 1
    return i


def _eh_op(token: tokenize.TokenInfo, texto: str) -> bool:
    return token.type == tokenize.OP and token.string == texto


class _Reescritor:
    """Percorre os tokens de um texto e acumula as edições que o mapa pede."""

    def __init__(
        self,
        texto: str,
        mapa: Mapping[str, str],
        *,
        em_migracao_django: bool,
        modulo_antigo: str | None = None,
        eh_pacote_antigo: bool = False,
    ) -> None:
        self.texto = texto
        self.mapa = mapa
        self.em_migracao_django = em_migracao_django
        self.modulo_antigo = modulo_antigo
        self.eh_pacote_antigo = eh_pacote_antigo
        self.resultado = _Analise()
        linhas = io.StringIO(texto).readlines()
        self._inicios = [0]
        for linha in linhas:
            self._inicios.append(self._inicios[-1] + len(linha))
        self.tokens = list(tokenize.generate_tokens(io.StringIO(texto).readline))

    def deslocamento(self, posicao: tuple[int, int]) -> int:
        linha, coluna = posicao
        return self._inicios[linha - 1] + coluna

    # -- nomes pontuados ------------------------------------------------------------------

    def _trocar(
        self, inicio: int, fim: int, antigo: str, novo: str, linha: int, rotulo: str
    ) -> None:
        """Registra a troca do trecho `[inicio, fim)` (que deve valer `antigo`) por `novo`."""
        if self.texto[inicio:fim].replace(" ", "") != antigo:
            raise RuntimeError(
                f"Posição inconsistente na linha {linha}: esperava '{antigo}' em "
                f"{self.texto[inicio:fim]!r}."
            )
        if novo == antigo:
            return
        self.resultado.edicoes.append(_Edicao(inicio, fim, novo))
        self.resultado.trocas.append(f"linha {linha}: {rotulo}{antigo} -> {novo}")

    def _ler_nome_pontuado(self, i: int) -> tuple[list[tokenize.TokenInfo], int] | None:
        """Lê `NOME(.NOME)*` a partir do índice `i`; devolve os tokens e o próximo índice."""
        i = _significativo(self.tokens, i)
        if i >= len(self.tokens) or self.tokens[i].type != tokenize.NAME:
            return None
        lidos = [self.tokens[i]]
        i += 1
        while (
            i + 1 < len(self.tokens)
            and _eh_op(self.tokens[i], ".")
            and self.tokens[i + 1].type == tokenize.NAME
        ):
            lidos.extend((self.tokens[i], self.tokens[i + 1]))
            i += 2
        return lidos, i

    @staticmethod
    def _nome_dos_tokens(lidos: Sequence[tokenize.TokenInfo]) -> str:
        return "".join(token.string for token in lidos)

    # -- instruções de import ---------------------------------------------------------------

    def _import(self, i: int) -> int:
        """Trata `import a.b[ as c][, d.e]`; `i` aponta para a palavra `import`."""
        linha = self.tokens[i].start[0]
        i += 1
        while True:
            lido = self._ler_nome_pontuado(i)
            if lido is None:
                return i
            nome_tokens, i = lido
            antigo = self._nome_dos_tokens(nome_tokens)
            novo = trocar_prefixo(antigo, self.mapa)
            j = _significativo(self.tokens, i)
            tem_alias = j + 1 < len(self.tokens) and self.tokens[j].string == "as"
            self._trocar(
                self.deslocamento(nome_tokens[0].start),
                self.deslocamento(nome_tokens[-1].end),
                antigo,
                novo,
                linha,
                "import ",
            )
            if novo != antigo and not tem_alias and novo.split(".")[0] != antigo.split(".")[0]:
                # `import a.b` liga o nome `a`; depois da troca ele deixa de existir no corpo.
                self.resultado.trocas[-1] += f" [revise os usos de '{antigo.split('.')[0]}']"
            if tem_alias:
                i = j + 2
            j = _significativo(self.tokens, i)
            if j < len(self.tokens) and _eh_op(self.tokens[j], ","):
                i = j + 1
                continue
            return i

    def _from(self, i: int) -> int:
        """Trata `from P import ...`, absoluto ou relativo; `i` aponta para a palavra `from`."""
        inicio_instrucao = i
        linha = self.tokens[i].start[0]
        j = _significativo(self.tokens, i + 1)
        pontos: list[tokenize.TokenInfo] = []
        while j < len(self.tokens) and self.tokens[j].type == tokenize.OP:
            if self.tokens[j].string not in (".", "..."):
                break
            pontos.append(self.tokens[j])
            j += 1
        sem_modulo = bool(pontos) and j < len(self.tokens) and self.tokens[j].string == "import"
        lido = None if sem_modulo else self._ler_nome_pontuado(j)
        if lido is None and not pontos:
            return i + 1
        nome_tokens, i = lido if lido is not None else ([], j)
        i = _significativo(self.tokens, i)
        if i >= len(self.tokens) or self.tokens[i].string != "import":
            return i
        i += 1
        nomes: list[str] = []
        i = _significativo(self.tokens, i)
        if i < len(self.tokens) and _eh_op(self.tokens[i], "("):
            i += 1
        while True:
            i = _significativo(self.tokens, i)
            if i >= len(self.tokens):
                break
            token = self.tokens[i]
            if _eh_op(token, "*") or token.type == tokenize.NAME:
                nomes.append(token.string)
                i += 1
            else:
                break
            j = _significativo(self.tokens, i)
            if j + 1 < len(self.tokens) and self.tokens[j].string == "as":
                i = j + 2
            j = _significativo(self.tokens, i)
            if j < len(self.tokens) and _eh_op(self.tokens[j], ","):
                i = j + 1
                continue
            break
        fim_instrucao = self.tokens[min(i, len(self.tokens)) - 1].end
        trecho = " ".join(
            self.texto[
                self.deslocamento(self.tokens[inicio_instrucao].start) : self.deslocamento(
                    fim_instrucao
                )
            ].split()
        )
        modulo = self._nome_dos_tokens(nome_tokens)
        if not pontos:
            self._reescrever_from(
                modulo, nome_tokens[0], nome_tokens[-1], modulo, nomes, linha, trecho
            )
            return i
        nivel = sum(len(ponto.string) for ponto in pontos)
        ultimo = nome_tokens[-1] if nome_tokens else pontos[-1]
        absoluto = self._resolver_relativo(nivel, modulo)
        if absoluto is not None and self._relativo_conhecido(absoluto, nomes):
            self._reescrever_from(
                absoluto, pontos[0], ultimo, "." * nivel + modulo, nomes, linha, trecho
            )
        return i

    def _resolver_relativo(self, nivel: int, modulo: str) -> str | None:
        """Nome antigo absoluto de `from <nivel pontos><modulo> import ...` neste arquivo."""
        if self.modulo_antigo is None:
            return None
        partes = self.modulo_antigo.split(".")
        pacote = partes if self.eh_pacote_antigo else partes[:-1]
        subir = nivel - 1
        if subir > len(pacote):
            return None
        base = pacote[: len(pacote) - subir]
        if modulo:
            base = [*base, *modulo.split(".")]
        return ".".join(base) or None

    def _relativo_conhecido(self, pacote: str, nomes: Sequence[str]) -> bool:
        """O alvo do import relativo é um nome que o mapa conhece (senão o import não muda)."""
        if pacote in self.mapa:
            return True
        return bool(nomes) and all(
            nome != "*" and f"{pacote}.{nome}" in self.mapa for nome in nomes
        )

    def _reescrever_from(
        self,
        pacote: str,
        primeiro: tokenize.TokenInfo,
        ultimo: tokenize.TokenInfo,
        antigo_no_texto: str,
        nomes: Sequence[str],
        linha: int,
        trecho: str,
    ) -> None:
        """Troca `P` em `from P import ...` (o trecho vai de `primeiro` até `ultimo`).

        `pacote` é o nome antigo absoluto de `P`; `antigo_no_texto` é como `P` está escrito (com os
        pontos, se for relativo).
        """
        pai_do_pacote = trocar_prefixo(pacote, self.mapa)
        pais: set[str] = set()
        for nome in nomes:
            alvo = f"{pacote}.{nome}"
            if nome != "*" and alvo in self.mapa:
                novo_pai, novo_ultimo = _pai_e_ultimo(self.mapa[alvo])
                if novo_ultimo != nome:
                    self.resultado.pendencias.append(
                        ImportAmbiguo(
                            "",
                            linha,
                            trecho,
                            f"'{alvo}' virou '{self.mapa[alvo]}', com outro nome de arquivo",
                        )
                    )
                    return
                pais.add(novo_pai)
            else:
                pais.add(pai_do_pacote)
        if len(pais) > 1:
            self.resultado.pendencias.append(
                ImportAmbiguo(
                    "", linha, trecho, "os nomes importados juntos vão para pacotes diferentes"
                )
            )
            return
        novo_pacote = pais.pop() if pais else pai_do_pacote
        self._trocar(
            self.deslocamento(primeiro.start),
            self.deslocamento(ultimo.end),
            antigo_no_texto,
            novo_pacote,
            linha,
            "from ",
        )

    # -- strings -----------------------------------------------------------------------------

    def _string(self, token: tokenize.TokenInfo, *, so_codigo: bool) -> None:
        """Reescreve nomes antigos num literal de string (nunca em f-string nem bytes)."""
        casou = _STRING.match(token.string)
        if casou is None:
            return
        prefixo = casou["prefixo"].lower()
        if "f" in prefixo or "b" in prefixo:
            return
        base = self.deslocamento(token.start) + len(casou["prefixo"]) + len(casou["aspas"])
        conteudo = casou["conteudo"]
        linha = token.start[0]
        if not so_codigo:
            self._string_de_nome(conteudo, base, linha)
        for achado in _CODIGO_EM_STRING.finditer(conteudo):
            grupo = "de" if achado["de"] else "nome"
            antigo = achado[grupo]
            novo = trocar_prefixo(antigo, self.mapa)
            if novo != antigo:
                inicio = base + achado.start(grupo)
                self._trocar(inicio, inicio + len(antigo), antigo, novo, linha, "código em string ")

    def _string_de_nome(self, conteudo: str, base: int, linha: int) -> None:
        """Conteúdo que é um nome antigo, ou que começa com `nome_antigo.` (ou `nome_antigo:`)."""
        achado = _PREFIXO_DE_NOME_NA_STRING.match(conteudo)
        if achado is None:
            return
        partes = achado.group().split(".")
        if len(partes) > 1 and partes[-1].lower() in EXTENSOES_DE_ARQUIVO:
            return
        for tamanho in range(len(partes), 0, -1):
            prefixo = ".".join(partes[:tamanho])
            if prefixo not in self.mapa:
                continue
            seguinte = conteudo[len(prefixo) : len(prefixo) + 1]
            if seguinte == ":" and conteudo[len(prefixo) + 1 :][:1].isidentifier():
                seguinte = ""  # `modulo:atributo`, como em ponto de entrada
            if seguinte not in ("", "."):
                continue
            if prefixo in NOMES_COMUNS:
                self.resultado.avisos.append(
                    f'linha {linha}: string ambígua não alterada: "{conteudo[:60]}"'
                    f" ('{prefixo}' é nome comum)"
                )
                return
            novo = self.mapa[prefixo]
            self._trocar(base, base + len(prefixo), prefixo, novo, linha, "string ")
            return

    # -- laço principal ----------------------------------------------------------------------

    def analisar(self) -> _Analise:
        """Percorre todos os tokens e devolve as edições, as trocas e as pendências."""
        tokens = self.tokens
        anterior: tokenize.TokenInfo | None = None  # último token que importa
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token.type in _NAO_SIGNIFICATIVOS:
                i += 1
                continue
            comeca_instrucao = (
                anterior is None
                or anterior.type == tokenize.NEWLINE
                or (anterior.type == tokenize.OP and anterior.string in (";", ":"))
            )
            if comeca_instrucao and token.type == tokenize.NAME and token.string == "import":
                i = self._import(i)
            elif comeca_instrucao and token.type == tokenize.NAME and token.string == "from":
                i = self._from(i)
            else:
                if token.type == tokenize.STRING and not self.em_migracao_django:
                    seguinte = _significativo(tokens, i + 1)
                    # Texto solto numa linha (docstring): só o código de exemplo dentro dele.
                    docstring = (
                        comeca_instrucao
                        and seguinte < len(tokens)
                        and tokens[seguinte].type == tokenize.NEWLINE
                    )
                    self._string(token, so_codigo=docstring)
                i += 1
            anterior = token
        return self.resultado


def _aplicar(texto: str, edicoes: Sequence[_Edicao]) -> str:
    for edicao in sorted(edicoes, key=lambda e: e.inicio, reverse=True):
        texto = texto[: edicao.inicio] + edicao.novo + texto[edicao.fim :]
    return texto


def analisar_codigo(
    texto: str,
    mapa: Mapping[str, str],
    *,
    em_migracao_django: bool,
    modulo_antigo: str | None = None,
    eh_pacote_antigo: bool = False,
) -> ResultadoDaAnalise:
    """Reescreve o que o mapa pede e devolve texto novo, trocas, pendências e avisos.

    Com `modulo_antigo` (o nome pontuado que o arquivo tinha antes da migração), os imports
    relativos viram absolutos: são resolvidos contra o pacote antigo e depois mapeados como
    qualquer outro. `eh_pacote_antigo` diz se o arquivo era um `__init__.py`. Sem `modulo_antigo`
    os imports relativos ficam como estão.
    """
    analise = _Reescritor(
        texto,
        mapa,
        em_migracao_django=em_migracao_django,
        modulo_antigo=modulo_antigo,
        eh_pacote_antigo=eh_pacote_antigo,
    ).analisar()
    return ResultadoDaAnalise(
        _aplicar(texto, analise.edicoes), analise.trocas, analise.pendencias, analise.avisos
    )


def reescrever_codigo(
    texto: str,
    mapa: Mapping[str, str],
    *,
    em_migracao_django: bool,
    modulo_antigo: str | None = None,
    eh_pacote_antigo: bool = False,
) -> tuple[str, list[str]]:
    """Texto novo e a lista de trocas feitas; levanta `ImportAmbiguo` na primeira pendência."""
    resultado = analisar_codigo(
        texto,
        mapa,
        em_migracao_django=em_migracao_django,
        modulo_antigo=modulo_antigo,
        eh_pacote_antigo=eh_pacote_antigo,
    )
    if resultado.pendencias:
        raise resultado.pendencias[0]
    return resultado.texto, resultado.trocas


# --------------------------------------------------------------------------------------
# Linha de comando
# --------------------------------------------------------------------------------------


def eh_migracao_django(caminho: Path) -> bool:
    """Arquivos dentro de uma pasta `migrations` guardam rótulos de app, não módulos."""
    return "migrations" in caminho.parts


def _relativo(caminho: Path, raiz: Path | None = None) -> str:
    try:
        return caminho.resolve().relative_to((raiz or RAIZ).resolve()).as_posix()
    except ValueError:
        return caminho.as_posix()


def _ignorado(caminho: Path) -> bool:
    relativo = _relativo(caminho)
    return any(relativo == p or relativo.startswith(f"{p}/") for p in IGNORADOS)


def coletar_arquivos(caminhos: Sequence[Path]) -> list[Path]:
    """Arquivos `.py` dos caminhos dados (diretórios são percorridos), em ordem estável."""
    achados: list[Path] = []
    for caminho in caminhos:
        if caminho.is_dir():
            for arquivo in sorted(caminho.rglob("*.py")):
                if not PASTAS_PULADAS.intersection(arquivo.relative_to(caminho).parts):
                    achados.append(arquivo)
        elif caminho.suffix == ".py":
            achados.append(caminho)
    return [arquivo for arquivo in achados if not _ignorado(arquivo)]


@dataclass
class ResultadoDoArquivo:
    caminho: Path
    trocas: list[str]
    pendencias: list[ImportAmbiguo]
    avisos: list[str] = field(default_factory=list)
    erro: str = ""
    mudou: bool = False


def reescrever_arquivo(
    caminho: Path,
    mapa: Mapping[str, str],
    *,
    aplicar: bool,
    raiz: Path | None = None,
    movimentos: Sequence[Movimento] = TABELA_MOVIMENTOS,
) -> ResultadoDoArquivo:
    """Reescreve um arquivo. Com pendências, aplica o resto e deixa o ambíguo como está.

    Se o arquivo é o destino (ou ainda a origem) de um movimento da tabela, os imports relativos
    dele também viram absolutos, resolvidos contra o nome que ele tinha antes da migração.
    """
    bruto = caminho.read_bytes()
    try:
        texto = bruto.decode("utf-8")
    except UnicodeDecodeError as erro:
        return ResultadoDoArquivo(caminho, [], [], erro=f"não é UTF-8: {erro}")
    bom = BOM if texto.startswith(BOM) else ""
    texto = texto.removeprefix(BOM)
    nome = _relativo(caminho, raiz)
    antigo = modulo_antigo_do_arquivo(nome, movimentos, RAIZES)
    try:
        analise = analisar_codigo(
            texto,
            mapa,
            em_migracao_django=eh_migracao_django(caminho),
            modulo_antigo=antigo[0] if antigo else None,
            eh_pacote_antigo=antigo[1] if antigo else False,
        )
    except (tokenize.TokenError, SyntaxError, RuntimeError) as erro:
        return ResultadoDoArquivo(caminho, [], [], erro=f"não foi possível analisar: {erro}")
    for pendencia in analise.pendencias:
        pendencia.arquivo = nome
    mudou = analise.texto != texto
    if mudou and aplicar:
        caminho.write_bytes((bom + analise.texto).encode("utf-8"))
    return ResultadoDoArquivo(
        caminho, analise.trocas, analise.pendencias, analise.avisos, mudou=mudou
    )


def _argumentos(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Reescreve imports e nomes pontuados antigos para os do monólito."
    )
    modo = parser.add_mutually_exclusive_group(required=True)
    modo.add_argument("--simular", action="store_true", help="só mostra o que mudaria")
    modo.add_argument("--aplicar", action="store_true", help="grava as mudanças nos arquivos")
    parser.add_argument("caminhos", nargs="+", type=Path, metavar="CAMINHO")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Ponto de entrada: imprime cada troca; com pendência ou erro, sai com 1."""
    args = _argumentos(argv)
    inexistentes = [c for c in args.caminhos if not c.exists()]
    if inexistentes:
        print(f"Caminho inexistente: {', '.join(map(str, inexistentes))}", file=sys.stderr)
        return 2
    mapa = mapa_da_tabela()
    alterados = trocas_total = 0
    pendencias: list[ImportAmbiguo] = []
    erros: list[str] = []
    avisos: list[str] = []
    for arquivo in coletar_arquivos(args.caminhos):
        resultado = reescrever_arquivo(arquivo, mapa, aplicar=args.aplicar)
        pendencias.extend(resultado.pendencias)
        avisos.extend(f"{_relativo(arquivo)}: {aviso}" for aviso in resultado.avisos)
        if resultado.erro:
            erros.append(f"{_relativo(arquivo)}: {resultado.erro}")
        if resultado.trocas:
            print(_relativo(arquivo))
            for troca in resultado.trocas:
                print(f"  {troca}")
        alterados += resultado.mudou
        trocas_total += len(resultado.trocas)
    modo = "aplicado" if args.aplicar else "simulação"
    print(f"\n{modo}: {alterados} arquivo(s) com mudança, {trocas_total} troca(s).")
    if erros:
        print(f"\nErros ({len(erros)}):", file=sys.stderr)
        for erro in erros:
            print(f"  {erro}", file=sys.stderr)
    if avisos:
        print(f"\nStrings ambíguas que NÃO foram alteradas ({len(avisos)}), confira à mão:")
        for aviso in avisos:
            print(f"  {aviso}")
    if pendencias:
        print(f"\nPendências de import ({len(pendencias)}), a corrigir à mão:")
        for pendencia in pendencias:
            print(f"  {pendencia.arquivo}:{pendencia.linha}: {pendencia.trecho}")
            print(f"      motivo: {pendencia.motivo}")
    return 1 if (pendencias or erros) else 0


if __name__ == "__main__":
    raise SystemExit(main())
