"""
Django settings for TUMOMITO ERP project.

En desarrollo: lee de .env (DEBUG=True, SQLite)
En produccion (Render): lee de variables de entorno (DEBUG=False, PostgreSQL)
"""
import os
from pathlib import Path
from decouple import config, Csv
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# ============================================================
# SEGURIDAD
# ============================================================
SECRET_KEY = config(
    'SECRET_KEY',
    default='django-insecure-cambiar-en-produccion-tumomito-erp-2026'
)
DEBUG = config('DEBUG', default=True, cast=bool)

# En produccion: ALLOWED_HOSTS=tumomito-erp.onrender.com,tudominio.com
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='*', cast=Csv())

# Render asigna automaticamente este header
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Para que CSRF funcione bien en Render
CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='https://*.onrender.com',
    cast=Csv()
)

# ============================================================
# APLICACIONES
# ============================================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # Third party
    'crispy_forms',
    'crispy_bootstrap5',

    # Apps locales
    'apps.core',
    'apps.personal',
    'apps.clientes',
    'apps.proveedores',
    'apps.inventario',
    'apps.compras',
    'apps.ventas',
    'apps.dashboard',
    'apps.tienda',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise sirve los static files en produccion (debe ir despues de Security)
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.personal.middleware.BitacoraMiddleware',
]

ROOT_URLCONF = 'tumomito.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.dashboard.context_processors.empresa_info',
                'apps.personal.context_processors.usuario_perfil',
            ],
        },
    },
]

WSGI_APPLICATION = 'tumomito.wsgi.application'

# ============================================================
# BASE DE DATOS
# ============================================================
# En desarrollo (sin DATABASE_URL): SQLite local
# En Render (con DATABASE_URL): PostgreSQL automatico
DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# ============================================================
# AUTENTICACION
# ============================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ============================================================
# INTERNACIONALIZACION
# ============================================================
LANGUAGE_CODE = 'es-bo'
TIME_ZONE = 'America/La_Paz'
USE_I18N = True
USE_TZ = True

# ============================================================
# ARCHIVOS ESTATICOS Y MEDIA
# ============================================================
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise: comprime y agrega cache headers a los static files
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================================
# CRISPY FORMS
# ============================================================
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# ============================================================
# LOGIN
# ============================================================
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard:home'
LOGOUT_REDIRECT_URL = 'login'

# ============================================================
# MENSAJES BOOTSTRAP
# ============================================================
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG: 'secondary',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

# ============================================================
# SEGURIDAD HTTPS (solo en produccion)
# ============================================================
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
    SECURE_HSTS_SECONDS = 31536000  # 1 ano
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
