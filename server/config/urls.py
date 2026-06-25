"""Roteamento raiz do servidor.

Delega ``/api/`` para o app ``api`` (borda HTTP). O front (templates servidos pelo
Django) será montado aqui pelo Agente Front-end quando existir.
"""

from __future__ import annotations

from django.urls import include, path

urlpatterns = [
    path("api/", include("api.urls")),
]
