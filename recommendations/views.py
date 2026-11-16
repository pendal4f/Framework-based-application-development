"""Recommendation views backed by Django ORM."""
from datetime import date

from django.core.paginator import Paginator
from django.db.models import F
from django.shortcuts import get_object_or_404, render

from places.models import Place
from users.models import User

from .models import Recommendation

PAGE_SIZE = 5

# Allowed values of ?sort= mapped to ORM fields; unknown values fall back to date.
SORT_FIELDS = {
    "date": "visit_date",
    "place": "place__name",
    "user": "user__name",
    "rating": "-place__rating",
}


def recommendation_list(request):
    visit_date = request.GET.get("date", "").strip()
    place_id = request.GET.get("place", "").strip()
    user_id = request.GET.get("user", "").strip()
    status = request.GET.get("status", "").strip()
    sort = request.GET.get("sort", "date")
    if sort not in SORT_FIELDS:
        sort = "date"
    error = None

    recommendations = Recommendation.objects.all()
    if visit_date:
        try:
            selected_date = date.fromisoformat(visit_date)
        except ValueError:
            error = "Укажите корректную дату."
        else:
            recommendations = recommendations.filter(visit_date=selected_date)
    # Filtering by foreign keys: no manual JOIN is needed.
    if place_id.isdigit():
        recommendations = recommendations.filter(place_id=int(place_id))
    if user_id.isdigit():
        recommendations = recommendations.filter(user_id=int(user_id))
    if status == "active":
        recommendations = recommendations.exclude(is_cancelled=True)
    elif status == "cancelled":
        recommendations = recommendations.filter(is_cancelled=True)

    # Only the fields the page needs: related names via F() + values().
    recommendations = (
        recommendations
        .annotate(
            place_name=F("place__name"),
            place_rating=F("place__rating"),
            category_name=F("place__category__name"),
            user_name=F("user__name"),
        )
        .order_by(SORT_FIELDS[sort], "pk")
        .values(
            "id", "visit_date", "is_cancelled", "place_name",
            "place_rating", "category_name", "user_name",
        )
    )

    page_obj = Paginator(recommendations, PAGE_SIZE).get_page(request.GET.get("page"))
    return render(request, "recommendations/recommendation_list.html", {
        "recommendations": page_obj,
        "page_obj": page_obj,
        "places": Place.objects.order_by("name"),
        "users": User.objects.order_by("name"),
        "visit_date": visit_date,
        "selected_place": place_id,
        "selected_user": user_id,
        "status": status,
        "sort": sort,
        "error": error,
    })


def recommendation_detail(request, recommendation_id):
    # One query with JOINs to user, place and category.
    recommendation = get_object_or_404(
        Recommendation.objects.select_related("user", "place__category"),
        pk=recommendation_id,
    )
    return render(request, "recommendations/recommendation_detail.html", {
        "recommendation": recommendation,
    })
