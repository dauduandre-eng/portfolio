from django.conf import settings
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

    def test_bio_mentions_real_background_not_placeholder_copy(self):
        """
        Regression test specifically against the old placeholder bio
        coming back - if someone reverts this template accidentally, this
        should fail loudly rather than silently shipping generic copy.
        """
        response = self.client.get(reverse("core:about"))

        self.assertContains(response, "Code::Blocks")
        self.assertContains(response, "December 2025")
        self.assertNotContains(response, "I work primarily in Django and Flask, with")


class ActiveNavTests(TestCase):
    """
    Confirms the app-name-based matching actually does what it's meant
    to: a Project's DETAIL page (not just the list page) should still
    highlight "Projects" in the nav, since both share the projects app.
    """

    def test_home_page_marks_home_link_active(self):
        response = self.client.get(reverse("core:home"))
        content = response.content.decode()

        self.assertIn('aria-current="page"', content)
        self.assertIn('class="nav-link active"', content)

    def test_about_page_does_not_mark_home_active(self):
        response = self.client.get(reverse("core:about"))

        home_link_start = response.content.decode().find('href="/">Home')
        active_marker = response.content.decode()[
            max(0, home_link_start - 80) : home_link_start
        ]
        self.assertNotIn("active", active_marker)

    def test_project_detail_page_marks_projects_link_active(self):
        project = Project.objects.create(
            title="A Project", summary="s", description="d"
        )

        response = self.client.get(project.get_absolute_url())

        projects_link_index = response.content.decode().find("Projects</a>")
        preceding = response.content.decode()[
            max(0, projects_link_index - 150) : projects_link_index
        ]
        self.assertIn("active", preceding)


class FooterTests(TestCase):
    def test_footer_links_to_real_github_and_linkedin(self):
        response = self.client.get(reverse("core:home"))

        self.assertContains(response, "https://github.com/dauduandre-eng")
        self.assertContains(response, "https://linkedin.com/in/andrewdaudu")

    def test_footer_includes_resume_download(self):
        response = self.client.get(reverse("core:home"))

        self.assertContains(response, "resume.pdf")

    def test_resume_pdf_exists_in_the_static_source_directory(self):
        """
        Confirms the actual file collectstatic would pick up genuinely
        exists on disk - not just that the template links to a path.
        Doesn't request it through the test client: Django's test client
        doesn't serve files under STATICFILES_DIRS the way `runserver`
        does in real dev (verified directly against a live runserver
        instance), so routing through self.client here would test a
        Django test-client quirk, not the thing that actually matters.
        """
        resume_path = settings.BASE_DIR / "static" / "resume.pdf"

        self.assertTrue(resume_path.exists())

    def test_footer_includes_philosophy_signoff(self):
        response = self.client.get(reverse("core:home"))

        self.assertContains(response, "Every Personal Build Is an Asset.")
        self.assertContains(response, "Build. Learn. Share. Grow.")


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

