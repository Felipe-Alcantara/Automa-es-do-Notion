"""Testes de integração do front servido pelo Django.

Valida a fiação da rota raiz, os assets e os elementos essenciais do fluxo sem
depender de rede, token do Notion ou execução de JavaScript no navegador.
"""

from __future__ import annotations

import os

import pytest

pytest.importorskip("django")

os.environ.setdefault("DJANGO_DEBUG", "1")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django  # noqa: E402
from django.contrib.staticfiles import finders  # noqa: E402
from django.test import Client  # noqa: E402
from django.urls import reverse  # noqa: E402

django.setup()


def test_home_serve_template_do_front():
    resposta = Client().get(reverse("home"))

    assert resposta.status_code == 200
    conteudo = resposta.content.decode()
    assert "Automações do Notion" in conteudo
    assert 'id="lista-tarefas"' in conteudo
    assert 'id="form-tarefa"' in conteudo
    assert 'role="dialog"' in conteudo
    assert 'aria-live="polite"' in conteudo


@pytest.mark.parametrize("asset", ["css/app.css", "js/app.js"])
def test_assets_do_front_sao_encontrados(asset):
    assert finders.find(asset) is not None


def test_css_preserva_elementos_ocultos():
    caminho = finders.find("css/app.css")

    assert caminho is not None
    assert "[hidden]" in open(caminho, encoding="utf-8").read()
