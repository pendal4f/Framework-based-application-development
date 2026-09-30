from pathlib import Path
import sys
import tempfile
import unittest

PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))

from models import Category, Place, Recommendation, User
from services import (
    cancel_recommendation,
    create_recommendation,
    get_matching_places,
    is_already_recommended,
)
from storage import (
    load_categories,
    load_places,
    load_recommendations,
    load_users,
    save_recommendations,
)


class OopProjectTest(unittest.TestCase):
    def test_objects_have_string_representation(self) -> None:
        category = Category(1, "Музыка", "Музыкальные места")
        user = User(1, "Иван Петров", ["Музыка"])
        place = Place(1, "Джаз-клуб Север", category, "ул. Музыкальная, 12", 8)
        recommendation = Recommendation(1, user, place)

        self.assertIn("Иван Петров", str(user))
        self.assertIn("Музыка", str(category))
        self.assertIn("Джаз-клуб Север", str(place))
        self.assertIn("активна", str(recommendation))

    def test_user_interest_methods(self) -> None:
        user = User(1, "Иван Петров")

        user.add_interest("Музыка")

        self.assertTrue(user.has_interest("Музыка"))
        self.assertTrue(user.remove_interest("Музыка"))
        self.assertFalse(user.has_interest("Музыка"))

    def test_get_matching_places_uses_objects(self) -> None:
        music = Category(1, "Музыка")
        sport = Category(2, "Спорт")
        users = [User(1, "Иван Петров", ["Музыка"])]
        places = [
            Place(1, "Джаз-клуб Север", music, "ул. Музыкальная, 12", 8),
            Place(2, "Городской спортцентр", sport, "пр-т Победы, 45", 9),
        ]

        matches = get_matching_places(users, places, 1, min_rating=7)

        self.assertEqual(matches, [places[0]])

    def test_create_recommendation_links_objects_and_forbids_duplicate(self) -> None:
        category = Category(1, "Музыка")
        users = [User(1, "Иван Петров", ["Музыка"])]
        places = [Place(1, "Джаз-клуб Север", category, "ул. Музыкальная, 12", 8)]
        recommendations: list[Recommendation] = []

        recommendation = create_recommendation(recommendations, users, places, 1, 1)

        self.assertIs(recommendation.user, users[0])
        self.assertIs(recommendation.place, places[0])
        self.assertTrue(is_already_recommended(recommendations, users[0], places[0]))
        with self.assertRaises(ValueError):
            create_recommendation(recommendations, users, places, 1, 1)

    def test_cancel_recommendation_changes_status(self) -> None:
        category = Category(1, "Музыка")
        user = User(1, "Иван Петров", ["Музыка"])
        place = Place(1, "Джаз-клуб Север", category, "ул. Музыкальная, 12", 8)
        recommendations = [Recommendation(1, user, place)]

        cancel_recommendation(recommendations, 1)

        self.assertEqual(recommendations[0].status, "отменена")

    def test_json_loads_objects_and_saves_links(self) -> None:
        users = load_users(PROJECT_DIR / "data" / "users.json")
        categories = load_categories(PROJECT_DIR / "data" / "categories.json")
        places = load_places(categories, PROJECT_DIR / "data" / "places.json")
        recommendations = load_recommendations(
            users,
            places,
            PROJECT_DIR / "data" / "recommendations.json",
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_file = Path(tmp_dir) / "recommendations.json"
            save_recommendations(recommendations, output_file)
            text = output_file.read_text(encoding="utf-8")

        self.assertIsInstance(recommendations[0].user, User)
        self.assertIsInstance(recommendations[0].place, Place)
        self.assertIn('"user_id": 1', text)
        self.assertIn('"place_id": 1', text)


if __name__ == "__main__":
    unittest.main()
