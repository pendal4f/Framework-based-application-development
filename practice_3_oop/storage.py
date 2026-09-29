from __future__ import annotations

import json
from pathlib import Path

from models import Category, Place, Recommendation, User
from services import get_category_by_id, get_place_by_id, get_user_by_id

DATA_DIR = Path(__file__).resolve().parent / "data"
USERS_FILE = DATA_DIR / "users.json"
CATEGORIES_FILE = DATA_DIR / "categories.json"
PLACES_FILE = DATA_DIR / "places.json"
RECOMMENDATIONS_FILE = DATA_DIR / "recommendations.json"


def read_json(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, data: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def load_users(path: Path = USERS_FILE) -> list[User]:
    return [User.from_data(item) for item in read_json(path)]


def save_users(users: list[User], path: Path = USERS_FILE) -> None:
    write_json(path, [user.to_data() for user in users])


def load_categories(path: Path = CATEGORIES_FILE) -> list[Category]:
    return [Category.from_data(item) for item in read_json(path)]


def save_categories(categories: list[Category], path: Path = CATEGORIES_FILE) -> None:
    write_json(path, [category.to_data() for category in categories])


def load_places(
    categories: list[Category],
    path: Path = PLACES_FILE,
) -> list[Place]:
    places = []
    for item in read_json(path):
        places.append(
            Place(
                place_id=int(item["id"]),
                name=str(item["name"]),
                category=get_category_by_id(categories, int(item["category_id"])),
                address=str(item["address"]),
                rating=int(item["rating"]),
                is_available=bool(item.get("is_available", True)),
            )
        )
    return places


def save_places(places: list[Place], path: Path = PLACES_FILE) -> None:
    write_json(path, [place.to_data() for place in places])


def load_recommendations(
    users: list[User],
    places: list[Place],
    path: Path = RECOMMENDATIONS_FILE,
) -> list[Recommendation]:
    recommendations = []
    for item in read_json(path):
        recommendations.append(
            Recommendation(
                recommendation_id=int(item["id"]),
                user=get_user_by_id(users, int(item["user_id"])),
                place=get_place_by_id(places, int(item["place_id"])),
                is_cancelled=bool(item.get("is_cancelled", False)),
            )
        )
    return recommendations


def save_recommendations(
    recommendations: list[Recommendation],
    path: Path = RECOMMENDATIONS_FILE,
) -> None:
    write_json(path, [recommendation.to_data() for recommendation in recommendations])
