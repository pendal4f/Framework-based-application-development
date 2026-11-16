"""Users of the recommendation service (domain users, not Django auth)."""
from django.db import models

from places.models import Category


class User(models.Model):
    """A person who receives place recommendations by interests."""

    name = models.CharField(
        max_length=200,
        verbose_name="Имя пользователя",
    )
    email = models.EmailField(
        blank=True,
        verbose_name="Электронная почта",
    )
    # Many-to-many: a user has several interests, a category interests many users.
    interests = models.ManyToManyField(
        Category,
        blank=True,
        related_name="interested_users",
        verbose_name="Интересы",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.name
