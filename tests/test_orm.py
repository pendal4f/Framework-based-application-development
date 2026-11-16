"""PR9-PR10: models, relations, manager, statuses and ORM-backed pages."""
from datetime import date

import pytest
from django.core.management import call_command
from django.db.models import ProtectedError
from django.test import Client

from places.models import Category, Place
from recommendations.models import Recommendation
from users.models import User

pytestmark = pytest.mark.django_db


@pytest.fixture
def demo_data():
    call_command("loaddata", "data/fixtures/demo.json", verbosity=0)


@pytest.fixture
def client(demo_data):
    return Client()


def test_fixture_and_relations(demo_data):
    assert Place.objects.count() == 6
    recommendation = Recommendation.objects.select_related("user", "place").get(pk=1)
    assert recommendation.user.name == "Иван Петров"
    assert recommendation.place.name == "Джаз-клуб Север"
    # Reverse relations through related_name.
    assert recommendation in recommendation.place.recommendations.all()
    assert recommendation in recommendation.user.recommendations.all()
    assert set(User.objects.get(pk=1).interests.values_list("name", flat=True)) == {
        "Музыка", "Кино"}


def test_protect_keeps_recommendation_history(demo_data):
    with pytest.raises(ProtectedError):
        Place.objects.get(pk=1).delete()
    with pytest.raises(ProtectedError):
        Category.objects.get(name="Музыка").delete()


def test_crud_through_orm(demo_data):
    category = Category.objects.create(name="Театр")
    place = Place.objects.create(name="Драмтеатр", category=category,
                                 address="пл. Театральная, 1", rating=8)
    place.rating = 9
    place.save()
    place.refresh_from_db()
    assert place.rating == 9
    place.delete()
    assert not Place.objects.filter(name="Драмтеатр").exists()


def test_main_pages_render(client):
    for url in ("/", "/places/", "/places/dzhaz-klub-sever-1/", "/places/available/",
                "/places/statistics/", "/recommendations/", "/recommendations/1/"):
        assert client.get(url).status_code == 200, url


def test_missing_objects_return_404(client):
    for url in ("/places/net-takogo-mesta/", "/recommendations/999/"):
        response = client.get(url)
        assert response.status_code == 404
        assert "Страница не найдена" in response.content.decode()


def test_place_search_by_name_or_address(client):
    html = client.get("/places/?q=Север&min_rating=7").content.decode()
    assert "Джаз-клуб Север" in html
    assert "Городской спортцентр" not in html
    assert "Городской спортцентр" in client.get("/places/?q=Победы").content.decode()


def test_place_list_sorting(client):
    html = client.get("/places/?sort=name").content.decode()
    assert html.index("Бассейн Волна") < html.index("Планетарий")
    # Unknown sort value falls back to rating order without errors.
    assert client.get("/places/?sort=drop_table").status_code == 200


def test_available_places_follow_weekday_schedule(client):
    html = client.get("/places/available/?date=2026-10-26").content.decode()
    assert "Городской спортцентр" in html
    assert "Джаз-клуб Север" not in html
    assert "Джаз-клуб Север" in client.get(
        "/places/available/?date=2026-10-29").content.decode()
    # The lecture hall is open by schedule but globally unavailable.
    assert "Лекторий Космос" not in client.get(
        "/places/available/?date=2026-10-29").content.decode()
    html = client.get("/places/available/?date=не-дата").content.decode()
    assert "Укажите корректную дату" in html


def test_statistics_counts_categories_without_places(client):
    Category.objects.create(name="Пустая категория")
    response = client.get("/places/statistics/")
    rows = {row["name"]: row for row in response.context["rows"].values(
        "name", "places_count", "recommendations_count")}
    assert rows["Пустая категория"]["places_count"] == 0
    assert rows["Музыка"]["recommendations_count"] == Recommendation.objects.filter(
        place__category__name="Музыка").active().count()


def test_recommendation_filters_sort_and_pagination(client):
    response = client.get("/recommendations/")
    assert response.context["page_obj"].paginator.num_pages == 3
    assert "?page=2" in response.content.decode()

    response = client.get("/recommendations/?place=4&sort=date")
    dates = [item["visit_date"] for item in response.context["recommendations"]]
    assert dates == sorted(dates) and len(dates) == 3

    response = client.get("/recommendations/?user=3&status=active")
    assert all(item["status"] == "active" and item["user_name"] == "Мария Соколова"
               for item in response.context["recommendations"])

    response = client.get("/recommendations/?status=not_cancelled")
    assert response.context["page_obj"].paginator.count == 10

    response = client.get(f"/recommendations/?date={date(2026, 11, 21)}")
    assert response.context["page_obj"].paginator.count == 2

    response = client.get("/recommendations/?date=bad&page=abc&sort=unknown")
    assert response.status_code == 200
    assert "Укажите корректную дату" in response.content.decode()
    assert response.context["page_obj"].number == 1


def test_pagination_keeps_filters(client):
    html = client.get("/recommendations/?sort=user&status=active").content.decode()
    assert "sort=user&amp;status=active&amp;page=2" in html


def test_manager_methods(demo_data):
    assert Recommendation.objects.active().count() == 9
    assert Recommendation.objects.cancelled().count() == 2
    assert Recommendation.objects.completed().count() == 1
    assert Recommendation.objects.active().for_date(date(2026, 11, 21)).count() == 1


def test_cancel_keeps_record(demo_data):
    recommendation = Recommendation.objects.get(pk=2)
    recommendation.cancel()
    recommendation.refresh_from_db()
    assert recommendation.status == Recommendation.Status.CANCELLED


def test_slug_and_absolute_url(demo_data):
    category = Category.objects.get(name="Наука")
    place = Place.objects.create(name="Музей Науки", category=category,
                                 address="ул. Опытная, 2", rating=6)
    assert place.slug == f"muzei-nauki-{place.pk}"
    assert place.get_absolute_url() == f"/places/muzei-nauki-{place.pk}/"
    place.name = "Новый музей"
    place.save()
    place.refresh_from_db()
    assert place.slug == f"muzei-nauki-{place.pk}"  # the URL stays stable


def test_generated_field_follows_rating(demo_data):
    place = Place.objects.get(pk=2)
    assert place.is_top_rated is False
    place.rating = 9
    place.save()
    place.refresh_from_db()
    assert place.is_top_rated is True


def test_admin_pages(admin_client, demo_data):
    for url in ("/admin/", "/admin/places/place/", "/admin/places/place/1/change/",
                "/admin/users/user/1/change/", "/admin/recommendations/recommendation/",
                "/admin/places/category/"):
        assert admin_client.get(url).status_code == 200, url
    html = admin_client.get(
        "/admin/recommendations/recommendation/?q=Планетарий").content.decode()
    assert "Планетарий" in html and "Джаз-клуб Север" not in html


def test_admin_cancel_action(admin_client, demo_data):
    admin_client.post("/admin/recommendations/recommendation/", {
        "action": "mark_cancelled", "_selected_action": ["2", "3"]})
    assert set(Recommendation.objects.cancelled().values_list("pk", flat=True)) >= {2, 3}


def test_context_processor(client):
    html = client.get("/").content.decode()
    assert "мест в каталоге: 6" in html
