from django.test import TestCase
from django.urls import reverse

from .models import Project, Technology


class ProjectModelTests(TestCase):
    def test_slug_is_auto_generated_from_title(self):
        project = Project.objects.create(
            title="Real-Time Chat App", summary="s", description="d"
        )

        self.assertEqual(project.slug, "real-time-chat-app")

    def test_explicit_slug_is_not_overwritten(self):
        project = Project.objects.create(
            title="Some Project", slug="custom-slug", summary="s", description="d"
        )

        self.assertEqual(project.slug, "custom-slug")

    def test_get_absolute_url_uses_the_slug(self):
        project = Project.objects.create(title="Demo", summary="s", description="d")

        self.assertEqual(project.get_absolute_url(), f"/projects/{project.slug}/")


class ProjectListViewTests(TestCase):
    def test_shows_published_projects_only(self):
        Project.objects.create(
            title="Visible Project", summary="s", description="d", is_published=True
        )
        Project.objects.create(
            title="Draft Project", summary="s", description="d", is_published=False
        )

        response = self.client.get(reverse("projects:list"))

        self.assertContains(response, "Visible Project")
        self.assertNotContains(response, "Draft Project")

    def test_empty_state_shown_when_no_projects_exist(self):
        response = self.client.get(reverse("projects:list"))

        self.assertContains(response, "Projects are on their way")

    def test_technologies_are_prefetched_not_queried_per_project(self):
        """
        Without prefetch_related, rendering N projects' technologies in the
        template fires N extra queries. This creates 3 projects with tags
        and asserts the WHOLE response — including all technology badges —
        renders in a fixed, small number of queries regardless of how many
        projects exist.
        """
        django_tag = Technology.objects.create(name="Django")
        for i in range(3):
            project = Project.objects.create(
                title=f"Project {i}", summary="s", description="d"
            )
            project.technologies.add(django_tag)

        with self.assertNumQueries(2):  # 1 for projects, 1 prefetch for tags
            self.client.get(reverse("projects:list"))


class ProjectDetailViewTests(TestCase):
    def test_published_project_returns_200(self):
        project = Project.objects.create(
            title="Visible Project", summary="s", description="d"
        )

        response = self.client.get(
            reverse("projects:detail", kwargs={"slug": project.slug})
        )

        self.assertEqual(response.status_code, 200)

    def test_draft_project_returns_404(self):
        project = Project.objects.create(
            title="Draft Project", summary="s", description="d", is_published=False
        )

        response = self.client.get(
            reverse("projects:detail", kwargs={"slug": project.slug})
        )

        self.assertEqual(response.status_code, 404)

    def test_nonexistent_slug_returns_404(self):
        response = self.client.get(
            reverse("projects:detail", kwargs={"slug": "does-not-exist"})
        )

        self.assertEqual(response.status_code, 404)
