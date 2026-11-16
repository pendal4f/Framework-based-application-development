from django.contrib import admin

from .models import Recommendation


class RecommendationInline(admin.TabularInline):
    """Recommendations shown inside place and user change pages."""

    model = Recommendation
    fields = ("user", "place", "visit_date", "status")
    autocomplete_fields = ("user", "place")
    extra = 0
    show_change_link = True


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ("id", "visit_date", "user", "place", "place_category", "status")
    list_display_links = ("id", "visit_date")
    list_filter = ("status", "visit_date", "place__category")
    search_fields = ("user__name", "place__name", "place__address")
    ordering = ("-visit_date", "-id")
    list_per_page = 20
    date_hierarchy = "visit_date"
    autocomplete_fields = ("user", "place")
    readonly_fields = ("created_at",)
    # One query with JOINs instead of a query per row for user/place/category.
    list_select_related = ("user", "place__category")
    actions = ("mark_cancelled", "mark_active", "mark_completed")

    @admin.display(description="Категория", ordering="place__category__name")
    def place_category(self, obj):
        return obj.place.category

    def _set_status(self, request, queryset, status, message):
        updated = queryset.update(status=status)
        self.message_user(request, f"{message}: {updated}")

    @admin.action(description="Отменить выбранные рекомендации")
    def mark_cancelled(self, request, queryset):
        self._set_status(request, queryset, Recommendation.Status.CANCELLED, "Отменено")

    @admin.action(description="Вернуть выбранные в активные")
    def mark_active(self, request, queryset):
        self._set_status(request, queryset, Recommendation.Status.ACTIVE, "Активировано")

    @admin.action(description="Отметить выбранные как завершённые")
    def mark_completed(self, request, queryset):
        self._set_status(request, queryset, Recommendation.Status.COMPLETED, "Завершено")
