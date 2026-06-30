from unittest.mock import MagicMock, patch

from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import ContactMessage


@override_settings(
    RESEND_API_KEY="test-key", DEFAULT_FROM_EMAIL="onboarding@resend.dev"
)
class ContactViewTests(TestCase):
    def setUp(self):
        # The rate-limit cache key is per client IP, and Django's test
        # client always uses the same fake IP for every request. Without
        # clearing the cache here, an earlier test's submissions would
        # count against this test's rate limit too.
        cache.clear()

    def _post(self, **overrides):
        data = {
            "name": "Jamie Recruiter",
            "email": "jamie@example.com",
            "message": "Are you open to contract work?",
            "website": "",
        }
        data.update(overrides)
        return self.client.post(reverse("contact:contact"), data)

    @patch("apps.contact.views.requests.post")
    def test_valid_submission_saves_message_and_calls_resend(self, mock_post):
        mock_post.return_value = MagicMock(status_code=200)

        response = self._post()

        self.assertRedirects(response, reverse("contact:contact"))
        self.assertEqual(ContactMessage.objects.count(), 1)
        mock_post.assert_called_once()

        call_kwargs = mock_post.call_args.kwargs
        self.assertEqual(call_kwargs["json"]["reply_to"], "jamie@example.com")
        self.assertIn("timeout", call_kwargs)

    @patch("apps.contact.views.requests.post")
    def test_honeypot_filled_pretends_success_and_never_calls_resend(self, mock_post):
        response = self._post(
            name="Bot", email="bot@example.com", website="http://spam.example"
        )

        self.assertRedirects(response, reverse("contact:contact"))
        self.assertEqual(ContactMessage.objects.count(), 0)
        mock_post.assert_not_called()

    def test_invalid_email_reshows_form_and_saves_nothing(self):
        response = self._post(email="not-an-email")

        self.assertEqual(response.status_code, 200)  # re-renders, no redirect
        self.assertEqual(ContactMessage.objects.count(), 0)

    @patch("apps.contact.views.requests.post")
    def test_sixth_submission_in_an_hour_is_rate_limited(self, mock_post):
        mock_post.return_value = MagicMock(status_code=200)

        for _ in range(5):
            self._post()

        response = self._post()

        self.assertEqual(ContactMessage.objects.count(), 5)
        self.assertContains(response, "Too many messages")

    @patch("apps.contact.views.requests.post")
    def test_resend_api_failure_still_saves_message_and_redirects(self, mock_post):
        """
        The real-world scenario this guards against: Resend has a bad
        moment, or the network hiccups. The visitor's message is never
        lost - it's already saved before this call happens - and they
        still see a normal success page, not a 500. This is the
        SMTP-hang bug's replacement test: same guarantee, new transport.
        """
        mock_post.side_effect = Exception("simulated network failure")

        response = self._post()

        self.assertRedirects(response, reverse("contact:contact"))
        self.assertEqual(ContactMessage.objects.count(), 1)


@override_settings(RESEND_API_KEY="")
class ContactViewWithoutApiKeyTests(TestCase):
    """
    Mirrors the old console-email-backend convenience: local dev with no
    real Resend account configured should still let the form work end to
    end, just without an actual API call.
    """

    def setUp(self):
        cache.clear()

    @patch("apps.contact.views.requests.post")
    def test_submission_succeeds_without_calling_resend(self, mock_post):
        response = self.client.post(
            reverse("contact:contact"),
            {
                "name": "Local Dev",
                "email": "dev@example.com",
                "message": "Testing without an API key",
                "website": "",
            },
        )

        self.assertRedirects(response, reverse("contact:contact"))
        self.assertEqual(ContactMessage.objects.count(), 1)
        mock_post.assert_not_called()

