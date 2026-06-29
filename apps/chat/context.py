from django.core.cache import cache

from apps.blog.models import BlogPost
from apps.projects.models import Project

CONTEXT_CACHE_KEY = "chat:context"
CONTEXT_CACHE_TTL = 60 * 10  # 10 minutes: long enough to spare the DB from
# a query on every single chat message, short enough that a newly
# published project shows up in conversation reasonably soon after.

# TODO: personalize this with real specifics (years of experience,
# availability, what kind of work you're looking for) — same caveat as
# the About page bio: nothing here is a claim about your actual history.
ABOUT_BLURB = (
    "Daudu Mezenobe Andrew is a full-stack Python developer working "
    "primarily in Django and Flask, with PostgreSQL as the default "
    "datastore. He cares about properly modeled data, tested code, and "
    "AI features that are scoped to a real problem rather than bolted on "
    "for the sake of a buzzword."
)


def build_context():
    cached = cache.get(CONTEXT_CACHE_KEY)
    if cached is not None:
        return cached

    projects = Project.objects.filter(is_published=True).prefetch_related(
        "technologies"
    )
    posts = BlogPost.objects.filter(is_published=True)[:5]

    project_lines = [
        f"- {p.title}: {p.summary} (tech: "
        f"{', '.join(t.name for t in p.technologies.all()) or 'unspecified'})"
        for p in projects
    ] or ["No projects published yet."]

    post_lines = [
        f"- {post.title}: {post.excerpt}" for post in posts
    ] or ["No blog posts published yet."]

    context = (
        f"{ABOUT_BLURB}\n\n"
        f"Published projects:\n" + "\n".join(project_lines) + "\n\n"
        "Recent blog posts:\n" + "\n".join(post_lines)
    )

    cache.set(CONTEXT_CACHE_KEY, context, timeout=CONTEXT_CACHE_TTL)
    return context
