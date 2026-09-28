import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from categories import add_category
from places import add_place
from recommendations import (
    cancel_recommendation,
    create_recommendation,
    get_matching_places,
    is_already_recommended,
)
from users import add_user


def make_data():
    users = {}
    add_user(users, "Иван Петров", ["Музыка"])
    categories = {}
    music_id = add_category(categories, "Музыка")
    sport_id = add_category(categories, "Спорт")
    places = {}
    add_place(places, "Джаз-клуб Север", music_id, "ул. Музыкальная, 12", 8)
    add_place(places, "Городской спортцентр", sport_id, "пр-т Победы, 45", 6)
    return users, places, categories


def test_get_matching_places():
    users, places, categories = make_data()
    matches = get_matching_places(users, places, categories, 1, min_rating=5)
    assert len(matches) == 1
    assert matches[0]["name"] == "Джаз-клуб Север"


def test_create_recommendation_and_duplicate_forbidden():
    users, places, categories = make_data()
    recommendations = []
    create_recommendation(recommendations, users, places, categories, 1, 1)
    assert is_already_recommended(recommendations, 1, 1)
    try:
        create_recommendation(recommendations, users, places, categories, 1, 1)
    except ValueError:
        pass
    else:
        assert False


def test_create_recommendation_without_matching_interest_raises_error():
    users, places, categories = make_data()
    recommendations = []
    try:
        create_recommendation(recommendations, users, places, categories, 1, 2)
    except ValueError:
        pass
    else:
        assert False


def test_cancel_recommendation():
    users, places, categories = make_data()
    recommendations = []
    recommendation = create_recommendation(recommendations, users, places, categories, 1, 1)
    assert cancel_recommendation(recommendations, recommendation["id"])
    assert recommendations == []
    assert not cancel_recommendation(recommendations, recommendation["id"])
