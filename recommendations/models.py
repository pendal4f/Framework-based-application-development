"""Recommendation of a place to a user for a planned visit date."""
from django.db import models

from places.models import Place
from users.models import User


class RecommendationQuerySet(models.QuerySet):
    """Reusable filters of recommendations by status and date."""

    def active(self):
        return self.filter(status=self.model.Status.ACTIVE)

    def cancelled(self):
        return self.filter(status=self.model.Status.CANCELLED)

    def completed(self):
        return self.filter(status=self.model.Status.COMPLETED)

    def for_date(self, selected_date):
        return self.filter(visit_date=selected_date)

    def with_related(self):
        return self.select_related("user", "place__category")


class RecommendationManager(models.Manager.from_queryset(RecommendationQuerySet)):
    pass


class Recommendation(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Активна"
        CANCELLED = "cancelled", "Отменена"
        COMPLETED = "completed", "Завершена"

    # PROTECT keeps the history: a user or a place with recommendations
    # cannot be deleted by accident.
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="recommendations",
        verbose_name="Пользователь",
    )
    place = models.ForeignKey(
        Place,
        on_delete=models.PROTECT,
        related_name="recommendations",
        verbose_name="Место",
    )
    visit_date = models.DateField(
        verbose_name="Дата посещения",
    )
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name="Статус",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Создано",
    )

    objects = RecommendationManager()

    class Meta:
        ordering = ["visit_date", "pk"]
        verbose_name = "Рекомендация"
        verbose_name_plural = "Рекомендации"

    def __str__(self):
        return f"{self.place} — {self.visit_date} ({self.user})"

    def cancel(self):
        """Mark the recommendation as cancelled; the record itself is kept."""
        self.status = self.Status.CANCELLED
        self.save(update_fields=["status"])
