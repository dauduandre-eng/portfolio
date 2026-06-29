import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Creates a superuser from DJANGO_SUPERUSER_USERNAME/EMAIL/PASSWORD env
    vars, but only if no superuser exists yet. Safe to run on every single
    deploy, forever - once a superuser exists, this is a no-op.

    Why this exists: Render's free tier doesn't include shell access, so
    `python manage.py createsuperuser` (which needs an interactive
    terminal) isn't available the way it is on your own machine. This is
    the standard workaround for any shell-less deploy target, not a hack
    specific to this project.
    """

    help = (
        "Creates a superuser from DJANGO_SUPERUSER_* env vars if none "
        "exists yet. Skips silently if a superuser already exists."
    )

    def handle(self, *args, **options):
        User = get_user_model()

        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write("A superuser already exists - skipping.")
            return

        username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

        if not all([username, email, password]):
            self.stdout.write(
                self.style.WARNING(
                    "DJANGO_SUPERUSER_USERNAME/EMAIL/PASSWORD aren't all "
                    "set - skipping superuser creation."
                )
            )
            return

        User.objects.create_superuser(
            username=username, email=email, password=password
        )
        self.stdout.write(self.style.SUCCESS(f"Created superuser '{username}'."))
