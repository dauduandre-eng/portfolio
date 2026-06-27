"""
WSGI config for the portfolio project.

This is the entry point synchronous servers (gunicorn, in our case) use to
talk to Django. Every request that reaches the deployed app passes through
the `application` callable defined here.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_wsgi_application()
