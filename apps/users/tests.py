from django.contrib.auth import get_user_model
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
