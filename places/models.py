"""ORM models of the place catalog: categories, places and weekly schedule."""
from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models import Case, Value, When
from django.urls import reverse
from django.utils.text import slugify
from unidecode import unidecode

TOP_RATING = 8


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
        help_text="Целое число от 0 до 10.",
    )
    is_available = models.BooleanField(
        default=True,
        verbose_name="Доступно для посещения",
    )
    slug = models.SlugField(
        max_length=220,
        unique=True,
        editable=False,
        verbose_name="URL-идентификатор",
    )
    # Calculated by the database from rating and stored in the table.
    is_top_rated = models.GeneratedField(
        expression=Case(
            When(rating__gte=TOP_RATING, then=Value(True)),
            default=Value(False),
            output_field=models.BooleanField(),
        ),
        output_field=models.BooleanField(),
        db_persist=True,
        verbose_name="Высокий рейтинг",
    )

    class Meta:
        ordering = ["-rating", "name"]
        verbose_name = "Место"
        verbose_name_plural = "Места"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # The slug is built once (transliterated name + pk) and then kept stable.
        if not self.slug:
            base_slug = slugify(unidecode(self.name)) or "place"
            if self.pk is None:
                super().save(*args, **kwargs)
                self.slug = f"{base_slug}-{self.pk}"
                super().save(update_fields=["slug"])
                return
            self.slug = f"{base_slug}-{self.pk}"
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("places:detail", kwargs={"slug": self.slug})

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
