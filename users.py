"""Функции для работы с пользователями и их интересами."""

from collections.abc import Iterator


def add_user(users: dict[int, dict], name: str, interests: list[str] | None = None) -> int:
    """Добавить пользователя в словарь users и вернуть его идентификатор.

    Интересы хранятся как множество (set), чтобы исключить повторы.
    """
    user_id = max(users.keys(), default=0) + 1
    users[user_id] = {"id": user_id, "name": name, "interests": set(interests or [])}
    return user_id


def iter_users(users: dict[int, dict]) -> Iterator[dict]:
    """Генератор, последовательно возвращающий данные пользователей."""
    for user in users.values():
        yield user


def find_user(users: dict[int, dict], query: str) -> list[dict]:
    """Найти пользователей, в имени которых встречается подстрока query."""
    query_lower = query.lower()
    return [user for user in iter_users(users) if query_lower in user["name"].lower()]


def get_user(users: dict[int, dict], user_id: int) -> dict:
    """Вернуть пользователя по идентификатору.

    Вызывает KeyError, если пользователь с таким id не найден.
    """
    if user_id not in users:
        raise KeyError(f"Пользователь с id={user_id} не найден")
    return users[user_id]


def add_interest(users: dict[int, dict], user_id: int, interest: str) -> None:
    """Добавить интерес пользователю (без повторов, за счёт множества)."""
    user = get_user(users, user_id)
    user["interests"].add(interest)


def remove_interest(users: dict[int, dict], user_id: int, interest: str) -> bool:
    """Удалить интерес пользователя. Возвращает True, если интерес был удалён."""
    user = get_user(users, user_id)
    if interest in user["interests"]:
        user["interests"].discard(interest)
        return True
    return False
