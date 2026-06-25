"""Views da borda HTTP — finas: parse, validação e delegação a ``services``.

Sem regra de negócio aqui (isso vive em ``services``) nem formato cru do Notion
(isso é do ``notion_starter``). O contrato das rotas segue o esboço da Fase 2 em
``docs/PLANO.md`` — alinhar a ``docs/CONTRATOS.md`` quando o Agente 0 publicá-lo:

    GET   /api/tarefas[?status=<nome>]   lista (filtro opcional por status)
    POST  /api/tarefas                   cria  {nome, status?, prazo?}        -> 201
    PATCH /api/tarefas/<id>              move status {status}                 -> 200

Saída em JSON. Erros mapeados: 400 (entrada inválida), 502 (falha na API do
Notion), 503 (servidor sem token/database configurado).
"""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from services import tarefas as svc

from notion_starter import NotionAPIError, NotionConfigurationError, NotionHTTPError

from .serializers import tarefa_para_dict


def health(_request: HttpRequest) -> JsonResponse:
    """Sinaliza que o servidor está de pé. Não toca no Notion."""

    return JsonResponse({"status": "ok", "service": "automacoes-notion"})


def _erro(codigo: str, mensagem: str, status: int) -> JsonResponse:
    """Monta o envelope de erro padrão (``docs/CONTRATOS.md`` §3)."""

    return JsonResponse({"erro": {"codigo": codigo, "mensagem": mensagem}}, status=status)


def _corpo_json(request: HttpRequest) -> dict[str, Any]:
    """Lê o corpo da requisição como objeto JSON (``ValueError`` se inválido)."""

    dados = json.loads(request.body.decode("utf-8") or "{}")
    if not isinstance(dados, dict):
        raise ValueError("o corpo deve ser um objeto JSON")
    return dados


def _responder(acao: Callable[[], JsonResponse]) -> JsonResponse:
    """Executa um caso de uso e mapeia exceções para o envelope de erro do contrato.

    Mensagens são genéricas de propósito: nunca vazam token, ID interno ou caminho
    local (guarda-corpo de ``docs/CONTRATOS.md`` §3).
    """

    try:
        return acao()
    except (json.JSONDecodeError, ValueError) as exc:
        return _erro("validacao", f"Requisição inválida: {exc}", 400)
    except NotionHTTPError as exc:
        if exc.status_code == 404:
            return _erro("nao_encontrado", "Tarefa não encontrada.", 404)
        return _erro("erro_upstream", "Falha ao falar com o Notion.", 502)
    except NotionAPIError:
        return _erro("erro_upstream", "Falha ao falar com o Notion.", 502)
    except (NotionConfigurationError, ImproperlyConfigured):
        return _erro("erro_interno", "Servidor não configurado corretamente.", 500)
    except Exception:  # noqa: BLE001 - contrato: qualquer outra falha vira 500 erro_interno
        return _erro("erro_interno", "Erro interno inesperado.", 500)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def tarefas(request: HttpRequest) -> JsonResponse:
    """Lista (``GET``) ou cria (``POST``) tarefas."""

    if request.method == "GET":

        def _listar() -> JsonResponse:
            itens = svc.listar_tarefas(status=request.GET.get("status") or None)
            return JsonResponse({"tarefas": [tarefa_para_dict(t) for t in itens]})

        return _responder(_listar)

    def _criar() -> JsonResponse:
        dados = _corpo_json(request)
        nome = (dados.get("nome") or "").strip()
        if not nome:
            raise ValueError("'nome' é obrigatório")
        tarefa = svc.criar_tarefa(
            nome,
            status=dados.get("status") or None,
            prazo=dados.get("prazo") or None,
        )
        return JsonResponse(tarefa_para_dict(tarefa), status=201)

    return _responder(_criar)


@csrf_exempt
@require_http_methods(["PATCH"])
def tarefa_detalhe(request: HttpRequest, task_id: str) -> JsonResponse:
    """Move o status de uma tarefa existente (``PATCH``)."""

    def _mover() -> JsonResponse:
        dados = _corpo_json(request)
        status = (dados.get("status") or "").strip()
        if not status:
            raise ValueError("'status' é obrigatório")
        tarefa = svc.mover_status(task_id, status)
        return JsonResponse(tarefa_para_dict(tarefa))

    return _responder(_mover)
