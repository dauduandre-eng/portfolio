from django.contrib import admin
from django.db import connection
from django.http import JsonResponse
from django.urls import include, path


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
    path("", include("apps.core.urls")),
]
