from __future__ import annotations

from services import (
    cancel_recommendation,
    create_recommendation,
    get_matching_places,
    show_items,
    sort_places_by_rating,
)
from storage import (
    load_categories,
    load_places,
    load_recommendations,
    load_users,
    save_categories,
    save_places,
    save_recommendations,
    save_users,
)


def main() -> None:
    users = load_users()
    categories = load_categories()
    places = load_places(categories)
    recommendations = load_recommendations(users, places)

    print("Сервис поиска мест по интересам")
    print("\nПользователи:")
    show_items(users)
    print("\nКатегории:")
    show_items(categories)
    print("\nМеста по рейтингу:")
    show_items(sort_places_by_rating(places))

    if users:
        print("\nПодходящие места для первого пользователя:")
        show_items(get_matching_places(users, places, users[0].id, min_rating=7))

    if users and places:
        try:
            recommendation = create_recommendation(
                recommendations,
                users,
                places,
                users[0].id,
                places[0].id,
            )
            print(f"\nСоздана рекомендация: {recommendation}")
            cancel_recommendation(recommendations, recommendation.id)
            print(f"После отмены: {recommendation}")
        except ValueError as error:
            print(f"\nРекомендация не создана: {error}")

    save_users(users)
    save_categories(categories)
    save_places(places)
    save_recommendations(recommendations)


if __name__ == "__main__":
    main()
