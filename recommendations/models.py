"""Recommendation of a place to a user for a planned visit date."""
from django.db import models

from places.models import Place
from users.models import User


class Recommendation(models.Model):
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
    is_cancelled = models.BooleanField(
        default=False,
        verbose_name="Рекомендация отменена",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Создано",
    )

    class Meta:
        ordering = ["visit_date", "pk"]
        verbose_name = "Рекомендация"
        verbose_name_plural = "Рекомендации"

    def __str__(self):
        return f"{self.place} — {self.visit_date} ({self.user})"

    def cancel(self):
        self.is_cancelled = True
        self.save(update_fields=["is_cancelled"])
