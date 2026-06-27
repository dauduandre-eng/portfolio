"""
ASGI config for the portfolio project.

Not used in production yet (gunicorn + WSGI is simpler and sufficient for
v1). Kept here because the future `chat` app may benefit from async views
when streaming AI responses — having this in place now means adopting
ASGI later is a config change, not a restructure.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_asgi_application()
