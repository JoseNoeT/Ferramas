"""Minimal Django settings scaffold for FERREMAX backend."""

import os
from pathlib import Path

try:
	from decouple import config
except ModuleNotFoundError:
	def config(key, default=None, cast=str):
		value = os.getenv(key, default)
		if cast is bool:
			if isinstance(value, bool):
				return value
			return str(value).lower() in {"1", "true", "yes", "on"}
		return cast(value) if value is not None else value

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("DJANGO_SECRET_KEY", default="change-me-in-development")
DEBUG = config(
	"DEBUG",
	default=config("DJANGO_DEBUG", default=True, cast=bool),
	cast=bool,
)
ALLOWED_HOSTS = config(
	"ALLOWED_HOSTS",
	default=config("DJANGO_ALLOWED_HOSTS", default="127.0.0.1,localhost"),
	cast=lambda v: [s.strip() for s in v.split(",") if s.strip()],
)

INSTALLED_APPS = [
	"django.contrib.admin",
	"django.contrib.auth",
	"django.contrib.contenttypes",
	"django.contrib.sessions",
	"django.contrib.messages",
	"django.contrib.staticfiles",
	"rest_framework",
	"corsheaders",
	"apps.usuarios.apps.UsuariosConfig",
	"apps.catalogo.apps.CatalogoConfig",
	"apps.inventario.apps.InventarioConfig",
	"apps.pagos.apps.PagosConfig",
	"apps.pedidos.apps.PedidosConfig",
	"apps.reportes.apps.ReportesConfig",
	"apps.autenticacion.apps.AutenticacionConfig",
	"apps.credito.apps.CreditoConfig",
	"apps.puntos.apps.PuntosConfig",
	"apps.maestros.apps.MaestrosConfig",
	"apps.encuestas.apps.EncuestasConfig",
	"apps.notificaciones.apps.NotificacionesConfig",
	"apps.integraciones.apps.IntegracionesConfig",
]

MIDDLEWARE = [
	"django.middleware.security.SecurityMiddleware",
	"corsheaders.middleware.CorsMiddleware",
	"django.contrib.sessions.middleware.SessionMiddleware",
	"django.middleware.common.CommonMiddleware",
	"django.middleware.csrf.CsrfViewMiddleware",
	"django.contrib.auth.middleware.AuthenticationMiddleware",
	"django.contrib.messages.middleware.MessageMiddleware",
	"django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
	{
		"BACKEND": "django.template.backends.django.DjangoTemplates",
		"DIRS": [BASE_DIR.parent / "frontend" / "templates"],
		"APP_DIRS": True,
		"OPTIONS": {
			"context_processors": [
				"django.template.context_processors.debug",
				"django.template.context_processors.request",
				"django.contrib.auth.context_processors.auth",
				"django.contrib.messages.context_processors.messages",
				"apps.pedidos.context_processors.carrito_context",
			],
		},
	},
]

WSGI_APPLICATION = "core.wsgi.application"
ASGI_APPLICATION = "core.asgi.application"

SQLITE_PATH = config("SQLITE_PATH", default=str(BASE_DIR / "db.sqlite3"))

DATABASES = {
	"default": {
		"ENGINE": "django.db.backends.sqlite3",
		"NAME": SQLITE_PATH,
	}
}

LANGUAGE_CODE = "es-cl"
TIME_ZONE = "America/Santiago"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR.parent / "frontend" / "static"]

CSRF_TRUSTED_ORIGINS = config(
	"CSRF_TRUSTED_ORIGINS",
	default="",
	cast=lambda v: [s.strip() for s in v.split(",") if s.strip()],
)

# CORS basico para desarrollo local.
CORS_ALLOW_ALL_ORIGINS = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Autenticacion
AUTH_USER_MODEL = "usuarios.Usuario"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"
LOGIN_URL = "/login/"

# API REST base (logica avanzada pendiente por endpoint).
REST_FRAMEWORK = {
	"DEFAULT_AUTHENTICATION_CLASSES": (
		"rest_framework_simplejwt.authentication.JWTAuthentication",
	),
	"DEFAULT_PERMISSION_CLASSES": (
		"rest_framework.permissions.AllowAny",
	),
}

# TODO: Ajustar expiraciones y politicas en fase de seguridad.
SIMPLE_JWT = {
	"AUTH_HEADER_TYPES": ("Bearer",),
}

# Transbank Webpay Plus
TRANSBANK_ENVIRONMENT = config("TRANSBANK_ENVIRONMENT", default="integration").lower()
TRANSBANK_COMMERCE_CODE = config(
	"TRANSBANK_COMMERCE_CODE",
	default="597055555532",
)
TRANSBANK_API_KEY = config(
	"TRANSBANK_API_KEY",
	default="579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C",
)

