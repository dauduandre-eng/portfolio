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

import os
from pathlib import Path

import environ
from django.contrib.messages import constants as message_constants

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

# Render sets RENDER_EXTERNAL_HOSTNAME automatically to the service's real
# onrender.com domain - appending it here means ALLOWED_HOSTS resolves
# correctly without us needing to know that domain in advance, or editing
# anything after the first deploy. A custom domain added later still needs
# adding to ALLOWED_HOSTS manually via the env var above.
RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Django 4+ checks incoming POST requests' Origin header against this list
# (in addition to ALLOWED_HOSTS) before accepting a CSRF token as valid.
# Behind Render's reverse proxy this is a real, easy-to-miss gotcha: without
# it, the contact form and chat widget — both POST endpoints — would work
# perfectly in dev and then mysteriously 403 in production.
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])
if RENDER_EXTERNAL_HOSTNAME:
    CSRF_TRUSTED_ORIGINS.append(f"https://{RENDER_EXTERNAL_HOSTNAME}")


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
    "django.contrib.sitemaps",
    "apps.users",
    "apps.core",
    "apps.projects",
    "apps.blog",
    "apps.contact",
    "apps.chat",
]

AUTH_USER_MODEL = "users.User"


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # Compresses HTML/JSON responses. Must sit near the top: middleware
    # process_response runs bottom-to-top, so placing this high means it
    # compresses the FINAL response after everything below it has already
    # run, not a half-built one. Note: GZip + a response that both reflects
    # attacker-controlled input AND carries a secret (the BREACH attack) is
    # the standard caveat here - none of our pages do that (the contact
    # form's CSRF token never appears alongside reflected user input), so
    # this is safe for this site specifically, not safe to add blindly.
    "django.middleware.gzip.GZipMiddleware",
    # WhiteNoise serves static files directly, bypassing the rest of the
    # stack for matched paths - it needs to be early, just not before GZip.
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
                "apps.chat.context_processors.chat_enabled",
                "apps.core.context_processors.canonical_url",
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
# Without this, Django opens a fresh DB connection on every single request
# and closes it at the end - real overhead under any real traffic. This
# keeps connections open and reuses them for up to 60 seconds. Harmless in
# local dev too, so there's no need to special-case it by DEBUG.
DATABASES["default"]["CONN_MAX_AGE"] = env.int("CONN_MAX_AGE", default=60)

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

# --- Email (contact form) ---
# Console backend in dev: emails print to the terminal running runserver
# instead of actually sending, so testing the contact form never needs
# real SMTP credentials. EMAIL_HOST etc. are provider-agnostic — point
# them at Gmail's SMTP (free, works immediately) or any transactional
# provider's SMTP relay (Resend, Postmark, etc.) later with zero code
# changes, just different environment variables.
EMAIL_BACKEND = (
    "django.core.mail.backends.console.EmailBackend"
    if DEBUG
    else "django.core.mail.backends.smtp.EmailBackend"
)
EMAIL_HOST = env("EMAIL_HOST", default="")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="webmaster@localhost")
# Where contact form submissions actually get sent. Defaults to
# DEFAULT_FROM_EMAIL so the site works out of the box, but can be a
# different address if you ever want submissions routed elsewhere.
CONTACT_RECIPIENT_EMAIL = env("CONTACT_RECIPIENT_EMAIL", default=DEFAULT_FROM_EMAIL)

# --- AI chat widget ---
# CHAT_ENABLED is derived, not set directly: unset ANTHROPIC_API_KEY in
# any environment and the widget disappears from every page with zero
# code changes - exactly the "can be disabled without touching anything
# else" isolation this app was designed around back in Milestone 0.
ANTHROPIC_API_KEY = env("ANTHROPIC_API_KEY", default="")
CHAT_MODEL = env("CHAT_MODEL", default="claude-haiku-4-5-20251001")
CHAT_ENABLED = bool(ANTHROPIC_API_KEY)

# Django's default tag for an ERROR-level message is "error", but
# Bootstrap's alert class is "alert-danger" — without this mapping,
# an error-level message would silently render as an unstyled,
# un-colored alert. We don't use messages.error() yet, but this is the
# kind of mismatch that's invisible until the day someone adds one.
MESSAGE_TAGS = {
    message_constants.ERROR: "danger",
}

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
    # Render's own internal health-check prober may hit this path directly
    # rather than through the same edge that sets X-Forwarded-Proto for
    # real visitor traffic - undocumented platform internals aren't worth
    # betting the deploy's health status on. Exempting it guarantees a 200
    # regardless, on a path no actual visitor ever sees anyway.
    SECURE_REDIRECT_EXEMPT = [r"^healthz/$"]
