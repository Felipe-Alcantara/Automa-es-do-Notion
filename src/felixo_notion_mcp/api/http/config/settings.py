"""Settings do Django — finos, lendo tudo de ``core.config`` (ambiente).

Sem segredo hardcoded: ``SECRET_KEY``, ``DEBUG``, hosts e o token do Notion vêm do
ambiente / ``.env``. Banco SQLite só para **estado operacional** (jobs, locks); a
fonte da verdade do conteúdo continua sendo o Notion.
"""

from __future__ import annotations

from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

from felixo_notion_mcp.core.config import SECRET_KEY_DEV, carregar_config

# Pasta da borda HTTP (``api/http``): onde moram ``templates``, ``static`` e ``staticfiles``.
BASE_DIR = Path(__file__).resolve().parent.parent

_cfg = carregar_config()

SECRET_KEY = _cfg.secret_key
DEBUG = _cfg.debug
ALLOWED_HOSTS = _cfg.allowed_hosts

# Em produção a SECRET_KEY de desenvolvimento é inaceitável.
if not DEBUG and SECRET_KEY == SECRET_KEY_DEV:
    raise ImproperlyConfigured(
        "Defina DJANGO_SECRET_KEY no ambiente para rodar com DEBUG desligado."
    )

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
    # Apps do servidor (camadas). Os nomes são os módulos; os rótulos (``operations`` e
    # ``api``) vêm do ``label`` de cada ``AppConfig`` e mantêm tabelas e migrações.
    "felixo_notion_mcp.repositories.operations",  # estado operacional (jobs/locks) em SQLite
    "felixo_notion_mcp.api.http.rest",  # borda HTTP (rotas REST)
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "felixo_notion_mcp.api.http.config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # front (Agente Front-end) mora aqui
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": []},
    },
]

WSGI_APPLICATION = "felixo_notion_mcp.api.http.config.wsgi.application"
ASGI_APPLICATION = "felixo_notion_mcp.api.http.config.asgi.application"

# SQLite só para estado operacional. O caminho vem do ambiente (OPERATIONAL_DB_PATH).
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(_cfg.database_path),
    }
}

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"] if (BASE_DIR / "static").exists() else []

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
