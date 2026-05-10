"""
Django settings for devsec_demo.

Environment variables
---------------------
Required
  DJANGO_SECRET_KEY       Long random string for cryptographic signing.
                          Generate: python -c "from django.core.management.utils
                          import get_random_secret_key; print(get_random_secret_key())"

Optional (safe defaults shown)
  DJANGO_DEBUG            'true' / '1' / 'yes' to enable debug mode.
                          Default: False  ← production-safe; opt IN to debug, not out.
  DJANGO_ALLOWED_HOSTS    Comma-separated hostnames Django will serve.
                          Default: 127.0.0.1,localhost
  DJANGO_EMAIL_BACKEND    Dotted path to email backend class.
                          Default: django.core.mail.backends.console.EmailBackend
  DJANGO_BEHIND_PROXY     'true' to trust X-Forwarded-Proto from a reverse proxy.
                          Never set unless a trusted proxy terminates TLS in front
                          of Django.
  DJANGO_SESSION_COOKIE_AGE
                          Session lifetime in seconds.
                          Default: 3600 (1 hour)

Copy .env.example to .env for local development.  Never commit .env.
"""

import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


# ------------------------------------------------------------------ #
# Environment-variable helpers
# ------------------------------------------------------------------ #

def _env_bool(name, *, default=False):
    """Parse a boolean environment variable.

    Truthy values: '1', 'true', 'yes' (case-insensitive).
    Anything else — including an absent variable — returns *default*.

    The built-in default is False so that leaving a variable unset is
    always the safe production choice (opt IN to permissive behaviour,
    never opt OUT of it).
    """
    val = os.environ.get(name, '').strip()
    if not val:
        return default
    return val.lower() in ('1', 'true', 'yes')


def _env_int(name, *, default):
    """Parse an integer environment variable.

    Returns *default* when the variable is absent or empty.
    Raises ImproperlyConfigured when the value is not a valid integer.
    """
    val = os.environ.get(name, '').strip()
    if not val:
        return default
    try:
        return int(val)
    except ValueError:
        raise ImproperlyConfigured(
            f"Environment variable {name!r} must be an integer, got {val!r}."
        )


# ------------------------------------------------------------------ #
# Secret key — required; startup fails loudly if absent or empty
# ------------------------------------------------------------------ #

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', '').strip()
if not SECRET_KEY:
    raise ImproperlyConfigured(
        "The DJANGO_SECRET_KEY environment variable is not set or is empty.\n"
        "Generate a suitable value with:\n"
        "  python -c \"from django.core.management.utils import "
        "get_random_secret_key; print(get_random_secret_key())\"\n"
        "Then add DJANGO_SECRET_KEY=<value> to your .env file or "
        "deployment environment before starting."
    )


# ------------------------------------------------------------------ #
# Core operational settings
# ------------------------------------------------------------------ #

# Default is False — omitting the variable in production is the SAFE path.
# Set DJANGO_DEBUG=true only in local development.
DEBUG = _env_bool('DJANGO_DEBUG', default=False)

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get('DJANGO_ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')
    if host.strip()
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apophia',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'apophia.middleware.ContentSecurityPolicyMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'devsec_demo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'devsec_demo.wsgi.application'


# ------------------------------------------------------------------ #
# Database
# ------------------------------------------------------------------ #

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ------------------------------------------------------------------ #
# Password validation
# ------------------------------------------------------------------ #

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ------------------------------------------------------------------ #
# Internationalisation
# ------------------------------------------------------------------ #

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# ------------------------------------------------------------------ #
# Static and media files
# ------------------------------------------------------------------ #

STATIC_URL = 'static/'

# Public uploads (avatars only). Serve via reverse-proxy in production.
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Private uploads (documents) — never exposed under MEDIA_URL.
PRIVATE_STORAGE_ROOT = BASE_DIR / 'private'

# Global upload guard; per-field limits in uploads.py are stricter.
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024   # 10 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024   # 10 MB


# ------------------------------------------------------------------ #
# Auth redirect targets
# ------------------------------------------------------------------ #

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'


# ------------------------------------------------------------------ #
# Email
# ------------------------------------------------------------------ #

# Default: console backend (safe for development — no real emails sent).
# Production: set DJANGO_EMAIL_BACKEND to an SMTP backend, e.g.
#   django.core.mail.backends.smtp.EmailBackend
EMAIL_BACKEND = os.environ.get(
    'DJANGO_EMAIL_BACKEND',
    'django.core.mail.backends.console.EmailBackend',
)


# ------------------------------------------------------------------ #
# Session and authentication timeouts
# ------------------------------------------------------------------ #

# 1 hour — short sessions limit the damage if a session token is stolen.
# Raise via DJANGO_SESSION_COOKIE_AGE for applications that need longer.
SESSION_COOKIE_AGE = _env_int('DJANGO_SESSION_COOKIE_AGE', default=3600)

# Password-reset links expire after 24 hours (Django default is 3 days).
PASSWORD_RESET_TIMEOUT = 86400  # seconds


# ------------------------------------------------------------------ #
# Security headers — applied in both development and production
# ------------------------------------------------------------------ #

SECURE_CONTENT_TYPE_NOSNIFF = True          # X-Content-Type-Options: nosniff
X_FRAME_OPTIONS = 'DENY'                    # X-Frame-Options: DENY
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin'

# HttpOnly prevents JavaScript from reading session / CSRF tokens.
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# SameSite=Lax blocks cookies on cross-site POST (primary CSRF vector)
# while still allowing cookies after a cross-site GET (link navigation).
# Explicit here rather than relying on the Django version-specific default.
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'


# ------------------------------------------------------------------ #
# Reverse-proxy TLS termination (opt-in)
# ------------------------------------------------------------------ #

# Enable only when a trusted reverse proxy (nginx, Caddy, …) terminates
# TLS and forwards the X-Forwarded-Proto header.  Setting this when
# Django is directly internet-facing over HTTP is a security risk.
if _env_bool('DJANGO_BEHIND_PROXY'):
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# ------------------------------------------------------------------ #
# Production-only transport security
# Activated whenever DEBUG is False (i.e. DJANGO_DEBUG is absent or
# set to a falsy value — which is the safe default).
# ------------------------------------------------------------------ #

if not DEBUG:
    # Redirect plain-HTTP requests to HTTPS.
    SECURE_SSL_REDIRECT = True

    # HSTS: tell browsers to use HTTPS for the next year, for this
    # domain and all subdomains.  Add to the preload list once confirmed.
    SECURE_HSTS_SECONDS = 31536000          # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # Mark cookies as Secure so browsers only send them over HTTPS.
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True


# ------------------------------------------------------------------ #
# Audit logging
# ------------------------------------------------------------------ #

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'audit': {
            'format': '{asctime} {levelname} {name} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'audit_console': {
            'class': 'logging.StreamHandler',
            'formatter': 'audit',
        },
    },
    'loggers': {
        'apophia.audit': {
            'handlers': ['audit_console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
