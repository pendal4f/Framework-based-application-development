"""Forms of the recommendations app: list filter and create/edit form."""
from datetime import timedelta

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from places.models import Place
from users.models import User

from .models import Recommendation

MAX_DAYS_AHEAD = 365


def validate_not_too_far(value):
    """Custom validator: a visit can be planned at most a year ahead."""
    if value > timezone.localdate() + timedelta(days=MAX_DAYS_AHEAD):
        raise ValidationError("Дата посещения не может быть позже чем через год.")


class RecommendationFilterForm(forms.Form):
    """GET filter of the recommendation list. The field names match the
    query parameters used since PR9, so old links keep working."""

    SORT_CHOICES = [
        ("date", "По дате"),
        ("place", "По месту"),
        ("user", "По пользователю"),
        ("rating", "По рейтингу места"),
    ]

    date = forms.DateField(
        required=False,
        label="Дата посещения",
        widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
    )
    place = forms.ModelChoiceField(
        queryset=Place.objects.order_by("name"),
        required=False,
        label="Место",
        empty_label="Все места",
    )
    user = forms.ModelChoiceField(
        queryset=User.objects.order_by("name"),
        required=False,
        label="Пользователь",
        empty_label="Все пользователи",
    )
    status = forms.ChoiceField(
        required=False,
        label="Статус",
        choices=[("", "Все"), *Recommendation.Status.choices,
                 ("not_cancelled", "Кроме отменённых")],
    )
    sort = forms.ChoiceField(
        required=False,
        label="Сортировка",
        choices=SORT_CHOICES,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css = "form-select" if isinstance(field.widget, forms.Select) else "form-control"
            field.widget.attrs.setdefault("class", css)


class RecommendationForm(forms.ModelForm):
    """Create/edit form. Status is not editable here: a new recommendation is
    always active, cancelling is a separate POST action."""

    class Meta:
        model = Recommendation
        fields = ["user", "place", "visit_date", "comment"]
        widgets = {
            "user": forms.Select(attrs={"class": "form-select"}),
            "place": forms.Select(attrs={"class": "form-select"}),
            "visit_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}, format="%Y-%m-%d"),
            "comment": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
        }
        help_texts = {
            "visit_date": "Место должно быть открыто в этот день недели.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["place"].queryset = Place.objects.select_related("category")
        self.fields["visit_date"].validators.append(validate_not_too_far)

    def clean_visit_date(self):
        visit_date = self.cleaned_data["visit_date"]
        if visit_date < timezone.localdate():
            raise ValidationError("Нельзя создать рекомендацию на прошедшую дату.")
        return visit_date

    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get("user")
        place = cleaned_data.get("place")
        visit_date = cleaned_data.get("visit_date")
        # Cross-field rules run only when the fields themselves are valid.
        if place and visit_date and not place.is_open_on(visit_date):
            self.add_error(
                "visit_date",
                f"«{place}» не принимает посетителей в выбранный день.",
            )
        if user and place and not user.interests.filter(pk=place.category_id).exists():
            self.add_error(
                "place",
                f"Категория «{place.category}» не входит в интересы пользователя.",
            )
        return cleaned_data
