from django.conf import settings


def chat_enabled(request):
    """
    A context processor runs for every template render, site-wide -
    unlike a view's get_context_data, which only applies to that one view.
    This is what lets base.html decide whether to show the chat widget
    without every single view needing to remember to pass that flag in.
    """
    return {"chat_enabled": settings.CHAT_ENABLED}
