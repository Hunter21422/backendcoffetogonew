# backend/settings.py

from pathlib import Path
from datetime import timedelta
import os

# =============================================================================
# БАЗОВЫЕ НАСТРОЙКИ
# =============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent

# Секретный ключ — ВСЕГДА из переменных окружения!
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("DJANGO_SECRET_KEY is not set in environment variables!")

# DEBUG — только локально!
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# В продакшене — конкретные домены!
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")

# Telegram Bot Token (обязательно из .env)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set!")

# =============================================================================
# ПРИЛОЖЕНИЯ
# =============================================================================
INSTALLED_APPS = [
    # Django core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
    "django_filters",

    # Local
    "Loyality",
]

# =============================================================================
# MIDDLEWARE
# =============================================================================
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # Всегда первым!
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    # CSRF отключён для чистого JWT API
    # "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# =============================================================================
# URLS / WSGI / ASGI
# =============================================================================
ROOT_URLCONF = "sixcoffee.urls"
WSGI_APPLICATION = "sixcoffee.wsgi.application"
ASGI_APPLICATION = "sixcoffee.asgi.application"

# =============================================================================
# БАЗА ДАННЫХ (SQLite для простоты, в проде лучше PostgreSQL)
# =============================================================================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# =============================================================================
# REST FRAMEWORK + JWT
# =============================================================================
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
    ),
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
        # BrowsableAPI только в DEBUG-режиме (чтобы не искать шаблоны в проде)
        "rest_framework.renderers.BrowsableAPIRenderer" if DEBUG else (),
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=12),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# =============================================================================
# CORS (для фронтенда)
# =============================================================================
CORS_ALLOW_ALL_ORIGINS = False

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://sixcoffee-frontend-new.vercel.app",  # ← добавь свой реальный Vercel-домен
    # Добавь другие домены по мере необходимости
]

CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS.copy()

# =============================================================================
# СТАТИКА И МЕДИА
# =============================================================================
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# =============================================================================
# ЯЗЫК И ВРЕМЯ
# =============================================================================
LANGUAGE_CODE = "ru-ru"
TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_TZ = True

# =============================================================================
# ПРОЕКТНЫЕ КОНСТАНТЫ
# =============================================================================
LOYALTY_MAX_STAMPS = 6
BARISTA_MASTER_CODE = "coffetogo555"
BARISTA_MASTER_CODES = ["coffetogo555", "coffetogo1985", "coffetogo777"]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# =============================================================================
# ПРОДАКШЕН-РЕКОМЕНДАЦИИ (раскомментируй/добавь при переходе)
# =============================================================================
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
# SECURE_BROWSER_XSS_FILTER = True
# SECURE_CONTENT_TYPE_NOSNIFF = True
# SECURE_HSTS_SECONDS = 31536000
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True
