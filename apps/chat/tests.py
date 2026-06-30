import json
from unittest.mock import MagicMock, patch

from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.projects.models import Project

from .context import build_context


def _mock_anthropic_response(text="Mocked reply."):
    """
    Builds a fake response shaped like what the real SDK returns
    (response.content[0].text), without calling the actual API.
    """
    block = MagicMock()
    block.text = text
    response = MagicMock()
    response.content = [block]
    return response


class BuildContextTests(TestCase):
    def setUp(self):
        # build_context() caches its result for 10 minutes - without
        # clearing it, a context built (and cached) by an earlier test
        # leaks into this one regardless of what's actually in the DB now.
        cache.clear()

    def test_published_project_is_included(self):
        Project.objects.create(
            title="Visible Project", summary="A real summary."
        )

        context = build_context()

        self.assertIn("Visible Project", context)

    def test_draft_project_is_excluded(self):
        """
        Confirms the chat respects the same is_published flag as the
        public pages — a draft project never leaks into what the
        assistant says, even indirectly.
        """
        Project.objects.create(
            title="Secret Draft",
            summary="s",
            is_published=False,
        )

        context = build_context()

        self.assertNotIn("Secret Draft", context)


@override_settings(CHAT_ENABLED=True, ANTHROPIC_API_KEY="test-key")
class ChatAskViewTests(TestCase):
    def setUp(self):
        # The rate-limit counter is per client IP, and the test client
        # always uses the same fake IP. LocMemCache, unlike the test
        # database, is NOT reset between test methods - without this, an
        # earlier test's submissions count against this one's limit.
        cache.clear()

    def _post(self, message="What technologies do you work with?"):
        return self.client.post(
            reverse("chat:ask"),
            data=json.dumps({"message": message}),
            content_type="application/json",
        )

    @patch("apps.chat.views.anthropic.Anthropic")
    def test_valid_message_returns_reply(self, mock_anthropic_cls):
        mock_anthropic_cls.return_value.messages.create.return_value = (
            _mock_anthropic_response("Andrew works mainly in Django and Flask.")
        )

        response = self._post()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["reply"], "Andrew works mainly in Django and Flask."
        )

    def test_empty_message_returns_400(self):
        response = self._post(message="   ")

        self.assertEqual(response.status_code, 400)

    def test_overlong_message_returns_400(self):
        response = self._post(message="x" * 501)

        self.assertEqual(response.status_code, 400)

    @override_settings(CHAT_ENABLED=False)
    def test_disabled_returns_503(self):
        response = self._post()

        self.assertEqual(response.status_code, 503)

    @patch("apps.chat.views.anthropic.Anthropic")
    def test_api_failure_returns_friendly_message_not_500(self, mock_anthropic_cls):
        mock_anthropic_cls.return_value.messages.create.side_effect = Exception(
            "simulated API outage"
        )

        response = self._post()

        self.assertEqual(response.status_code, 200)
        self.assertIn("trouble", response.json()["reply"])

    @patch("apps.chat.views.anthropic.Anthropic")
    def test_sixth_message_in_an_hour_is_rate_limited(self, mock_anthropic_cls):
        mock_anthropic_cls.return_value.messages.create.return_value = (
            _mock_anthropic_response()
        )

        for _ in range(15):
            self._post()

        response = self._post()

        self.assertEqual(response.status_code, 429)

    @patch("apps.chat.views.anthropic.Anthropic")
    def test_conversation_history_is_sent_on_the_second_message(
        self, mock_anthropic_cls
    ):
        """
        Confirms history actually persists across requests via the
        session, by inspecting what the second call sent to the (mocked)
        API - not just trusting that session storage "should" work.
        """
        mock_create = mock_anthropic_cls.return_value.messages.create
        mock_create.return_value = _mock_anthropic_response("First reply.")

        self._post(message="What's your tech stack?")

        mock_create.return_value = _mock_anthropic_response("Second reply.")
        self._post(message="And what about the AI feature?")

        second_call_messages = mock_create.call_args.kwargs["messages"]
        self.assertEqual(len(second_call_messages), 3)  # 2 user + 1 assistant
        self.assertEqual(second_call_messages[0]["content"], "What's your tech stack?")


class ChatWidgetVisibilityTests(TestCase):
    @override_settings(CHAT_ENABLED=True)
    def test_widget_appears_when_enabled(self):
        response = self.client.get(reverse("core:home"))

        self.assertContains(response, "Ask about my work")

    @override_settings(CHAT_ENABLED=False)
    def test_widget_is_absent_when_disabled(self):
        response = self.client.get(reverse("core:home"))

        self.assertNotContains(response, "Ask about my work")
