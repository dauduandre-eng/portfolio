from django.test import TestCase
from django.urls import reverse

from apps.projects.models import Project


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

    def test_skip_link_is_present(self):
        response = self.client.get(reverse("core:home"))

        self.assertContains(response, "Skip to main content")


class AboutViewTests(TestCase):
    def test_about_page_returns_200_with_expected_template(self):
        response = self.client.get(reverse("core:about"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/about.html")


class RobotsTxtTests(TestCase):
    def test_returns_200_and_points_at_the_sitemap(self):
        response = self.client.get(reverse("robots_txt"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sitemap:")
        self.assertContains(response, "Disallow: /admin/")


class SitemapTests(TestCase):
    def test_includes_published_project_excludes_draft(self):
        """
        Same published/draft pattern as everywhere else in this project -
        a draft shouldn't leak into the sitemap any more than it leaks
        into the public list page or the chat assistant's context.
        """
        Project.objects.create(
            title="Visible Project", summary="s", description="d", is_published=True
        )
        Project.objects.create(
            title="Secret Draft", summary="s", description="d", is_published=False
        )

        response = self.client.get(reverse("sitemap"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "visible-project")
        self.assertNotContains(response, "secret-draft")

    def test_includes_static_pages(self):
        response = self.client.get(reverse("sitemap"))

        self.assertContains(response, "/projects/")
        self.assertContains(response, "/blog/")
        self.assertContains(response, "/contact/")


class CrossCuttingHardeningTests(TestCase):
    """
    Things that apply to every page, checked once here rather than
    duplicated across every app's own test file.
    """

    def test_canonical_url_is_present_and_correct(self):
        response = self.client.get(reverse("core:about"))

        self.assertContains(
            response, '<link rel="canonical" href="http://testserver/about/">'
        )

    def test_response_is_gzip_compressed_when_requested(self):
        response = self.client.get(reverse("core:home"), HTTP_ACCEPT_ENCODING="gzip")

        self.assertEqual(response.get("Content-Encoding"), "gzip")

