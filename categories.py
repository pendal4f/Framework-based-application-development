"""Функции для работы с категориями мест."""

from collections.abc import Iterator


def add_category(categories: dict[int, dict], name: str, description: str = "") -> int:
    """Добавить категорию и вернуть её идентификатор."""
    category_id = max(categories.keys(), default=0) + 1
    categories[category_id] = {
        "id": category_id,
        "name": name,
        "description": description,
    }
    return category_id


def iter_categories(categories: dict[int, dict]) -> Iterator[dict]:
    """Генератор, последовательно возвращающий категории."""
    for category in categories.values():
        yield category


def get_category(categories: dict[int, dict], category_id: int) -> dict:
    """Вернуть категорию по идентификатору."""
    if category_id not in categories:
        raise KeyError(f"Категория с id={category_id} не найдена")
    return categories[category_id]


def find_category_by_name(categories: dict[int, dict], name: str) -> dict | None:
    """Найти категорию по названию без учёта регистра."""
    name_lower = name.lower()
    for category in iter_categories(categories):
        if category["name"].lower() == name_lower:
            return category
    return None
