"""ORM models of the place catalog: categories, places and weekly schedule."""
from django.core.validators import MaxValueValidator
from django.db import models


class Category(models.Model):
    """Thematic direction of leisure, e.g. music, sport or science."""

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Название категории",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Place(models.Model):
    """A venue that can be recommended to a user."""

    name = models.CharField(
        max_length=200,
        verbose_name="Название места",
    )
    # PROTECT: a category cannot disappear while places still refer to it.
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="places",
        verbose_name="Категория",
    )
    address = models.CharField(
        max_length=255,
        verbose_name="Адрес",
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(10)],
        verbose_name="Рейтинг",
    )
    is_available = models.BooleanField(
        default=True,
        verbose_name="Доступно для посещения",
    )

    class Meta:
        ordering = ["-rating", "name"]
        verbose_name = "Место"
        verbose_name_plural = "Места"

    def __str__(self):
        return self.name

    def is_open_on(self, selected_date):
        """Return True when the place accepts visitors on the given date."""
        return self.is_available and self.schedule.filter(
            weekday=selected_date.weekday(),
            is_available=True,
        ).exists()


class PlaceAvailability(models.Model):
    """Weekly schedule: whether a place is open on a given day of the week."""

    class Weekday(models.IntegerChoices):
        MONDAY = 0, "Понедельник"
        TUESDAY = 1, "Вторник"
        WEDNESDAY = 2, "Среда"
        THURSDAY = 3, "Четверг"
        FRIDAY = 4, "Пятница"
        SATURDAY = 5, "Суббота"
        SUNDAY = 6, "Воскресенье"

    # CASCADE: the schedule has no meaning without its place.
    place = models.ForeignKey(
        Place,
        on_delete=models.CASCADE,
        related_name="schedule",
        verbose_name="Место",
    )
    weekday = models.PositiveSmallIntegerField(
        choices=Weekday.choices,
        verbose_name="День недели",
    )
    is_available = models.BooleanField(
        default=True,
        verbose_name="Открыто",
    )

    class Meta:
        ordering = ["place", "weekday"]
        verbose_name = "График работы"
        verbose_name_plural = "График работы"
        constraints = [
            models.UniqueConstraint(
                fields=["place", "weekday"],
                name="unique_place_weekday",
            ),
        ]

    def __str__(self):
        return f"{self.place} — {self.get_weekday_display()}"
