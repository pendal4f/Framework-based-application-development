from __future__ import annotations

from models import Category, Place, Recommendation, User


DomainObject = User | Category | Place | Recommendation


def next_id(items: list[DomainObject]) -> int:
    return max((item.id for item in items), default=0) + 1


def get_user_by_id(users: list[User], user_id: int) -> User:
    for user in users:
        if user.id == user_id:
            return user
    raise ValueError(f"Пользователь с id {user_id} не найден")


def get_category_by_id(categories: list[Category], category_id: int) -> Category:
    for category in categories:
        if category.id == category_id:
            return category
    raise ValueError(f"Категория с id {category_id} не найдена")


def get_place_by_id(places: list[Place], place_id: int) -> Place:
    for place in places:
        if place.id == place_id:
            return place
    raise ValueError(f"Место с id {place_id} не найдено")


def add_user(users: list[User], name: str, interests: list[str] | None = None) -> User:
    user = User(next_id(users), name, interests)
    users.append(user)
    return user


def add_category(categories: list[Category], name: str, description: str = "") -> Category:
    category = Category(next_id(categories), name, description)
    categories.append(category)
    return category


def add_place(
    places: list[Place],
    name: str,
    category: Category,
    address: str,
    rating: int,
    is_available: bool = True,
) -> Place:
    place = Place(next_id(places), name, category, address, rating, is_available)
    places.append(place)
    return place


def find_users(users: list[User], query: str) -> list[User]:
    lowered_query = query.lower()
    return [user for user in users if lowered_query in user.name.lower()]


def find_category_by_name(categories: list[Category], name: str) -> Category | None:
    for category in categories:
        if category.matches(name):
            return category
    return None


def find_places_by_category(places: list[Place], category: Category) -> list[Place]:
    return [place for place in places if place.matches_category(category)]


def filter_places_by_min_rating(places: list[Place], min_rating: int) -> list[Place]:
    return [place for place in places if place.rating >= min_rating]


def sort_places_by_rating(places: list[Place]) -> list[Place]:
    return sorted(places, key=lambda place: place.rating, reverse=True)


def get_matching_places(
    users: list[User],
    places: list[Place],
    user_id: int,
    min_rating: int,
) -> list[Place]:
    user = get_user_by_id(users, user_id)
    return [
        place
        for place in places
        if any(place.is_suitable_for_interest(interest, min_rating) for interest in user.interests)
    ]


def is_already_recommended(
    recommendations: list[Recommendation],
    user: User,
    place: Place,
) -> bool:
    return any(
        recommendation.user.id == user.id
        and recommendation.place.id == place.id
        and not recommendation.is_cancelled
        for recommendation in recommendations
    )


def create_recommendation(
    recommendations: list[Recommendation],
    users: list[User],
    places: list[Place],
    user_id: int,
    place_id: int,
) -> Recommendation:
    user = get_user_by_id(users, user_id)
    place = get_place_by_id(places, place_id)

    if is_already_recommended(recommendations, user, place):
        raise ValueError("Место уже рекомендовано этому пользователю")
    if not place.is_available:
        raise ValueError("Место сейчас недоступно")
    if not user.has_interest(place.category.name):
        raise ValueError("Категория места не соответствует интересам пользователя")

    recommendation = Recommendation(next_id(recommendations), user, place)
    recommendations.append(recommendation)
    return recommendation


def cancel_recommendation(recommendations: list[Recommendation], recommendation_id: int) -> None:
    for recommendation in recommendations:
        if recommendation.id == recommendation_id:
            recommendation.cancel()
            return
    raise ValueError(f"Рекомендация с id {recommendation_id} не найдена")


def show_items(items: list[DomainObject]) -> None:
    for item in items:
        print(item)
