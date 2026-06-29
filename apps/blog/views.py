from django.views.generic import DetailView, ListView

from .models import BlogPost


class BlogPostListView(ListView):
    template_name = "blog/list.html"
    context_object_name = "posts"

    def get_queryset(self):
        # No prefetch_related needed here, unlike projects — there's no
        # related model to fetch. The optimization only earns its place
        # when there's an actual N+1 to prevent.
        return BlogPost.objects.filter(is_published=True)


class BlogPostDetailView(DetailView):
    template_name = "blog/detail.html"
    context_object_name = "post"

    def get_queryset(self):
        return BlogPost.objects.filter(is_published=True)
