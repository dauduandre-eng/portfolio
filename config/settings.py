"""
Django settings for the portfolio project.

Design decision: this is the SAME settings.py in dev, staging, and prod.
There is no settings/dev.py vs settings/prod.py split. Every value that
changes between environments (secrets, debug flag, allowed hosts, the
database) is read from an environment variable instead. This is the
Twelve-Factor App approach: https://12factor.net/config

Why this over split settings files: split files duplicate the 80% of
settings that don't change between environments, and that duplication is
exactly how "works in staging, breaks in prod" bugs creep in (someone
updates settings/dev.py and forgets settings/prod.py). A single file with
env-var driven values means there is only one place to look, ever.

Locally, values come from a .env file (gitignored, never committed).
In production, Render injects these as real environment variables — no
.env file exists there, and none is needed.
"""

from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False),  # secure-by-default: you must opt INTO debug mode
)

# Only read a .env file if one exists. In production there isn't one —
# Render (or any other host) sets real environment variables directly.
_env_file = BASE_DIR / ".env"
if _env_file.exists():
    environ.Env.read_env(_env_file)

# No default value here on purpose: if SECRET_KEY is missing, the app
# should crash immediately on startup rather than silently run insecurely.
SECRET_KEY = env("SECRET_KEY")

DEBUG = env("DEBUG")

# No default here either: if ALLOWED_HOSTS is empty and DEBUG=False,
# Django will reject every request with a 400. That's intentional —
# it forces you to explicitly decide which hosts can serve this app
# before it's reachable in production, rather than discovering a
# misconfiguration from a security scanner.
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])


# Application definition
# Custom apps live under apps/ to keep the project root clean as we add
# core, projects, blog, and chat in upcoming milestones.
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.users",
    "apps.core",
    "apps.projects",
]

AUTH_USER_MODEL = "users.User"


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # WhiteNoise must sit directly after SecurityMiddleware so it can serve
    # static files in production without a separate Nginx/CDN layer.
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # Project-level templates (base.html, shared layout) live here.
        # Populated in Milestone 2 — empty for now besides a .gitkeep.
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# env.db() parses a DATABASE_URL string (e.g. postgres://user:pass@host:port/name)
# into the dict Django's DATABASES setting expects. Render's managed Postgres
# add-on hands you exactly this kind of URL, so this line is also what makes
# "connect to the production database" a zero-code-change operation.
DATABASES = {
    "default": env.db("DATABASE_URL"),
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation."
        "UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
# Where Django (and `collectstatic`) looks for OUR static source files in
# addition to each app's own static/ directory. Distinct from STATIC_ROOT
# below, which is the build OUTPUT — never edit files there by hand.
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
# Manifest + compression is a PRODUCTION-only optimization. It requires
# `collectstatic` to have already built a manifest file before any page
# can resolve a {% static %} tag — if we used it in dev too, that would
# make running tests or `runserver` silently depend on a build step
# happening first, which is a fragile thing to require. In dev, Django's
# plain staticfiles storage needs no manifest and just works.
if DEBUG:
    STORAGES = {
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    }
else:
    STORAGES = {
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
        },
    }

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# --- Production security hardening ---
# These only activate when DEBUG=False, so local development is unaffected.
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 7  # 1 week; raise once this is proven stable
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    # Render terminates TLS at its edge and forwards plain HTTP internally,
    # using this header to tell Django the original request was HTTPS.
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
