# backend/settings.py — финальная версия с AUTH_USER_MODEL

from pathlib import Path
from datetime import timedelta
import os
import dj_database_url

# =============================================================================
# БАЗОВЫЕ НАСТРОЙКИ
# =============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent

# Секретный ключ
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    SECRET_KEY = "q48ugk5tqgv9sw(uoo(=lw6cd85ztme*4vq_bo6x6j$2g1+nv-"

    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║ ВНИМАНИЕ: DJANGO_SECRET_KEY НЕ НАЙДЕН В ПЕРЕМЕННЫХ ОКРУЖЕНИЯ!      ║")
    print("║ Используется ВРЕМЕННЫЙ НЕБЕЗОПАСНЫЙ ключ ТОЛЬКО для локальной разработки ║")
    print("║ На Render / продакшене ОБЯЗАТЕЛЬНО задай настоящий секретный ключ! ║")
    print("╚════════════════════════════════════════════════════════════════════╝")

# DEBUG
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# Хосты
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1,[::1],*.onrender.com").split(",")

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN and not DEBUG:
    print("WARNING: TELEGRAM_BOT_TOKEN не задан → Telegram-функции работать не будут")

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
    
    "Loyality.apps.LoyalityConfig",
    
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
]

# САМОЕ ВАЖНОЕ — КАСТОМНАЯ МОДЕЛЬ ПОЛЬЗОВАТЕЛЯ
AUTH_USER_MODEL = 'Loyality.User'   # ← ЭТУ СТРОКУ ДОБАВЬ ОБЯЗАТЕЛЬНО!

# =============================================================================
# TEMPLATES — обязательно для админки
# =============================================================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# =============================================================================
# MIDDLEWARE
# =============================================================================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# =============================================================================
# REST FRAMEWORK + JWT
# =============================================================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

# =============================================================================
# CORS
# =============================================================================
CORS_ALLOW_ALL_ORIGINS = DEBUG
if not DEBUG:
    CORS_ALLOWED_ORIGINS = [
        "https://sixcoffee-frontend-new.vercel.app",
        "https://*.vercel.app",
    ]
    CSRF_TRUSTED_ORIGINS = [
        "https://sixcoffee-frontend-new.vercel.app",
        "https://*.vercel.app",
    ]

# =============================================================================
# БАЗА ДАННЫХ
# =============================================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# На Render будет переопределяться через DATABASE_URL
if "DATABASE_URL" in os.environ:
    DATABASES['default'] = dj_database_url.config(conn_max_age=600)
else:
    print("INFO: Используется локальная SQLite база (db.sqlite3)")

# =============================================================================
# СТАТИКА И МЕДИА
# =============================================================================
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

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
