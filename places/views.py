"""Place catalog views backed by Django ORM."""
from datetime import date

from django.db.models import Avg, Count, IntegerField, Max, Min, OuterRef, Q, Subquery
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, render

from recommendations.models import Recommendation

from .models import Category, Place

# Allowed sort keys -> model fields. User input never reaches order_by() directly.
PLACE_SORT_FIELDS = {
    "rating": ("-rating", "name"),
    "name": ("name",),
    "category": ("category__name", "name"),
}


def place_list(request):
    query = request.GET.get("q", "").strip()
    category_id = request.GET.get("category_id", "").strip()
    min_rating = request.GET.get("min_rating", "").strip()
    sort = request.GET.get("sort", "rating")

    places = Place.objects.select_related("category")
    if query:
        # Search by several string fields: name OR address.
        places = places.filter(Q(name__icontains=query) | Q(address__icontains=query))
    if category_id.isdigit():
        places = places.filter(category_id=int(category_id))
    if min_rating.isdigit():
        places = places.filter(rating__gte=int(min_rating))
    places = places.order_by(*PLACE_SORT_FIELDS.get(sort, PLACE_SORT_FIELDS["rating"]))

    return render(request, "places/place_list.html", {
        "places": places,
        "categories": Category.objects.order_by("name"),
        "query": query,
        "selected_category": category_id,
        "min_rating": min_rating,
        "sort": sort,
    })


def place_detail(request, slug):
    place = get_object_or_404(Place.objects.select_related("category"), slug=slug)
    # Reverse relations: place.schedule and place.recommendations.
    recommendations = (
        place.recommendations
        .select_related("user")
        .exclude(status=Recommendation.Status.CANCELLED)
        .order_by("visit_date")
    )
    return render(request, "places/place_detail.html", {
        "place": place,
        "schedule": place.schedule.all(),
        "recommendations": recommendations,
    })


def available_places(request):
    raw_date = request.GET.get("date", "").strip()
    error = None
    try:
        selected_date = date.fromisoformat(raw_date) if raw_date else date.today()
    except ValueError:
        selected_date = None
        error = "Укажите корректную дату."

    places = Place.objects.none()
    if selected_date is not None:
        # Filter by the related model (schedule) with several conditions.
        places = (
            Place.objects
            .filter(
                is_available=True,
                schedule__weekday=selected_date.weekday(),
                schedule__is_available=True,
            )
            .select_related("category")
            .order_by("-rating", "name")
        )
    return render(request, "places/available.html", {
        "places": places,
        "selected_date": selected_date.isoformat() if selected_date else raw_date,
        "error": error,
    })


def statistics(request):
    # Active recommendations per category as a correlated subquery, so that
    # joining recommendations does not inflate place counts and averages.
    active_recommendations = (
        Recommendation.objects
        .active()
        .filter(place__category=OuterRef("pk"))
        .order_by()
        .values("place__category")
        .annotate(total=Count("pk"))
        .values("total")
    )
    rows = (
        Category.objects
        .annotate(
            places_count=Count("places"),
            available_count=Count("places", filter=Q(places__is_available=True)),
            average_rating=Avg("places__rating"),
            recommendations_count=Coalesce(
                Subquery(active_recommendations, output_field=IntegerField()), 0,
            ),
        )
        .order_by("-places_count", "name")
    )
    summary = Place.objects.aggregate(
        total_places=Count("pk"),
        average_rating=Avg("rating"),
        best_rating=Max("rating"),
        worst_rating=Min("rating"),
    )
    statuses = Recommendation.Status
    recommendation_summary = Recommendation.objects.aggregate(
        total=Count("pk"),
        active=Count("pk", filter=Q(status=statuses.ACTIVE)),
        cancelled=Count("pk", filter=Q(status=statuses.CANCELLED)),
        completed=Count("pk", filter=Q(status=statuses.COMPLETED)),
    )
    return render(request, "places/statistics.html", {
        "rows": rows,
        "summary": summary,
        "recommendation_summary": recommendation_summary,
    })
