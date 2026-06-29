from django.urls import path

from . import views
from .feeds import LatestPostsFeed

app_name = "blog"

urlpatterns = [
    path("", views.BlogPostListView.as_view(), name="list"),
    # This MUST come before the <slug:slug>/ pattern below. Django tries
    # urlpatterns in order — if the slug pattern were listed first, a
    # request for /blog/feed/ would match it too (since "feed" is a
    # perfectly valid slug) and never reach the dedicated feed view.
    path("feed/", LatestPostsFeed(), name="feed"),
    path("<slug:slug>/", views.BlogPostDetailView.as_view(), name="detail"),
]
