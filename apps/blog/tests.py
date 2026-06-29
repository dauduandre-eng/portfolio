from django.test import TestCase
from django.urls import reverse

from .models import BlogPost


class BlogPostModelTests(TestCase):
    def test_slug_is_auto_generated_from_title(self):
        post = BlogPost.objects.create(
            title="Why I Chose Django", excerpt="e", body="b"
        )

        self.assertEqual(post.slug, "why-i-chose-django")

    def test_get_absolute_url_uses_the_slug(self):
        post = BlogPost.objects.create(title="A Post", excerpt="e", body="b")

        self.assertEqual(post.get_absolute_url(), f"/blog/{post.slug}/")


class BlogPostListViewTests(TestCase):
    def test_shows_published_posts_only(self):
        BlogPost.objects.create(
            title="Visible Post", excerpt="e", body="b", is_published=True
        )
        BlogPost.objects.create(
            title="Draft Post", excerpt="e", body="b", is_published=False
        )

        response = self.client.get(reverse("blog:list"))

        self.assertContains(response, "Visible Post")
        self.assertNotContains(response, "Draft Post")

    def test_empty_state_shown_when_no_posts_exist(self):
        response = self.client.get(reverse("blog:list"))

        self.assertContains(response, "Nothing published yet")


class BlogPostDetailViewTests(TestCase):
    def test_published_post_returns_200(self):
        post = BlogPost.objects.create(title="A Post", excerpt="e", body="b")

        response = self.client.get(reverse("blog:detail", kwargs={"slug": post.slug}))

        self.assertEqual(response.status_code, 200)

    def test_draft_post_returns_404(self):
        post = BlogPost.objects.create(
            title="Draft Post", excerpt="e", body="b", is_published=False
        )

        response = self.client.get(reverse("blog:detail", kwargs={"slug": post.slug}))

        self.assertEqual(response.status_code, 404)


class BlogFeedTests(TestCase):
    def test_feed_url_resolves_to_the_feed_not_the_detail_view(self):
        """
        Regression test for the urls.py ordering gotcha: if feed/ were
        listed after <slug:slug>/, this request would 404 (Django would
        try to find a BlogPost with slug="feed") instead of returning RSS.
        """
        response = self.client.get(reverse("blog:feed"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("rss", response["Content-Type"])

    def test_feed_includes_published_posts_only(self):
        BlogPost.objects.create(
            title="Visible Post", excerpt="e", body="b", is_published=True
        )
        BlogPost.objects.create(
            title="Draft Post", excerpt="e", body="b", is_published=False
        )

        response = self.client.get(reverse("blog:feed"))

        self.assertContains(response, "Visible Post")
        self.assertNotContains(response, "Draft Post")
