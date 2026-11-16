from django.contrib import admin
from django.db.models import Count

from recommendations.admin import RecommendationInline

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "recommendations_count")
    list_display_links = ("id", "name")
    search_fields = ("name", "email")
    list_filter = ("interests",)
    ordering = ("name",)
    filter_horizontal = ("interests",)
    inlines = (RecommendationInline,)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            recommendations_total=Count("recommendations"),
        )

    @admin.display(description="Рекомендаций", ordering="recommendations_total")
    def recommendations_count(self, obj):
        return obj.recommendations_total
