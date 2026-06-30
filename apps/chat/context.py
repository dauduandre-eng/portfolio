from django.core.cache import cache

from apps.blog.models import BlogPost
from apps.projects.models import Project

CONTEXT_CACHE_KEY = "chat:context"
CONTEXT_CACHE_TTL = 60 * 10  # 10 minutes: long enough to spare the DB from
# a query on every single chat message, short enough that a newly
# published project shows up in conversation reasonably soon after.

ABOUT_BLURB = (
    "Daudu Mezenobe Andrew is a full-stack developer based in Lagos, "
    "Nigeria, working primarily in Django and Python with PostgreSQL. "
    "Since 2024 he's built real production systems: a multi-vendor "
    "WhatsApp commerce platform with live Paystack billing (ProductBot), "
    "a fintech investment simulator on its own custom domain "
    "(ZovoAssets), and a captive-portal Wi-Fi access system for shared "
    "workspaces (PepperHouse). In December 2025 he moved to focus on "
    "software engineering full-time. He's currently exploring agentic AI "
    "integration with Claude's API on one of his existing projects."
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
