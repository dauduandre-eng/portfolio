from django.test import TestCase
from django.urls import reverse


class HomeViewTests(TestCase):
    def test_home_page_returns_200_with_expected_template(self):
        response = self.client.get(reverse("core:home"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/home.html")

    def test_home_page_states_the_value_proposition(self):
        """
        A loose content check rather than just a status code — if someone
        accidentally deletes the headline while editing the template,
        this test should catch it, not just "the page didn't 500".
        """
        response = self.client.get(reverse("core:home"))

        self.assertContains(response, "Full-Stack Python Developer")


class AboutViewTests(TestCase):
    def test_about_page_returns_200_with_expected_template(self):
        response = self.client.get(reverse("core:about"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/about.html")
