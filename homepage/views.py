"""Homepage backed by Django ORM."""
from django.db.models import Count
from django.shortcuts import render

from places.models import Category, Place


def index(request):
    # Categories with the number of their places; prefetch avoids N+1
    # queries when the template lists the places of every category.
    categories = (
        Category.objects
        .annotate(places_count=Count("places"))
        .prefetch_related("places")
        .order_by("name")
    )
    # The three best available places (LIMIT 3 via slicing).
    top_places = (
        Place.objects
        .filter(is_available=True)
        .select_related("category")
        .order_by("-rating", "name")[:3]
    )
    return render(request, "homepage/index.html", {
        "categories": categories,
        "places_count": Place.objects.count(),
        "top_places": top_places,
    })


def not_found(request, exception=None):
    return render(request, "404.html", {"exception": exception}, status=404)
