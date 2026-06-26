"""Conversão entre Markdown e blocos do Notion.

Par de **escrita** (``markdown_para_blocos``) e **leitura**
(``blocos_para_markdown``) que poupa quem usa a biblioteca de decorar o JSON
verboso de blocos do Notion. Uma IA (ou um humano) escreve Markdown comum e
recebe Markdown de volta ao ler uma página; a montagem dos blocos fica aqui.

São funções pequenas e puras — sem rede, sem estado. O acesso HTTP aos blocos
vive em :class:`notion_starter.client.NotionClient` (``ler_blocos``,
``anexar_blocos``, ``atualizar_bloco``, ``excluir_bloco``); a orquestração
("ler a página como texto", "anexar conteúdo") fica na camada de serviço.

Cobre os blocos de uso cotidiano em notas: títulos (``#``/``##``/``###``),
parágrafos, listas com marcador (``-``) e numeradas (``1.``), tarefas
(``- [ ]`` / ``- [x]``), citações (``>``), código (cercado por ``` ``` ```) e
divisória (``---``). Blocos fora desse conjunto, ao ler, viram texto simples a
partir do *rich text* do bloco, para nunca perder conteúdo silenciosamente.

Exemplo:
    >>> blocos = markdown_para_blocos("# Título\\n\\nUm parágrafo.")
    >>> blocos[0]["type"]
    'heading_1'
    >>> blocos_para_markdown(blocos)
    '# Título\\n\\nUm parágrafo.'
"""

from __future__ import annotations

from typing import Any

# Tipos de bloco do Notion que carregam *rich text* num campo de mesmo nome.
_TIPOS_TEXTO = (
    "paragraph",
    "heading_1",
    "heading_2",
    "heading_3",
    "bulleted_list_item",
    "numbered_list_item",
    "to_do",
    "quote",
    "callout",
    "toggle",
    "code",
)


def _rich_text(texto: str) -> list[dict[str, Any]]:
    """Monta o *rich text* de um bloco a partir de texto simples."""

    if not texto:
        return []
    return [{"type": "text", "text": {"content": texto}}]


