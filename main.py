"""Точка запуска сервиса поиска мест по интересам."""

from categories import find_category_by_name
from places import filter_places_by_min_rating, find_places_by_category, sort_places_by_rating
from recommendations import (
    cancel_recommendation,
    create_recommendation,
    get_matching_places,
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
from users import add_interest
from utils import describe_function, input_int

USERS_FILE = "data/users.json"
CATEGORIES_FILE = "data/categories.json"
PLACES_FILE = "data/places.json"
RECOMMENDATIONS_FILE = "data/recommendations.json"


def show_users(users: dict[int, dict]) -> None:
    """Вывести список пользователей с их интересами."""
    if not users:
        print("Список пользователей пуст.")
        return
    for user in users.values():
        interests = ", ".join(sorted(user["interests"])) or "нет интересов"
        print(f'{user["id"]}. {user["name"]} — интересы: {interests}')


def show_categories(categories: dict[int, dict]) -> None:
    """Вывести список категорий."""
    if not categories:
        print("Список категорий пуст.")
        return
    for category in categories.values():
        print(f'{category["id"]}. {category["name"]} — {category["description"]}')


def show_places(places: dict[int, dict], categories: dict[int, dict]) -> None:
    """Вывести список мест."""
    if not places:
        print("Каталог мест пуст.")
        return
    for place in places.values():
        category = categories.get(place["category_id"], {})
        category_name = category.get("name", "неизвестная категория")
        status = "доступно" if place["is_available"] else "недоступно"
        print(
            f'{place["id"]}. {place["name"]} ({category_name}) — '
            f'{place["address"]}, рейтинг {place["rating"]}, {status}'
        )


def show_recommendations(
    recommendations: list[dict], users: dict[int, dict], places: dict[int, dict]
) -> None:
    """Вывести список рекомендаций с указанием пользователя и места."""
    if not recommendations:
        print("Рекомендаций пока нет.")
        return
    for recommendation in recommendations:
        user = users.get(recommendation["user_id"], {})
        place = places.get(recommendation["place_id"], {})
        user_name = user.get("name", "неизвестный пользователь")
        place_name = place.get("name", "неизвестное место")
        print(f'{recommendation["id"]}. {user_name} → {place_name}')


def print_menu() -> None:
    """Вывести меню приложения."""
    print("\n=== Сервис поиска мест по интересам ===")
    print("1. Показать пользователей")
    print("2. Добавить интерес пользователю")
    print("3. Показать категории")
    print("4. Показать места")
    print("5. Найти места по категории")
    print("6. Показать места с рейтингом не ниже N")
    print("7. Показать места по убыванию рейтинга")
    print("8. Подобрать места по интересам пользователя")
    print("9. Создать рекомендацию")
    print("10. Отменить рекомендацию")
    print("11. Показать все рекомендации")
    print("12. Информация о функции (интроспекция)")
    print("0. Выход")


def main() -> None:
    """Точка запуска приложения: цикл меню и вызов функций проекта."""
    users = load_users(USERS_FILE)
    categories = load_categories(CATEGORIES_FILE)
    places = load_places(PLACES_FILE)
    recommendations = load_recommendations(RECOMMENDATIONS_FILE)

    while True:
        print_menu()
        choice = input("Выберите действие: ").strip()

        if choice == "0":
            save_users(USERS_FILE, users)
            save_categories(CATEGORIES_FILE, categories)
            save_places(PLACES_FILE, places)
            save_recommendations(RECOMMENDATIONS_FILE, recommendations)
            print("Данные сохранены. До встречи!")
            break

        elif choice == "1":
            show_users(users)

        elif choice == "2":
            user_id = input_int("Идентификатор пользователя: ")
            interest = input("Интерес: ")
            try:
                add_interest(users, user_id, interest)
                print("Интерес добавлен.")
            except KeyError as error:
                print(error)

        elif choice == "3":
            show_categories(categories)

        elif choice == "4":
            show_places(places, categories)

        elif choice == "5":
            category_name = input("Категория: ")
            category = find_category_by_name(categories, category_name)
            if category is None:
                print("Категория не найдена.")
                continue
            for place in find_places_by_category(places, category["id"]):
                print(f'{place["id"]}. {place["name"]} — {place["address"]}')

        elif choice == "6":
            min_rating = input_int("Минимальный рейтинг: ")
            for place in filter_places_by_min_rating(places, min_rating):
                print(f'{place["name"]} — рейтинг {place["rating"]}')

        elif choice == "7":
            for place in sort_places_by_rating(places):
                print(f'{place["rating"]} — {place["name"]}')

        elif choice == "8":
            user_id = input_int("Идентификатор пользователя: ")
            min_rating = input_int("Минимальный рейтинг: ")
            try:
                matches = get_matching_places(users, places, categories, user_id, min_rating)
                if not matches:
                    print("Подходящих мест не найдено.")
                for place in matches:
                    category = categories.get(place["category_id"], {})
                    print(f'{place["id"]}. {place["name"]} ({category.get("name", "?")})')
            except KeyError as error:
                print(error)

        elif choice == "9":
            user_id = input_int("Идентификатор пользователя: ")
            place_id = input_int("Идентификатор места: ")
            try:
                recommendation = create_recommendation(
                    recommendations, users, places, categories, user_id, place_id,
                )
                print(f'Рекомендация создана, id={recommendation["id"]}')
            except (KeyError, ValueError) as error:
                print(f"Не удалось создать рекомендацию: {error}")

        elif choice == "10":
            recommendation_id = input_int("Идентификатор рекомендации: ")
            if cancel_recommendation(recommendations, recommendation_id):
                print("Рекомендация отменена.")
            else:
                print("Рекомендация не найдена.")

        elif choice == "11":
            show_recommendations(recommendations, users, places)

        elif choice == "12":
            print(describe_function(create_recommendation))

        else:
            print("Неизвестный пункт меню, попробуйте снова.")


if __name__ == "__main__":
    main()
