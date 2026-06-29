from django.contrib.syndication.views import Feed

from .models import BlogPost


class LatestPostsFeed(Feed):
    title = "Daudu Mezenobe Andrew — Blog"
    link = "/blog/"
    description = "Backend engineering, Django, and AI integration, without the hype."

    def items(self):
        return BlogPost.objects.filter(is_published=True)[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.excerpt

    def item_pubdate(self, item):
        return item.published_at

    # item_link falls back to item.get_absolute_url() automatically when
    # not defined here — Django's syndication framework resolves that
    # relative URL to an absolute one using the current request, so no
    # extra "what's our domain" configuration is needed.
