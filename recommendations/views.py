"""Recommendation views backed by Django ORM and Django forms."""
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import RecommendationFilterForm, RecommendationForm
from .models import Recommendation

PAGE_SIZE = 5

# Allowed values of ?sort= mapped to ORM fields; user input never reaches order_by().
SORT_FIELDS = {
    "date": "visit_date",
    "place": "place__name",
    "user": "user__name",
    "rating": "-place__rating",
}


def recommendation_list(request):
    form = RecommendationFilterForm(request.GET or None)
    form_valid = form.is_valid() if form.is_bound else False
    filters = form.cleaned_data if form_valid else {}
    error = "Проверьте введённые значения фильтров." if form.is_bound and not form_valid else None

    recommendations = Recommendation.objects.all()
    if filters.get("date"):
        recommendations = recommendations.for_date(filters["date"])
    # Filtering by foreign keys: no manual JOIN is needed.
    if filters.get("place"):
        recommendations = recommendations.filter(place=filters["place"])
    if filters.get("user"):
        recommendations = recommendations.filter(user=filters["user"])
    status = filters.get("status")
    if status in Recommendation.Status.values:
        recommendations = recommendations.filter(status=status)
    elif status == "not_cancelled":
        recommendations = recommendations.exclude(status=Recommendation.Status.CANCELLED)
    sort = filters.get("sort") or "date"

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
            "id", "visit_date", "status", "place_name",
            "place_rating", "category_name", "user_name",
        )
    )

    page_obj = Paginator(recommendations, PAGE_SIZE).get_page(request.GET.get("page"))
    return render(request, "recommendations/recommendation_list.html", {
        "recommendations": page_obj,
        "page_obj": page_obj,
        "form": form,
        "error": error,
    })


def recommendation_detail(request, recommendation_id):
    # One query with JOINs to user, place and category.
    recommendation = get_object_or_404(
        Recommendation.objects.with_related(),
        pk=recommendation_id,
    )
    return render(request, "recommendations/recommendation_detail.html", {
        "recommendation": recommendation,
    })


def _has_active_duplicate(form, exclude_pk=None):
    """Business rule: one active recommendation per user, place and date."""
    duplicates = Recommendation.objects.active().filter(
        user=form.cleaned_data["user"],
        place=form.cleaned_data["place"],
        visit_date=form.cleaned_data["visit_date"],
    )
    if exclude_pk is not None:
        # While editing, the recommendation must not conflict with itself.
        duplicates = duplicates.exclude(pk=exclude_pk)
    return duplicates.exists()


DUPLICATE_ERROR = "У пользователя уже есть активная рекомендация этого места на эту дату."


def recommendation_create(request):
    if request.method == "POST":
        form = RecommendationForm(request.POST)
        if form.is_valid():
            if _has_active_duplicate(form):
                form.add_error(None, DUPLICATE_ERROR)
            else:
                recommendation = form.save()
                messages.success(request, f"Рекомендация №{recommendation.pk} создана.")
                return redirect("recommendations:detail", recommendation.pk)
    else:
        form = RecommendationForm()
    return render(request, "recommendations/recommendation_form.html", {
        "form": form,
        "title": "Новая рекомендация",
        "submit_label": "Создать",
    })


def recommendation_edit(request, recommendation_id):
    # Only active recommendations can be changed; others return 404.
    recommendation = get_object_or_404(Recommendation.objects.active(), pk=recommendation_id)
    if request.method == "POST":
        form = RecommendationForm(request.POST, instance=recommendation)
        if form.is_valid():
            if _has_active_duplicate(form, exclude_pk=recommendation.pk):
                form.add_error(None, DUPLICATE_ERROR)
            else:
                form.save()
                messages.success(request, f"Рекомендация №{recommendation.pk} изменена.")
                return redirect("recommendations:detail", recommendation.pk)
    else:
        form = RecommendationForm(instance=recommendation)
    return render(request, "recommendations/recommendation_form.html", {
        "form": form,
        "recommendation": recommendation,
        "title": f"Редактирование рекомендации №{recommendation.pk}",
        "submit_label": "Сохранить",
    })


@require_POST
def recommendation_cancel(request, recommendation_id):
    recommendation = get_object_or_404(Recommendation.objects.active(), pk=recommendation_id)
    # The record is kept: only its status changes to "cancelled".
    recommendation.cancel()
    messages.success(request, f"Рекомендация №{recommendation.pk} отменена.")
    return redirect("recommendations:list")
