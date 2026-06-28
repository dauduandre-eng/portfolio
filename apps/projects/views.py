from django.views.generic import DetailView, ListView

from .models import Project


class ProjectListView(ListView):
    template_name = "projects/list.html"
    context_object_name = "projects"

    def get_queryset(self):
        # prefetch_related, not select_related: technologies is a
        # many-to-many, so Django needs a second query either way, but
        # prefetch_related runs that ONE extra query for the whole list.
        # Without it, {{ project.technologies.all }} in the template would
        # fire a fresh query per project — an N+1 query bug that's invisible
        # with 3 projects and very real with 30.
        return Project.objects.filter(is_published=True).prefetch_related(
            "technologies"
        )


class ProjectDetailView(DetailView):
    template_name = "projects/detail.html"
    context_object_name = "project"

    def get_queryset(self):
        return Project.objects.filter(is_published=True).prefetch_related(
            "technologies"
        )
