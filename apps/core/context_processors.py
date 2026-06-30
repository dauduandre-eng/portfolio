def canonical_url(request):
    """
    request.path (not request.get_full_path()) deliberately excludes the
    query string - a canonical URL should point at the clean version of a
    page even if someone arrived via ?utm_source=... tracking params.
    """
    return {"canonical_url": request.build_absolute_uri(request.path)}


def active_nav(request):
    """
    A naive "does this URL match the current path" check breaks here:
    Projects and Blog each have a list page AND detail pages that should
    highlight the same nav item, so we match on the URL's app_name instead.
    Home and About share the `core` app, so those two are matched on the
    specific view name rather than the app, or being on About would
    incorrectly also light up Home.
    """
    match = request.resolver_match
    if match is None:
        return {"active_nav": None}

    if match.app_name == "core":
        active = match.url_name  # "home" or "about"
    else:
        active = match.app_name  # "projects", "blog", "contact"

    return {"active_nav": active}
