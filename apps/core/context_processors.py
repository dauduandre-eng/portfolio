def canonical_url(request):
    """
    request.path (not request.get_full_path()) deliberately excludes the
    query string - a canonical URL should point at the clean version of a
    page even if someone arrived via ?utm_source=... tracking params.
    """
    return {"canonical_url": request.build_absolute_uri(request.path)}
