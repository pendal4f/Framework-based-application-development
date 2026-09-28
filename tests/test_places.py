import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from places import (
    add_place,
    filter_places_by_min_rating,
    find_places_by_category,
    sort_places_by_rating,
)


def make_places():
    places = {}
    add_place(places, "Джаз-клуб Север", 1, "ул. Музыкальная, 12", 8)
    add_place(places, "Городской спортцентр", 2, "пр-т Победы, 45", 6)
    return places


def test_add_place():
    places = {}
    place_id = add_place(places, "Джаз-клуб Север", 1, "ул. Музыкальная, 12", 8)
    assert place_id == 1
    assert places[1]["category_id"] == 1


def test_find_places_by_category():
    places = make_places()
    found = find_places_by_category(places, 1)
    assert len(found) == 1
    assert found[0]["name"] == "Джаз-клуб Север"


def test_filter_places_by_min_rating():
    places = make_places()
    result = filter_places_by_min_rating(places, 7)
    assert len(result) == 1
    assert result[0]["name"] == "Джаз-клуб Север"


def test_sort_places_by_rating():
    places = make_places()
    result = sort_places_by_rating(places)
    assert [place["name"] for place in result] == [
        "Джаз-клуб Север",
        "Городской спортцентр",
    ]
