"""Cliente HTTP para a API do Notion."""

from __future__ import annotations

import os
from typing import Any

import requests

try:  # ``NotRequired`` só existe em ``typing`` a partir do 3.11.
    from typing import NotRequired, TypedDict
except ImportError:  # pragma: no cover - fallback para Python 3.10
    from typing_extensions import NotRequired, TypedDict

from .constants import (
    NOTION_BASE_URL,
    NOTION_TIMEOUT_SECONDS,
    NOTION_TOKEN_ENV,
    NOTION_TOKEN_PREFIX,
    NOTION_VERSION,
)
from .exceptions import (
    NotionConfigurationError,
    NotionConnectionError,
    NotionHTTPError,
    NotionInvalidResponseError,
)
from .logging import get_logger

logger = get_logger()


class DatabaseParentPayload(TypedDict):
    """Payload do parent de um database."""

    type: str
    page_id: str


class DatabaseTitleTextPayload(TypedDict):
    """Payload de texto do título de um database."""

    content: str


class DatabaseTitleItemPayload(TypedDict):
    """Item do título de um database."""

    type: str
    text: DatabaseTitleTextPayload


class DatabaseCreatePayload(TypedDict):
    """Payload para criação de database."""

    parent: DatabaseParentPayload
    title: list[DatabaseTitleItemPayload]
    properties: dict[str, dict[str, object]]


class DatabaseQueryPayload(TypedDict):
    """Payload para consulta de database."""

    page_size: int
    filter: NotRequired[dict[str, object]]
    start_cursor: NotRequired[str]


class PageParentPayload(TypedDict):
    """Parent de página vinculada a um database."""

    database_id: str


class PageCreatePayload(TypedDict):
    """Payload para criação de página."""

    parent: PageParentPayload
    properties: dict[str, dict[str, object]]


class PageUpdatePayload(TypedDict):
    """Payload para atualização de página."""

    properties: dict[str, dict[str, object]]


class PageArchivePayload(TypedDict):
    """Payload para arquivamento de página."""

    archived: bool


def _validar_identificador(identificador: str, nome_campo: str) -> str:
    """Valida um identificador obrigatório do Notion.

    Args:
        identificador: Valor bruto recebido.
        nome_campo: Nome lógico do campo, usado na mensagem de erro.

    Returns:
        O identificador limpo.

    Raises:
        NotionConfigurationError: Se o identificador estiver vazio.
    """

    limpo = (identificador or "").strip()
    if not limpo:
        raise NotionConfigurationError(f"{nome_campo} não pode estar vazio.")
    return limpo


