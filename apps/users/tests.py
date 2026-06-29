import os
from io import StringIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

from .models import User


class CustomUserModelTests(TestCase):
    def test_auth_user_model_points_to_our_custom_model(self):
        """
        get_user_model() is what every other app should use to reference
        the user model (never import User directly) — so confirming it
        resolves to our model is the test that actually matters here.
        """
        self.assertIs(get_user_model(), User)

    def test_can_create_a_user(self):
        user = User.objects.create_user(
            username="andrew", password="a-sufficiently-strong-password"
        )

        self.assertTrue(user.check_password("a-sufficiently-strong-password"))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)


class EnsureSuperuserCommandTests(TestCase):
    @patch.dict(
        os.environ,
        {
            "DJANGO_SUPERUSER_USERNAME": "andrew",
            "DJANGO_SUPERUSER_EMAIL": "andrew@example.com",
            "DJANGO_SUPERUSER_PASSWORD": "a-sufficiently-strong-password",
        },
    )
    def test_creates_superuser_from_env_vars_when_none_exists(self):
        call_command("ensure_superuser", stdout=StringIO())

        self.assertTrue(
            User.objects.filter(username="andrew", is_superuser=True).exists()
        )

    @patch.dict(os.environ, {}, clear=True)
    def test_skips_silently_when_env_vars_are_missing(self):
        """
        This is the case that matters most in practice: every deploy after
        the first one, once a superuser already exists - covered by the
        next test - but this confirms it doesn't crash the build if the
        vars were never set at all either.
        """
        call_command("ensure_superuser", stdout=StringIO())

        self.assertEqual(User.objects.count(), 0)

    @patch.dict(
        os.environ,
        {
            "DJANGO_SUPERUSER_USERNAME": "someone-else",
            "DJANGO_SUPERUSER_EMAIL": "someone-else@example.com",
            "DJANGO_SUPERUSER_PASSWORD": "a-sufficiently-strong-password",
        },
    )
    def test_skips_when_a_superuser_already_exists(self):
        """
        The actual safety property this command depends on: re-running it
        on every single deploy, forever, must never create a second
        superuser or touch the existing one.
        """
        User.objects.create_superuser(
            username="andrew", email="andrew@example.com", password="x"
        )

        call_command("ensure_superuser", stdout=StringIO())

        self.assertEqual(User.objects.filter(is_superuser=True).count(), 1)
        self.assertFalse(User.objects.filter(username="someone-else").exists())
