"""Checkpoints of earlier practices: PR5 (inline), PR6 (JSON templates), PR7 (sqlite3)."""
import pytest
from django.test import Client, override_settings

from db import database
from db.import_json import import_json


# The shared context processor reads the ORM database on every page.
pytestmark = pytest.mark.django_db


@pytest.fixture
def sql_client(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "test.sqlite3")
    import_json()
    with override_settings(ROOT_URLCONF="roomly.pr7_urls"):
        yield Client()


def test_pr7_pages_render(sql_client):
    for url in ("/", "/places/", "/places/1/", "/recommendations/",
                "/places/statistics/"):
        assert sql_client.get(url).status_code == 200, url


def test_pr7_place_search_uses_filters(sql_client):
    html = sql_client.get("/places/?q=Север&min_rating=7").content.decode()
    assert "Джаз-клуб Север" in html
    assert "Городской спортцентр" not in html


def test_pr7_missing_place_returns_404(sql_client):
    response = sql_client.get("/places/999/")
    assert response.status_code == 404
    assert "Страница не найдена" in response.content.decode()


def test_pr7_available_page_uses_weekday(sql_client):
    html = sql_client.get("/places/available/?date=2026-10-26").content.decode()
    assert "Городской спортцентр" in html
    assert "Джаз-клуб Север" not in html
    assert "Джаз-клуб Север" in sql_client.get(
        "/places/available/?date=2026-10-29").content.decode()
    assert "Доступных мест не найдено" in sql_client.get(
        "/places/available/?date=2026-10-25").content.decode()


@pytest.mark.parametrize("urlconf", ["roomly.pr5_urls", "roomly.pr6_urls"])
def test_pr5_and_pr6_checkpoints_render(urlconf):
    with override_settings(ROOT_URLCONF=urlconf):
        client = Client()
        for url in ("/", "/places/", "/places/1/", "/recommendations/"):
            assert client.get(url).status_code == 200, (urlconf, url)
        if urlconf.endswith("pr5_urls"):
            assert "bootstrap" in client.get("/").content.decode()
        else:
            assert "<html" in client.get("/").content.decode()
