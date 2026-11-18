from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-this-secret-key")
DEBUG = os.getenv("DEBUG", "True").lower() in {"1", "true", "yes", "on"}
ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",") if h.strip()]
CSRF_TRUSTED_ORIGINS = [h.strip() for h in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if h.strip()]

INSTALLED_APPS = [
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
    "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
    "cpa.apps.CpaConfig",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware", "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware", "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware", "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware", "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "config.urls"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"], "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.debug", "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth", "django.contrib.messages.context_processors.messages",
    ]},
}]
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"
DATABASES = {"default": dj_database_url.config(default=os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'db.sqlite3'}"), conn_max_age=600)}
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
LANGUAGE_CODE = "pt-br"
TIME_ZONE = os.getenv("TIME_ZONE", "America/Sao_Paulo")
USE_I18N = True
USE_TZ = True
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_BACKEND = "whitenoise.storage.CompressedManifestStaticFilesStorage" if not DEBUG else "whitenoise.storage.CompressedStaticFilesStorage"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": STATIC_BACKEND},
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "cpa:dashboard"
LOGOUT_REDIRECT_URL = "login"

# O pacote independente oferece cadastro próprio; no projeto principal, deixe False.
CPA_ENABLE_REGISTRATION = True
