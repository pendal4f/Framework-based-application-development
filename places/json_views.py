"""Template-based place views for PR6 backed by the preserved JSON storage."""
from django.http import Http404
from django.shortcuts import render

from storage import load_categories, load_places


def place_list(request):
    categories = load_categories()
    return render(request, "places/place_list.html", {
        "legacy_storage": True,
        "places": load_places(categories),
    })


def place_detail(request, place_id):
    categories = load_categories()
    place = next((item for item in load_places(categories) if item.id == place_id), None)
    if place is None:
        raise Http404("Место не найдено")
    return render(request, "places/place_detail.html", {"place": place, "legacy_storage": True})
