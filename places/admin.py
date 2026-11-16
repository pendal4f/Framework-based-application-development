from django.contrib import admin
from django.db.models import Count, F, Q, Value
from django.db.models.functions import Least

from recommendations.admin import RecommendationInline
from recommendations.models import Recommendation

from .models import Category, Place, PlaceAvailability


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "places_count", "description")
    search_fields = ("name",)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(places_count=Count("places"))

    @admin.display(description="Мест", ordering="places_count")
    def places_count(self, obj):
        return obj.places_count


class PlaceAvailabilityInline(admin.TabularInline):
    model = PlaceAvailability
    extra = 0
    max_num = 7


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = (
        "id", "name", "category", "rating", "is_available",
        "is_top_rated", "active_recommendations",
    )
    list_display_links = ("id", "name")
    list_editable = ("rating", "is_available")
    list_filter = ("category", "is_available", "is_top_rated")
    search_fields = ("name", "address")
    ordering = ("-rating", "name")
    list_per_page = 20
    list_select_related = ("category",)
    readonly_fields = ("slug", "is_top_rated")
    inlines = (PlaceAvailabilityInline, RecommendationInline)
    actions = ("raise_rating",)
    view_on_site = True

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            active_count=Count(
                "recommendations",
                filter=Q(recommendations__status=Recommendation.Status.ACTIVE),
            ),
        )

    @admin.display(description="Активных рекомендаций", ordering="active_count")
    def active_recommendations(self, obj):
        return obj.active_count

    @admin.action(description="Повысить рейтинг на 1 (не выше 10)")
    def raise_rating(self, request, queryset):
        # F() lets the database compute the new value without loading objects.
        updated = queryset.update(rating=Least(F("rating") + 1, Value(10)))
        self.message_user(request, f"Рейтинг повышен у мест: {updated}")
