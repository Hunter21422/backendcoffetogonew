# backend/settings.py — финальная версия для Render + PostgreSQL (январь 2026)

from pathlib import Path
from datetime import timedelta
import os
import dj_database_url  # ← обязательно для PostgreSQL на Render

# =============================================================================
# БАЗОВЫЕ НАСТРОЙКИ
# =============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent

# Секретный ключ — ОБЯЗАТЕЛЬНО из переменных окружения Render!
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("DJANGO_SECRET_KEY is not set in environment variables!")

# DEBUG — False в продакшене (Render добавит DEBUG=False)
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")

# Хосты — из env или wildcard (в проде укажи конкретные)
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")

# Telegram Bot Token — обязательно из env
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set in environment variables!")

# =============================================================================
# ПРИЛОЖЕНИЯ
# =============================================================================
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
    "django_filters",

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
    # CSRF отключён для чистого JWT API (если нужен — раскомментируй)
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
# БАЗА ДАННЫХ — PostgreSQL на Render (автоматически берёт DATABASE_URL)
# =============================================================================
DATABASES = {
    "default": dj_database_url.config(
        default="sqlite:///db.sqlite3",  # fallback для локальной разработки
        conn_max_age=600,
    )
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
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ] + (
        ["rest_framework.renderers.BrowsableAPIRenderer"] if DEBUG else []
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
# CORS — для фронтенда (Vercel + localhost)
# =============================================================================
CORS_ALLOW_ALL_ORIGINS = False

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://sixcoffee-frontend-new.vercel.app",  # ← твой реальный Vercel-домен
    "https://*.vercel.app",  # ← для preview-веток и всех доменов Vercel
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["GET", "POST", "PATCH", "DELETE", "OPTIONS", "HEAD"]
CORS_ALLOW_HEADERS = ["*"]  # ← разрешаем все заголовки (временно для отладки)

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
# ПРОДАКШЕН-НАСТРОЙКИ (раскомментируй после тестов)
# =============================================================================
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
# SECURE_BROWSER_XSS_FILTER = True
# SECURE_CONTENT_TYPE_NOSNIFF = True
# SECURE_HSTS_SECONDS = 31536000  # 1 год
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True
