"""Forms of the place catalog: search filter and create/edit form with image."""
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator

from .models import Category, Place

MAX_IMAGE_SIZE = 2 * 1024 * 1024


def validate_has_letters(value):
    """Custom validator: a name must contain letters, not only digits/symbols."""
    if not any(char.isalpha() for char in value):
        raise ValidationError("Название должно содержать буквы.")


class PlaceFilterForm(forms.Form):
    SORT_CHOICES = [
        ("rating", "По рейтингу"),
        ("name", "По названию"),
        ("category", "По категории"),
    ]

    q = forms.CharField(
        required=False,
        max_length=100,
        label="Название или адрес",
        widget=forms.TextInput(attrs={"placeholder": "Название или адрес"}),
    )
    category_id = forms.ModelChoiceField(
        queryset=Category.objects.order_by("name"),
        required=False,
        label="Категория",
        empty_label="Все категории",
    )
    min_rating = forms.IntegerField(
        required=False,
        label="Рейтинг от",
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        widget=forms.NumberInput(attrs={"min": 0, "max": 10, "placeholder": "Рейтинг от"}),
    )
    sort = forms.ChoiceField(required=False, label="Сортировка", choices=SORT_CHOICES)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css = "form-select" if isinstance(field.widget, forms.Select) else "form-control"
            field.widget.attrs.setdefault("class", css)


class PlaceForm(forms.ModelForm):
    class Meta:
        model = Place
        fields = ["name", "category", "address", "rating", "is_available", "image"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "address": forms.TextInput(attrs={"class": "form-control"}),
            "rating": forms.NumberInput(attrs={"class": "form-control", "min": 0, "max": 10}),
            "is_available": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control", "accept": "image/*"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].validators.append(validate_has_letters)

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if image and image.size > MAX_IMAGE_SIZE:
            raise ValidationError("Размер изображения не должен превышать 2 МБ.")
        return image
