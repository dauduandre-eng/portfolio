from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.blog.models import BlogPost
from apps.projects.models import Project


class StaticViewSitemap(Sitemap):
    """
    Pages with no model behind them still belong in the sitemap - this is
    the simplest way Django's sitemap framework supports that: list the
    URL names, and reverse() does the rest.
    """

    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return [
            "core:home",
            "core:about",
            "projects:list",
            "blog:list",
            "contact:contact",
        ]

    def location(self, item):
        return reverse(item)


class ProjectSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.9  # the centerpiece of the site - weighted higher than static pages

    def items(self):
        return Project.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at


class BlogPostSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return BlogPost.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at
