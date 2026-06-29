"""Caso de uso: inventário de repositórios GitHub em um database do Notion.

Diferente de :mod:`services.sincronizar_github` (que é orientado a *tarefas*),
este serviço materializa um **inventário** — um database com uma página por
repositório, com propriedades ricas (estrelas, linguagem, licença, datas...) e o
**README exportado no corpo** de cada página.

Camadas: a coleta vem do :class:`GitHubClient` (HTTP/normalização), a escrita vai
pelo :class:`NotionClient` e por :func:`services.conteudo.escrever_conteudo`
(Markdown → blocos). Aqui mora só a regra de negócio do inventário.

Pontos de extensão (Open/Closed):
- :class:`CamposGitHub` permite renomear as colunas sem tocar no mapeamento.
- :data:`construir_schema` define o schema do database de forma isolada.
- A lista de contas é um parâmetro, não um valor fixo.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from integrations.github import GitHubClient, RepoInfo

from notion_starter import NotionClient, properties

# Limite defensivo do tamanho do README importado (Markdown bruto).
MAX_README_CHARS = 100_000


@dataclass(frozen=True)
class CamposGitHub:
    """Nomes das propriedades do database de inventário GitHub.

    Configurável para que workspaces com colunas em outro idioma/nome reusem o
    serviço sem alterar o mapeamento.
    """

    nome: str = "Nome"
    dono: str = "Conta"
    descricao: str = "Descrição"
    url: str = "URL"
    homepage: str = "Homepage"
    linguagem: str = "Linguagem"
    topicos: str = "Tópicos"
    licenca: str = "Licença"
    estrelas: str = "Estrelas"
    forks: str = "Forks"
    issues: str = "Issues abertas"
    tamanho_kb: str = "Tamanho (KB)"
    privado: str = "Privado"
    fork: str = "Fork"
    arquivado: str = "Arquivado"
    criado_em: str = "Criado em"
    atualizado_em: str = "Atualizado em"
    enviado_em: str = "Último push"


@dataclass
class ResumoInventario:
    """Resultado de uma exportação de inventário."""

    repos_encontrados: int = 0
    paginas_criadas: int = 0
    paginas_atualizadas: int = 0
    readmes_escritos: int = 0
    erros: list[str] = field(default_factory=list)

    @property
    def total_erros(self) -> int:
        return len(self.erros)


def construir_schema(campos: CamposGitHub | None = None) -> dict[str, dict[str, object]]:
    """Monta o schema (definição de colunas) do database de inventário.

    Retorna o formato cru da API do Notion esperado por
    :meth:`NotionClient.criar_database`. A coluna ``nome`` é o ``title``.
    """

    c = campos or CamposGitHub()
    return {
        c.nome: {"title": {}},
        c.dono: {"select": {}},
        c.descricao: {"rich_text": {}},
        c.url: {"url": {}},
        c.homepage: {"url": {}},
        c.linguagem: {"select": {}},
        c.topicos: {"multi_select": {}},
        c.licenca: {"select": {}},
        c.estrelas: {"number": {}},
        c.forks: {"number": {}},
        c.issues: {"number": {}},
        c.tamanho_kb: {"number": {}},
        c.privado: {"checkbox": {}},
        c.fork: {"checkbox": {}},
        c.arquivado: {"checkbox": {}},
        c.criado_em: {"date": {}},
        c.atualizado_em: {"date": {}},
        c.enviado_em: {"date": {}},
    }


def _propriedades_pagina(
    repo: RepoInfo,
    campos: CamposGitHub,
) -> dict[str, Any]:
    """Mapeia um :class:`RepoInfo` para as propriedades da página."""

    props: dict[str, Any] = {
        campos.nome: properties.title(repo.nome_completo or repo.nome),
        campos.estrelas: properties.number(repo.estrelas),
        campos.forks: properties.number(repo.forks),
        campos.issues: properties.number(repo.issues_abertas),
        campos.tamanho_kb: properties.number(repo.tamanho_kb),
        campos.privado: properties.checkbox(repo.privado),
        campos.fork: properties.checkbox(repo.fork),
        campos.arquivado: properties.checkbox(repo.arquivado),
    }
    if repo.dono:
        props[campos.dono] = properties.select(repo.dono)
    if repo.descricao:
        props[campos.descricao] = properties.rich_text(repo.descricao[:2000])
    if repo.url_html:
        props[campos.url] = properties.url(repo.url_html)
    if repo.homepage:
        props[campos.homepage] = properties.url(repo.homepage)
    if repo.linguagem:
        props[campos.linguagem] = properties.select(repo.linguagem)
    if repo.topicos:
        props[campos.topicos] = properties.multi_select(repo.topicos)
    if repo.licenca:
        props[campos.licenca] = properties.select(repo.licenca)
    if repo.criado_em:
        props[campos.criado_em] = properties.date(repo.criado_em)
    if repo.atualizado_em:
        props[campos.atualizado_em] = properties.date(repo.atualizado_em)
    if repo.enviado_em:
        props[campos.enviado_em] = properties.date(repo.enviado_em)
    return props


def garantir_database(
    pagina_id: str,
    *,
    titulo: str = "GITHUB",
    cliente: NotionClient,
    campos: CamposGitHub | None = None,
) -> str:
    """Cria o database de inventário sob ``pagina_id`` e devolve o ID.

    Não tenta deduplicar databases existentes: a busca do Notion não filtra por
    página-pai de forma confiável, e criar o database é a operação que o chamador
    pede explicitamente. Para reusar um database já criado, passe o ID dele pelo
    chamador em vez de chamar esta função.
    """

    campos = campos or CamposGitHub()
    resposta = cliente.criar_database(
        pagina_id=pagina_id,
        titulo=titulo,
        propriedades=construir_schema(campos),
    )
    database_id = str(resposta.get("id") or "")
    if not database_id:
        raise ValueError("O Notion não retornou o ID do database criado.")
    return database_id


def _pagina_existente(
    cliente: NotionClient,
    database_id: str,
    repo: RepoInfo,
    campos: CamposGitHub,
) -> dict[str, Any] | None:
    """Procura uma página do repositório por URL (ou nome, se faltar URL)."""

    if repo.url_html:
        filtro: dict[str, object] = {
            "property": campos.url,
            "url": {"equals": repo.url_html},
        }
    else:
        filtro = {
            "property": campos.nome,
            "title": {"equals": repo.nome_completo or repo.nome},
        }
    paginas = cliente.consultar_database(database_id, page_size=1, filtro=filtro)
    return paginas[0] if paginas else None


def _escrever_readme(
    cliente: NotionClient,
    page_id: str,
    readme: str,
) -> bool:
    """Cria uma subpágina ``README`` dentro da página do projeto.

    O conteúdo do README (Markdown) é convertido em blocos e vai para uma
    **página filha** chamada ``README`` — não para o corpo da própria linha do
    database —, deixando a linha limpa e fácil de organizar depois. A quebra em
    lotes ≤100 blocos é responsabilidade de :meth:`NotionClient.criar_subpagina`.

    Retorna ``True`` se a subpágina foi criada com conteúdo.
    """

    from services.conteudo import markdown_para_blocos

    texto = (readme or "").strip()
    if not texto:
        return False

    blocos = markdown_para_blocos(texto[:MAX_README_CHARS])
    if not blocos:
        return False

    cliente.criar_subpagina(page_id, "README", blocos=blocos)
    return True


def exportar_repos(
    contas: list[str],
    database_id: str,
    *,
    github_client: GitHubClient,
    notion_client: NotionClient,
    campos: CamposGitHub | None = None,
    incluir_readme: bool = True,
) -> ResumoInventario:
    """Exporta os repositórios das ``contas`` para o ``database_id``.

    Faz *upsert* por repositório (cria a página ou atualiza a existente) e, quando
    ``incluir_readme`` é verdadeiro, busca os detalhes do repo e escreve o README
    no corpo da página recém-criada. READMEs só são escritos em páginas novas,
    para não duplicar o conteúdo em execuções repetidas.

    Erros por repositório são acumulados em :attr:`ResumoInventario.erros` e não
    interrompem a exportação dos demais.
    """

    if not contas:
        raise ValueError("Informe ao menos uma conta do GitHub.")
    if not database_id:
        raise ValueError("database_id é obrigatório.")

    campos = campos or CamposGitHub()
    resumo = ResumoInventario()
    vistos: set[str] = set()

    for conta in contas:
        try:
            repos = github_client.listar_repos(conta)
        except Exception as exc:  # noqa: BLE001 — registramos e seguimos
            resumo.erros.append(f"listar {conta}: {exc}")
            continue

        for repo in repos:
            chave = repo.url_html or repo.nome_completo
            if chave in vistos:
                continue
            vistos.add(chave)
            resumo.repos_encontrados += 1
            _exportar_repo(
                repo,
                database_id,
                github_client=github_client,
                notion_client=notion_client,
                campos=campos,
                incluir_readme=incluir_readme,
                resumo=resumo,
            )

    return resumo


def _exportar_repo(
    repo: RepoInfo,
    database_id: str,
    *,
    github_client: GitHubClient,
    notion_client: NotionClient,
    campos: CamposGitHub,
    incluir_readme: bool,
    resumo: ResumoInventario,
) -> None:
    """Cria/atualiza a página de um repositório e escreve o README se for nova."""

    try:
        props = _propriedades_pagina(repo, campos)
        existente = _pagina_existente(notion_client, database_id, repo, campos)
        if existente and existente.get("id"):
            notion_client.atualizar_pagina(str(existente["id"]), props)
            resumo.paginas_atualizadas += 1
            return

        criada = notion_client.criar_pagina(database_id, props)
        resumo.paginas_criadas += 1
    except Exception as exc:  # noqa: BLE001 — registramos e seguimos
        resumo.erros.append(f"{repo.nome_completo}: {exc}")
        return

    if not incluir_readme:
        return

    page_id = str(criada.get("id") or "")
    if not page_id:
        return
    try:
        detalhado = github_client.detalhar_repo(repo.nome_completo)
        if detalhado.readme and _escrever_readme(notion_client, page_id, detalhado.readme):
            resumo.readmes_escritos += 1
    except Exception as exc:  # noqa: BLE001 — README é best-effort
        resumo.erros.append(f"readme {repo.nome_completo}: {exc}")
