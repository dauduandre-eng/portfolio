from django.views.generic import TemplateView


class HomeView(TemplateView):
    """
    TemplateView over a plain function view here because there's no logic
    yet — just "render this template". The moment this page needs to pull
    data (e.g. featured projects in a later milestone), overriding
    get_context_data() is a smaller change than rewriting a function view
    into a class.
    """

    template_name = "core/home.html"


class AboutView(TemplateView):
    template_name = "core/about.html"
