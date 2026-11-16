"""Smoke tests for the Django pages backed by SQLite."""
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "roomly.settings")

import django

django.setup()

import pytest
from django.test import Client, override_settings

from db import database
from db.import_json import import_json


@pytest.fixture
def site_client(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "test.sqlite3")
    import_json()
    return Client()


def test_main_pages_render(site_client):
    for url in ("/", "/places/", "/places/1/", "/recommendations/",
                "/places/statistics/"):
        response = site_client.get(url)
        assert response.status_code == 200, url


def test_place_search_uses_filters(site_client):
    response = site_client.get("/places/?q=Север&min_rating=7")
    assert response.status_code == 200
    assert "Джаз-клуб Север" in response.content.decode()
    assert "Городской спортцентр" not in response.content.decode()


def test_missing_place_returns_404(site_client):
    response = site_client.get("/places/999/")
    assert response.status_code == 404
    assert "Страница не найдена" in response.content.decode()


def test_available_page_accepts_date(site_client):
    response = site_client.get("/places/available/?date=2026-10-26")
    assert response.status_code == 200
    assert "2026-10-26" in response.content.decode()
    assert "Городской спортцентр" in response.content.decode()
    assert "Джаз-клуб Север" not in response.content.decode()


def test_available_page_changes_with_selected_weekday(site_client):
    response = site_client.get("/places/available/?date=2026-10-29")
    assert "Джаз-клуб Север" in response.content.decode()

    response = site_client.get("/places/available/?date=2026-10-25")
    assert "Доступных мест не найдено" in response.content.decode()


@pytest.mark.parametrize("urlconf", ["roomly.pr5_urls", "roomly.pr6_urls"])
def test_pr5_and_pr6_checkpoints_render(urlconf):
    with override_settings(ROOT_URLCONF=urlconf):
        client = Client()
        for url in ("/", "/places/", "/places/1/", "/recommendations/"):
            response = client.get(url)
            assert response.status_code == 200, (urlconf, url)
        if urlconf.endswith("pr5_urls"):
            assert "bootstrap" in client.get("/").content.decode()
        else:
            assert "<html" in client.get("/").content.decode()