class NotionClient:
    """Wrapper fino e tipado sobre a API REST do Notion.

    Exemplo:
        >>> client = NotionClient(token="ntn_...")
        >>> client.criar_pagina(database_id, {"Nome": {"title": [{"text": {"content": "Oi"}}]}})

    Args:
        token: Token de integração do Notion. Quando omitido, é lido da
            variável de ambiente ``NOTION_TOKEN``.
        base_url: Sobrescreve a URL base da API (útil para testes).
        timeout: Timeout por requisição, em segundos.
        version: Valor enviado no header ``Notion-Version``.

    Raises:
        NotionConfigurationError: Se nenhum token válido puder ser resolvido.
    """

    def __init__(
        self,
        token: str | None = None,
        *,
        base_url: str = NOTION_BASE_URL,
        timeout: int = NOTION_TIMEOUT_SECONDS,
        version: str = NOTION_VERSION,
    ) -> None:
        self._token = self._resolver_token(token)
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._version = version

    @staticmethod
    def _resolver_token(token: str | None) -> str:
        """Resolve e valida o token de integração.

        Args:
            token: Token explícito, ou ``None`` para ler do ambiente.

        Returns:
            O token validado.

        Raises:
            NotionConfigurationError: Se o token estiver ausente ou malformado.
        """

        bruto = token if token is not None else os.environ.get(NOTION_TOKEN_ENV, "")
        limpo = str(bruto).strip()
        if not limpo:
            raise NotionConfigurationError(
                f"Token do Notion ausente. Passe token=... ou defina a "
                f"variável de ambiente {NOTION_TOKEN_ENV}."
            )
        if not limpo.startswith(NOTION_TOKEN_PREFIX):
            raise NotionConfigurationError(
                f"Token do Notion inválido: ele deve começar com "
                f"'{NOTION_TOKEN_PREFIX}'."
            )
        return limpo

    def _headers(self) -> dict[str, str]:
        """Monta os headers padrão autenticados."""

        return {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
            "Notion-Version": self._version,
        }

    def _request_json(
        self,
        *,
        method: str,
        path: str,
        payload: dict[str, object] | None = None,
    ) -> dict[str, Any]:
        """Executa uma requisição JSON contra a API do Notion.

        Args:
            method: Método HTTP.
            path: Caminho relativo à URL base.
            payload: Corpo JSON opcional.

        Returns:
            A resposta JSON decodificada.

        Raises:
            NotionHTTPError: Se a API responder com 4xx/5xx.
            NotionConnectionError: Em falha de rede ou timeout.
            NotionInvalidResponseError: Se a resposta não for JSON válido.
        """

        url = f"{self._base_url}{path}"
        try:
            response = requests.request(
                method=method,
                url=url,
                json=payload,
                headers=self._headers(),
                timeout=self._timeout,
            )
            response.raise_for_status()
        except requests.HTTPError as exc:
            status_code = exc.response.status_code if exc.response is not None else 500
            body = exc.response.text if exc.response is not None else str(exc)
            logger.error("Erro HTTP do Notion", extra={"status_code": status_code, "path": path})
            raise NotionHTTPError(status_code, body) from exc
        except requests.RequestException as exc:
            logger.error("Erro de conexão com o Notion", extra={"path": path, "error": str(exc)})
            raise NotionConnectionError(str(exc)) from exc

        try:
            return response.json()
        except ValueError as exc:
            logger.error("Resposta JSON inválida do Notion", extra={"path": path})
            raise NotionInvalidResponseError(
                "A API do Notion retornou um JSON inválido."
            ) from exc

    # -- Databases ---------------------------------------------------------

    def get_database(self, database_id: str) -> dict[str, Any]:
        """Busca os metadados de um database Notion.

        Args:
            database_id: ID do database.

        Returns:
            A resposta JSON do database solicitado.
        """

        limpo = _validar_identificador(database_id, "database_id")
        return self._request_json(method="GET", path=f"/databases/{limpo}")

    def criar_database(
        self,
        pagina_id: str,
        titulo: str,
        propriedades: dict[str, dict[str, object]],
    ) -> dict[str, Any]:
        """Cria um novo database como filho de uma página.

        Args:
            pagina_id: ID da página pai.
            titulo: Título do database.
            propriedades: Schema do database no formato da API.

        Returns:
            A resposta JSON do database criado.
        """

        pagina_limpa = _validar_identificador(pagina_id, "pagina_id")
        titulo_limpo = _validar_identificador(titulo, "titulo")
        payload: DatabaseCreatePayload = {
            "parent": {"type": "page_id", "page_id": pagina_limpa},
            "title": [{"type": "text", "text": {"content": titulo_limpo}}],
            "properties": propriedades,
        }
        return self._request_json(method="POST", path="/databases", payload=payload)

    def consultar_database(
        self,
        database_id: str,
        page_size: int = 100,
        buscar_todos: bool = False,
        filtro: dict[str, object] | None = None,
    ) -> list[dict[str, Any]]:
        """Consulta as páginas de um database com suporte a paginação.

        Args:
            database_id: ID do database.
            page_size: Quantidade de registros por página.
            buscar_todos: Quando verdadeiro, percorre toda a paginação.
            filtro: Filtro Notion opcional.

        Returns:
            A lista de páginas retornadas pela API.

        Raises:
            NotionConfigurationError: Se ``database_id`` for inválido.
            ValueError: Se ``page_size`` for menor que 1.
        """

        limpo = _validar_identificador(database_id, "database_id")
        if page_size < 1:
            raise ValueError("page_size deve ser maior que zero.")

        payload: DatabaseQueryPayload = {"page_size": page_size}
        if filtro:
            payload["filter"] = filtro

        resultados: list[dict[str, Any]] = []

        while True:
            data = self._request_json(
                method="POST",
                path=f"/databases/{limpo}/query",
                payload=payload,
            )
            resultados.extend(data.get("results", []))

            if not buscar_todos or not data.get("has_more"):
                break

            next_cursor = data.get("next_cursor")
            if not next_cursor:
                break
            payload["start_cursor"] = next_cursor

        return resultados

    # -- Páginas -----------------------------------------------------------

    def criar_pagina(
        self,
        database_id: str,
        propriedades: dict[str, dict[str, object]],
    ) -> dict[str, Any]:
        """Cria uma nova página dentro de um database.

        Args:
            database_id: ID do database de destino.
            propriedades: Propriedades da nova página.

        Returns:
            A resposta JSON da página criada.
        """

        limpo = _validar_identificador(database_id, "database_id")
        payload: PageCreatePayload = {
            "parent": {"database_id": limpo},
            "properties": propriedades,
        }
        return self._request_json(method="POST", path="/pages", payload=payload)

    def atualizar_pagina(
        self,
        page_id: str,
        propriedades: dict[str, dict[str, object]],
    ) -> dict[str, Any]:
        """Atualiza as propriedades de uma página existente.

        Args:
            page_id: ID da página.
            propriedades: Propriedades atualizadas.

        Returns:
            A resposta JSON da página atualizada.
        """

        limpo = _validar_identificador(page_id, "page_id")
        payload: PageUpdatePayload = {"properties": propriedades}
        return self._request_json(method="PATCH", path=f"/pages/{limpo}", payload=payload)

    def arquivar_pagina(self, page_id: str) -> dict[str, Any]:
        """Arquiva uma página do Notion.

        Args:
            page_id: ID da página.

        Returns:
            A resposta JSON da API.
        """

        limpo = _validar_identificador(page_id, "page_id")
        payload: PageArchivePayload = {"archived": True}
        return self._request_json(method="PATCH", path=f"/pages/{limpo}", payload=payload)
