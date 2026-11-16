from django.shortcuts import render

from storage import load_categories, load_places


def index(request):
    categories = load_categories()
    places_count = len(load_places(categories))
    return render(request, "homepage/index.html", {
        "legacy_storage": True,
        "categories": categories,
        "places_count": places_count,
    })


def not_found(request, exception=None):
    return render(request, "404.html", {"exception": exception, "legacy_storage": True}, status=404)
