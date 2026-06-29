from django.core import mail
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from .models import ContactMessage


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

    def test_valid_submission_saves_message_and_sends_email(self):
        response = self._post()

        self.assertRedirects(response, reverse("contact:contact"))
        self.assertEqual(ContactMessage.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        # Reply-to is the visitor's address, not DEFAULT_FROM_EMAIL — so
        # hitting "reply" in an email client goes back to them, not into
        # a no-reply void.
        self.assertEqual(mail.outbox[0].reply_to, ["jamie@example.com"])

    def test_honeypot_filled_pretends_success_but_saves_nothing(self):
        response = self._post(
            name="Bot", email="bot@example.com", website="http://spam.example"
        )

        self.assertRedirects(response, reverse("contact:contact"))
        self.assertEqual(ContactMessage.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_invalid_email_reshows_form_and_saves_nothing(self):
        response = self._post(email="not-an-email")

        self.assertEqual(response.status_code, 200)  # re-renders, no redirect
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_sixth_submission_in_an_hour_is_rate_limited(self):
        for _ in range(5):
            self._post()

        response = self._post()

        self.assertEqual(ContactMessage.objects.count(), 5)
        self.assertContains(response, "Too many messages")
