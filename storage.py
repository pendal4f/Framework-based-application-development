"""Функции сохранения и загрузки данных проекта в формате JSON."""

import json


def load_users(filename: str) -> dict[int, dict]:
    """Загрузить пользователей из JSON-файла.

    Список интересов JSON преобразуется в множество (set) в памяти.
    Если файл отсутствует или содержит некорректный JSON, возвращается
    пустой словарь пользователей.
    """
    try:
        with open(filename, encoding="utf-8") as file:
            users_list = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    users = {}
    for user in users_list:
        user["interests"] = set(user["interests"])
        users[user["id"]] = user
    return users


def save_users(filename: str, users: dict[int, dict]) -> None:
    """Сохранить пользователей в JSON-файл (множество интересов -> список)."""
    users_list = [
        {"id": user["id"], "name": user["name"], "interests": sorted(user["interests"])}
        for user in users.values()
    ]
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(users_list, file, ensure_ascii=False, indent=2)


def load_places(filename: str) -> dict[int, dict]:
    """Загрузить места из JSON-файла.

    Если файл отсутствует или содержит некорректный JSON, возвращается
    пустой словарь мест.
    """
    try:
        with open(filename, encoding="utf-8") as file:
            places_list = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    return {place["id"]: place for place in places_list}


def save_places(filename: str, places: dict[int, dict]) -> None:
    """Сохранить места в JSON-файл."""
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(list(places.values()), file, ensure_ascii=False, indent=2)


def load_categories(filename: str) -> dict[int, dict]:
    """Загрузить категории из JSON-файла."""
    try:
        with open(filename, encoding="utf-8") as file:
            categories_list = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    return {category["id"]: category for category in categories_list}


def save_categories(filename: str, categories: dict[int, dict]) -> None:
    """Сохранить категории в JSON-файл."""
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(list(categories.values()), file, ensure_ascii=False, indent=2)


def load_recommendations(filename: str) -> list[dict]:
    """Загрузить рекомендации из JSON-файла.

    Если файл отсутствует или содержит некорректный JSON, возвращается
    пустой список рекомендаций.
    """
    try:
        with open(filename, encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_recommendations(filename: str, recommendations: list[dict]) -> None:
    """Сохранить рекомендации в JSON-файл."""
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(recommendations, file, ensure_ascii=False, indent=2)
