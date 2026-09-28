"""Функции для подбора и учёта рекомендаций мест пользователям."""

from categories import get_category
from places import get_place
from users import get_user


def get_recommendation_status(
    is_interest_match: bool, is_rating_ok: bool, is_available: bool
) -> str:
    """Вернуть текстовый статус рекомендации (функция из ПР1, без изменений логики)."""
    if not is_available:
        return "Место сейчас недоступно для посещения"
    elif not is_interest_match:
        return "Место не соответствует интересам пользователя"
    elif not is_rating_ok:
        return "Рейтинг места ниже порога рекомендации"
    else:
        return "Место рекомендовано пользователю"


def get_matching_places(
    users: dict[int, dict],
    places: dict[int, dict],
    categories: dict[int, dict],
    user_id: int,
    min_rating: int,
) -> list[dict]:
    """Подобрать места, соответствующие интересам пользователя.

    Место подходит, если название его категории входит в множество интересов
    пользователя, рейтинг не ниже min_rating и место доступно.
    """
    user = get_user(users, user_id)
    matches = []
    for place in places.values():
        category = get_category(categories, place["category_id"])
        if (
            category["name"] in user["interests"]
            and place["rating"] >= min_rating
            and place["is_available"]
        ):
            matches.append(place)
    return matches


def is_already_recommended(recommendations: list[dict], user_id: int, place_id: int) -> bool:
    """Проверить, была ли уже создана рекомендация для этой пары пользователь-место."""
    for recommendation in recommendations:
        if recommendation["user_id"] == user_id and recommendation["place_id"] == place_id:
            return True
    return False


def create_recommendation(
    recommendations: list[dict],
    users: dict[int, dict],
    places: dict[int, dict],
    categories: dict[int, dict],
    user_id: int,
    place_id: int,
) -> dict:
    """Создать рекомендацию места пользователю.

    Вызывает ValueError, если место не соответствует интересам пользователя,
    недоступно для посещения или уже было рекомендовано.
    """
    user = get_user(users, user_id)
    place = get_place(places, place_id)
    category = get_category(categories, place["category_id"])

    if is_already_recommended(recommendations, user_id, place_id):
        raise ValueError("Место уже было рекомендовано этому пользователю")
    if not place["is_available"]:
        raise ValueError("Место сейчас недоступно для посещения")
    if category["name"] not in user["interests"]:
        raise ValueError("Место не соответствует интересам пользователя")

    recommendation_id = max((rec["id"] for rec in recommendations), default=0) + 1
    recommendation = {
        "id": recommendation_id,
        "user_id": user_id,
        "place_id": place_id,
    }
    recommendations.append(recommendation)
    return recommendation


def cancel_recommendation(recommendations: list[dict], recommendation_id: int) -> bool:
    """Отменить рекомендацию по идентификатору.

    Возвращает True, если рекомендация была найдена и удалена.
    """
    for index, recommendation in enumerate(recommendations):
        if recommendation["id"] == recommendation_id:
            del recommendations[index]
            return True
    return False
