"""PR11: Django forms — filters, ModelForm create/edit, cancel, uploads."""
from datetime import timedelta
from io import BytesIO

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import Client
from django.utils import timezone
from PIL import Image

from places.models import Place
from recommendations.forms import RecommendationForm
from recommendations.models import Recommendation

pytestmark = pytest.mark.django_db

CINEMA_ID = 4      # open every day, category «Кино»
JAZZ_ID = 1        # open Thursday–Saturday, category «Музыка»
IVAN_ID = 1        # interests: Музыка, Кино
ANNA_ID = 2        # interests: Спорт, Наука


@pytest.fixture
def client():
    call_command("loaddata", "data/fixtures/demo.json", verbosity=0)
    return Client()


def next_date(weekdays, start_offset=1):
    day = timezone.localdate() + timedelta(days=start_offset)
    while day.weekday() not in weekdays:
        day += timedelta(days=1)
    return day


def form_data(**overrides):
    data = {"user": IVAN_ID, "place": CINEMA_ID,
            "visit_date": next_date(range(7)).isoformat(), "comment": "Премьера"}
    data.update(overrides)
    return data


def test_filter_form_keeps_values_and_rejects_bad_input(client):
    response = client.get("/recommendations/?place=4&sort=user&status=active")
    form = response.context["form"]
    assert form.is_valid() and form.cleaned_data["place"].pk == 4
    assert 'value="4" selected' in response.content.decode()

    response = client.get("/recommendations/?place=999&status=unknown")
    assert response.status_code == 200
    assert set(response.context["form"].errors) == {"place", "status"}


def test_place_filter_form_validates_rating(client):
    response = client.get("/places/?min_rating=15")
    assert response.status_code == 200
    assert "Проверьте значения фильтров" in response.content.decode()
    response = client.get("/places/?min_rating=abc")
    assert response.status_code == 200
    html = client.get("/places/?category_id=1").content.decode()
    assert "Джаз-клуб Север" in html and "Планетарий" not in html


def test_create_form_get_has_csrf(client):
    html = client.get("/recommendations/create/").content.decode()
    assert "csrfmiddlewaretoken" in html and 'name="visit_date"' in html


def test_create_recommendation(client):
    before = Recommendation.objects.count()
    response = client.post("/recommendations/create/", form_data())
    assert response.status_code == 302
    created = Recommendation.objects.latest("pk")
    assert Recommendation.objects.count() == before + 1
    assert created.status == Recommendation.Status.ACTIVE
    assert response["Location"] == f"/recommendations/{created.pk}/"


def test_past_date_is_rejected(client):
    past = (timezone.localdate() - timedelta(days=1)).isoformat()
    response = client.post("/recommendations/create/", form_data(visit_date=past))
    assert response.status_code == 200
    assert "прошедшую дату" in response.content.decode()


def test_far_future_date_is_rejected():
    far = timezone.localdate() + timedelta(days=400)
    call_command("loaddata", "data/fixtures/demo.json", verbosity=0)
    form = RecommendationForm(data=form_data(visit_date=far.isoformat()))
    assert not form.is_valid()
    assert "через год" in str(form.errors["visit_date"])


def test_closed_day_and_interest_rules(client):
    monday = next_date([0])
    response = client.post("/recommendations/create/",
                           form_data(place=JAZZ_ID, visit_date=monday.isoformat()))
    assert "не принимает посетителей" in response.content.decode()

    response = client.post("/recommendations/create/", form_data(user=ANNA_ID))
    assert "не входит в интересы" in response.content.decode()


def test_duplicate_active_recommendation_is_rejected(client):
    data = form_data()
    client.post("/recommendations/create/", data)
    response = client.post("/recommendations/create/", data)
    assert response.status_code == 200
    assert "уже есть активная рекомендация" in response.content.decode()


def test_cancelled_recommendation_does_not_block(client):
    data = form_data()
    client.post("/recommendations/create/", data)
    Recommendation.objects.latest("pk").cancel()
    assert client.post("/recommendations/create/", data).status_code == 302


def test_edit_recommendation(client):
    client.post("/recommendations/create/", form_data())
    recommendation = Recommendation.objects.latest("pk")
    response = client.get(f"/recommendations/{recommendation.pk}/edit/")
    assert response.context["form"].instance == recommendation
    # Saving without changes must not conflict with itself.
    response = client.post(f"/recommendations/{recommendation.pk}/edit/",
                           form_data(comment="Изменённый комментарий"))
    assert response.status_code == 302
    recommendation.refresh_from_db()
    assert recommendation.comment == "Изменённый комментарий"


def test_cancel_requires_post_and_changes_status(client):
    client.post("/recommendations/create/", form_data())
    recommendation = Recommendation.objects.latest("pk")
    url = f"/recommendations/{recommendation.pk}/cancel/"
    assert client.get(url).status_code == 405
    assert client.post(url).status_code == 302
    recommendation.refresh_from_db()
    assert recommendation.status == Recommendation.Status.CANCELLED
    # A cancelled recommendation can be neither cancelled nor edited again.
    assert client.post(url).status_code == 404
    assert client.get(f"/recommendations/{recommendation.pk}/edit/").status_code == 404


def test_missing_recommendation_returns_404(client):
    assert client.get("/recommendations/999/edit/").status_code == 404
    assert client.post("/recommendations/999/cancel/").status_code == 404


def make_image():
    buffer = BytesIO()
    Image.new("RGB", (10, 10), "teal").save(buffer, format="PNG")
    return SimpleUploadedFile("place.png", buffer.getvalue(), content_type="image/png")


def test_create_place_with_image(client, settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    response = client.post("/places/create/", {
        "name": "Арт-галерея Квадрат", "category": 1, "address": "ул. Красная, 5",
        "rating": 7, "is_available": "on", "image": make_image(),
    })
    place = Place.objects.get(name="Арт-галерея Квадрат")
    assert response["Location"] == place.get_absolute_url()
    assert place.image.name.startswith("places/")
    assert (tmp_path / place.image.name).exists()
    assert place.image.url in client.get(place.get_absolute_url()).content.decode()


def test_place_form_validation(client):
    response = client.post("/places/create/", {
        "name": "12345", "category": 1, "address": "x", "rating": 15,
    })
    html = response.content.decode()
    assert response.status_code == 200
    assert "должно содержать буквы" in html
    assert "rating" in response.context["form"].errors

    bad_file = SimpleUploadedFile("file.png", b"not an image", content_type="image/png")
    response = client.post("/places/create/", {
        "name": "Галерея", "category": 1, "address": "x", "rating": 5, "image": bad_file,
    })
    assert "image" in response.context["form"].errors


def test_edit_place_keeps_slug(client):
    url = "/places/dzhaz-klub-sever-1/edit/"
    assert client.get(url).context["form"].instance.pk == 1
    response = client.post(url, {"name": "Джаз-клуб Север", "category": 1,
                                 "address": "ул. Музыкальная, 14", "rating": 9})
    assert response["Location"] == "/places/dzhaz-klub-sever-1/"
    place = Place.objects.get(pk=1)
    assert place.address == "ул. Музыкальная, 14" and place.is_top_rated
