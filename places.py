"""Функции для работы с каталогом мест."""

from collections.abc import Iterator


def add_place(
    places: dict[int, dict],
    name: str,
    category_id: int,
    address: str,
    rating: int,
    is_available: bool = True,
) -> int:
    """Добавить место в словарь places и вернуть его идентификатор."""
    place_id = max(places.keys(), default=0) + 1
    places[place_id] = {
        "id": place_id,
        "name": name,
        "category_id": category_id,
        "address": address,
        "rating": rating,
        "is_available": is_available,
    }
    return place_id


def iter_places(places: dict[int, dict]) -> Iterator[dict]:
    """Генератор, последовательно возвращающий данные мест."""
    for place in places.values():
        yield place


def get_place(places: dict[int, dict], place_id: int) -> dict:
    """Вернуть место по идентификатору."""
    if place_id not in places:
        raise KeyError(f"Место с id={place_id} не найдено")
    return places[place_id]


def find_places_by_category(places: dict[int, dict], category_id: int) -> list[dict]:
    """Найти места заданной категории."""
    return [place for place in iter_places(places) if place["category_id"] == category_id]


def filter_places_by_min_rating(places: dict[int, dict], min_rating: int) -> list[dict]:
    """Отобрать места с рейтингом не ниже min_rating."""
    return [place for place in iter_places(places) if place["rating"] >= min_rating]


def sort_places_by_rating(places: dict[int, dict]) -> list[dict]:
    """Вернуть места, отсортированные по убыванию рейтинга."""
    return sorted(iter_places(places), key=lambda place: place["rating"], reverse=True)
