"""Cliente HTTP para a API do Notion."""

from __future__ import annotations

import os
import time
from copy import deepcopy
from typing import Any

import requests

try:  # ``NotRequired`` só existe em ``typing`` a partir do 3.11.
    from typing import NotRequired, TypedDict
except ImportError:  # pragma: no cover - fallback para Python 3.10
    from typing_extensions import NotRequired, TypedDict

from .constants import (
    NOTION_BACKOFF_BASE,
    NOTION_BASE_URL,
    NOTION_MAX_RETRIES,
    NOTION_RATE_LIMIT_STATUS_CODES,
    NOTION_RETRYABLE_STATUS_CODES,
    NOTION_SCHEMA_CACHE_TTL,
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


class SearchPayload(TypedDict):
    """Payload para busca no workspace via ``/search``."""

    page_size: int
    query: NotRequired[str]
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
        max_retries: Número de retentativas em operações idempotentes após
            erros transitórios. ``0`` desabilita o retry.
        backoff_base: Base do backoff exponencial entre retentativas, em
            segundos. O tempo de espera é ``backoff_base * 2^tentativa``,
            exceto em 429 com ``Retry-After``, que tem prioridade.
        cache_ttl: TTL do cache de schema (``get_database``), em segundos.
            ``0`` desabilita o cache.

    Raises:
        NotionConfigurationError: Se nenhum token válido puder ser resolvido.
        ValueError: Se a configuração de retry/cache for negativa.
    """

    def __init__(
        self,
        token: str | None = None,
        *,
        base_url: str = NOTION_BASE_URL,
        timeout: int = NOTION_TIMEOUT_SECONDS,
        version: str = NOTION_VERSION,
        max_retries: int = NOTION_MAX_RETRIES,
        backoff_base: float = NOTION_BACKOFF_BASE,
        cache_ttl: int = NOTION_SCHEMA_CACHE_TTL,
    ) -> None:
        self._token = self._resolver_token(token)
        if max_retries < 0:
            raise ValueError("max_retries não pode ser negativo.")
        if backoff_base < 0:
            raise ValueError("backoff_base não pode ser negativo.")
        if cache_ttl < 0:
            raise ValueError("cache_ttl não pode ser negativo.")

        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._version = version
        self._max_retries = max_retries
        self._backoff_base = backoff_base
        self._cache_ttl = cache_ttl
        self._cache_schema: dict[str, tuple[float, dict[str, Any]]] = {}

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
                f"Token do Notion inválido: ele deve começar com '{NOTION_TOKEN_PREFIX}'."
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
        idempotente: bool,
    ) -> dict[str, Any]:
        """Executa uma requisição JSON contra a API do Notion.

        Operações idempotentes são retentadas em erros transitórios e falhas de
        rede, com backoff exponencial. Em criações, o retry fica restrito a
        respostas 429/529, nas quais o Notion orienta aguardar e repetir; falhas
        ambíguas de rede ou 5xx não são repetidas para evitar duplicatas.
        Respostas com ``Retry-After`` têm prioridade.

        Args:
            method: Método HTTP.
            path: Caminho relativo à URL base.
            payload: Corpo JSON opcional.
            idempotente: Se repetir a operação preserva o mesmo efeito.

        Returns:
            A resposta JSON decodificada.

        Raises:
            NotionHTTPError: Se a API responder com 4xx/5xx após esgotadas
                as retentativas.
            NotionConnectionError: Em falha de rede ou timeout após esgotadas
                as retentativas.
            NotionInvalidResponseError: Se a resposta não for JSON válido.
        """

        url = f"{self._base_url}{path}"
        total_tentativas = self._max_retries + 1

        for tentativa in range(total_tentativas):
            try:
                resp = requests.request(
                    method=method,
                    url=url,
                    json=payload,
                    headers=self._headers(),
                    timeout=self._timeout,
                )
            except requests.RequestException as exc:
                if idempotente and tentativa + 1 < total_tentativas:
                    espera = self._backoff_base * (2**tentativa)
                    logger.warning(
                        "Retentativa %d/%d após erro de conexão",
                        tentativa + 1,
                        self._max_retries,
                        extra={"path": path, "error": str(exc)},
                    )
                    time.sleep(espera)
                    continue
                logger.error(
                    "Erro de conexão com o Notion",
                    extra={"path": path, "error": str(exc)},
                )
                raise NotionConnectionError(str(exc)) from exc

            if resp.status_code < 400:
                try:
                    return resp.json()
                except ValueError as exc:
                    logger.error("Resposta JSON inválida do Notion", extra={"path": path})
                    raise NotionInvalidResponseError(
                        "A API do Notion retornou um JSON inválido."
                    ) from exc

            pode_retentar = idempotente or (resp.status_code in NOTION_RATE_LIMIT_STATUS_CODES)
            if (
                pode_retentar
                and resp.status_code in NOTION_RETRYABLE_STATUS_CODES
                and tentativa + 1 < total_tentativas
            ):
                espera = self._calcular_espera(resp, tentativa)
                logger.warning(
                    "Retentativa %d/%d após HTTP %d",
                    tentativa + 1,
                    self._max_retries,
                    resp.status_code,
                    extra={"path": path},
                )
                time.sleep(espera)
                continue

            logger.error(
                "Erro HTTP do Notion",
                extra={"status_code": resp.status_code, "path": path},
            )
            raise NotionHTTPError(resp.status_code, resp.text)

        raise RuntimeError("Fluxo de requisição terminou sem resposta.")

    def _calcular_espera(self, resp: requests.Response, tentativa: int) -> float:
        """Calcula o tempo de espera respeitando ``Retry-After``.

        Se a resposta contém o header ``Retry-After`` (comum em 429), usa esse
        valor. Caso contrário, usa backoff exponencial:
        ``backoff_base * 2^tentativa``.
        """

        retry_after = resp.headers.get("Retry-After")
        if retry_after:
            try:
                return max(float(retry_after), 0.0)
            except ValueError:
                pass
        return self._backoff_base * (2**tentativa)

    # -- Busca -------------------------------------------------------------

    def buscar(
        self,
        query: str | None = None,
        page_size: int = 100,
        buscar_todos: bool = False,
        filtro: dict[str, object] | None = None,
    ) -> list[dict[str, Any]]:
        """Busca páginas e databases compartilhados com a integração.

        Percorre o endpoint ``/search`` do Notion, que retorna apenas os itens
        que a integração tem permissão de ver. Sem ``query``, lista tudo o que é
        visível — útil para inventariar o workspace.

        Args:
            query: Texto para casar com o título dos itens. ``None`` retorna tudo.
            page_size: Quantidade de itens por página.
            buscar_todos: Quando verdadeiro, percorre toda a paginação.
            filtro: Filtro Notion opcional (ex.: só páginas ou só databases).

        Returns:
            A lista de itens (páginas e/ou databases) retornados pela API.

        Raises:
            ValueError: Se ``page_size`` for menor que 1.
            NotionHTTPError: Se a API responder com 4xx/5xx.
        """

        if page_size < 1:
            raise ValueError("page_size deve ser maior que zero.")

        payload: SearchPayload = {"page_size": page_size}
        if query:
            payload["query"] = query
        if filtro:
            payload["filter"] = filtro

        resultados: list[dict[str, Any]] = []

        while True:
            data = self._request_json(
                method="POST",
                path="/search",
                payload=payload,
                idempotente=True,
            )
            resultados.extend(data.get("results", []))

            if not buscar_todos or not data.get("has_more"):
                break

            next_cursor = data.get("next_cursor")
            if not next_cursor:
                break
            payload["start_cursor"] = next_cursor

        return resultados

    # -- Databases ---------------------------------------------------------

    def get_database(self, database_id: str) -> dict[str, Any]:
        """Busca os metadados de um database Notion.

        Usa cache em memória quando ``cache_ttl > 0`` — o schema de um database
        muda raramente, então evitar chamadas repetidas reduz latência e
        consumo de rate limit. Falha no cache nunca quebra o fluxo.

        Args:
            database_id: ID do database.

        Returns:
            A resposta JSON do database solicitado.
        """

        limpo = _validar_identificador(database_id, "database_id")

        if self._cache_ttl > 0 and limpo in self._cache_schema:
            instante, dados = self._cache_schema[limpo]
            if time.monotonic() - instante < self._cache_ttl:
                return deepcopy(dados)
            self._cache_schema.pop(limpo, None)

        resultado = self._request_json(
            method="GET",
            path=f"/databases/{limpo}",
            idempotente=True,
        )

        if self._cache_ttl > 0:
            self._cache_schema[limpo] = (time.monotonic(), deepcopy(resultado))

        return resultado

    def invalidar_cache(self, database_id: str | None = None) -> None:
        """Invalida o cache de schema.

        Args:
            database_id: ID específico para invalidar. ``None`` limpa todo
                o cache.
        """

        if database_id is None:
            self._cache_schema.clear()
        else:
            limpo = _validar_identificador(database_id, "database_id")
            self._cache_schema.pop(limpo, None)

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
        return self._request_json(
            method="POST",
            path="/databases",
            payload=payload,
            idempotente=False,
        )

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
                idempotente=True,
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
        return self._request_json(
            method="POST",
            path="/pages",
            payload=payload,
            idempotente=False,
        )

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
        return self._request_json(
            method="PATCH",
            path=f"/pages/{limpo}",
            payload=payload,
            idempotente=True,
        )

    def arquivar_pagina(self, page_id: str) -> dict[str, Any]:
        """Arquiva uma página do Notion.

        Args:
            page_id: ID da página.

        Returns:
            A resposta JSON da API.
        """

        limpo = _validar_identificador(page_id, "page_id")
        payload: PageArchivePayload = {"archived": True}
        return self._request_json(
            method="PATCH",
            path=f"/pages/{limpo}",
            payload=payload,
            idempotente=True,
        )
