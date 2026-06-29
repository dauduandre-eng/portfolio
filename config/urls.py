from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.db import connection
from django.http import JsonResponse
from django.urls import include, path

from apps.core.sitemaps import BlogPostSitemap, ProjectSitemap, StaticViewSitemap
from apps.core.views import robots_txt

sitemaps = {
    "static": StaticViewSitemap,
    "projects": ProjectSitemap,
    "blog": BlogPostSitemap,
}


def healthz(request):
    """
    Confirms the app can actually reach the database — not just that the
    process started. A view that doesn't touch the DB only proves Django
    booted; this one proves the full chain (settings -> DATABASES ->
    connection -> query) works end to end.

    We'll point Render's health check at this URL in Milestone 8.
    """
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("healthz/", healthz, name="healthz"),
    path("robots.txt", robots_txt, name="robots_txt"),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="sitemap",
    ),
    path("", include("apps.core.urls")),
    path("projects/", include("apps.projects.urls")),
    path("blog/", include("apps.blog.urls")),
    path("contact/", include("apps.contact.urls")),
    path("chat/", include("apps.chat.urls")),
]