def _bloco(tipo: str, texto: str, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    """Monta um bloco do Notion de um tipo que carrega *rich text*."""

    corpo: dict[str, Any] = {"rich_text": _rich_text(texto)}
    if extra:
        corpo.update(extra)
    return {"object": "block", "type": tipo, tipo: corpo}


def _texto_de_bloco(bloco: dict[str, Any]) -> str:
    """Extrai o texto simples de um bloco, qualquer que seja o tipo textual."""

    tipo = bloco.get("type", "")
    corpo = bloco.get(tipo, {})
    itens = corpo.get("rich_text", []) if isinstance(corpo, dict) else []
    return "".join(_texto_de_item(item) for item in itens).strip()


def _texto_de_item(item: dict[str, Any]) -> str:
    """Extrai o texto de um item de *rich text*, ignorando ícones decorativos.

    *Custom emojis* (ícones de imagem usados em títulos) vêm como menção com
    ``plain_text`` no formato ``:nome:`` — ruído visual, não conteúdo. São
    descartados para o Markdown ficar legível.
    """

    mention = item.get("mention")
    if isinstance(mention, dict) and mention.get("type") == "custom_emoji":
        return ""
    return item.get("plain_text", item.get("text", {}).get("content", ""))


def markdown_para_blocos(markdown: str) -> list[dict[str, Any]]:
    """Converte um texto Markdown em blocos do Notion.

    Linhas em branco separam blocos; cada linha não vazia vira um bloco do tipo
    correspondente. Trechos cercados por ``` ``` ``` viram um único bloco de
    código preservando as quebras internas.

    Args:
        markdown: Texto em Markdown.

    Returns:
        A lista de blocos no formato aceito por ``anexar_blocos``.
    """

    blocos: list[dict[str, Any]] = []
    linhas = markdown.splitlines()
    i = 0
    while i < len(linhas):
        linha = linhas[i]
        despojada = linha.strip()

        if despojada.startswith("```"):
            lingua = despojada[3:].strip()
            corpo: list[str] = []
            i += 1
            while i < len(linhas) and not linhas[i].strip().startswith("```"):
                corpo.append(linhas[i])
                i += 1
            i += 1  # pula o fechamento ```
            blocos.append(
                _bloco("code", "\n".join(corpo), {"language": lingua or "plain text"})
            )
            continue

        if not despojada:
            i += 1
            continue

        blocos.append(_linha_para_bloco(despojada))
        i += 1

    return blocos


def _linha_para_bloco(linha: str) -> dict[str, Any]:
    """Mapeia uma linha de Markdown já despojada para um bloco do Notion."""

    if linha == "---":
        return {"object": "block", "type": "divider", "divider": {}}
    if linha.startswith("### "):
        return _bloco("heading_3", linha[4:])
    if linha.startswith("## "):
        return _bloco("heading_2", linha[3:])
    if linha.startswith("# "):
        return _bloco("heading_1", linha[2:])
    if linha.startswith("> "):
        return _bloco("quote", linha[2:])
    if linha[:6].lower() in ("- [ ] ", "- [x] "):
        marcado = linha[3] == "x"
        return _bloco("to_do", linha[6:], {"checked": marcado})
    if linha.startswith(("- ", "* ")):
        return _bloco("bulleted_list_item", linha[2:])
    numerada = _prefixo_numerado(linha)
    if numerada is not None:
        return _bloco("numbered_list_item", numerada)
    return _bloco("paragraph", linha)


def _prefixo_numerado(linha: str) -> str | None:
    """Devolve o texto após ``N. `` numa lista numerada, ou ``None``."""

    ponto = linha.find(". ")
    if ponto > 0 and linha[:ponto].isdigit():
        return linha[ponto + 2 :]
    return None


def blocos_para_markdown(blocos: list[dict[str, Any]]) -> str:
    """Converte blocos do Notion de volta em Markdown legível.

    Tipos conhecidos viram a marcação correspondente; tipos desconhecidos que
    tenham *rich text* viram parágrafo, para nunca descartar conteúdo. Blocos
    aninhados (a chave ``_filhos``, presente quando ``ler_blocos`` é recursivo)
    são incluídos logo após o bloco-pai — assim o conteúdo dentro de colunas e
    toggles não some.

    Args:
        blocos: Lista de blocos como retornados por ``ler_blocos``.

    Returns:
        O texto em Markdown, com blocos separados por linha em branco.
    """

    linhas: list[str] = []
    for bloco in blocos:
        linha = _bloco_para_linha(bloco)
        if linha is not None:
            linhas.append(linha)
        filhos = bloco.get("_filhos")
        if filhos:
            aninhado = blocos_para_markdown(filhos)
            if aninhado:
                linhas.append(aninhado)
    return "\n\n".join(linhas)


def _titulo_child_database(bloco: dict[str, Any]) -> str:
    """Título de um bloco ``child_database`` (cai para ``"(sem título)"``)."""

    titulo = bloco.get("child_database", {}).get("title", "")
    return titulo or "(sem título)"


def _bloco_para_linha(bloco: dict[str, Any]) -> str | None:
    """Converte um único bloco em sua linha Markdown (``None`` se vazio)."""

    tipo = bloco.get("type", "")
    texto = _texto_de_bloco(bloco)
    if tipo == "divider":
        return "---"
    if tipo == "heading_1":
        return f"# {texto}"
    if tipo == "heading_2":
        return f"## {texto}"
    if tipo == "heading_3":
        return f"### {texto}"
    if tipo == "quote":
        return f"> {texto}"
    if tipo == "bulleted_list_item":
        return f"- {texto}"
    if tipo == "numbered_list_item":
        return f"1. {texto}"
    if tipo == "to_do":
        marca = "x" if bloco.get("to_do", {}).get("checked") else " "
        return f"- [{marca}] {texto}"
    if tipo == "code":
        lingua = bloco.get("code", {}).get("language", "")
        return f"```{lingua}\n{texto}\n```"
    if tipo == "child_database":
        return f"**[database: {_titulo_child_database(bloco)}]**"
    if tipo == "child_page":
        return f"**[página: {bloco.get('child_page', {}).get('title', '') or '(sem título)'}]**"
    if tipo in _TIPOS_TEXTO:
        return texto or None
    return texto or None
