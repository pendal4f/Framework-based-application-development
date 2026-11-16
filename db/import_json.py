"""Import the existing JSON catalog into the standalone SQLite database."""
import json
from pathlib import Path

from db.database import BASE_DIR, get_connection


def import_json(data_dir: Path = BASE_DIR / "data") -> None:
    with get_connection() as connection:
        connection.execute("DELETE FROM recommendations")
        connection.execute("DELETE FROM place_availability")
        connection.execute("DELETE FROM places")
        connection.execute("DELETE FROM user_interests")
        connection.execute("DELETE FROM users")
        connection.execute("DELETE FROM categories")
        for filename, table, columns in (
            ("categories.json", "categories", ("id", "name", "description")),
            ("users.json", "users", ("id", "name")),
            ("places.json", "places", (
                "id", "name", "category_id", "address", "rating", "is_available"
            )),
            ("recommendations.json", "recommendations", (
                "id", "user_id", "place_id", "is_cancelled"
            )),
        ):
            records = json.loads((data_dir / filename).read_text(encoding="utf-8"))
            placeholders = ", ".join("?" for _ in columns)
            names = ", ".join(columns)
            statement = (
                f"INSERT OR REPLACE INTO {table} ({names}) VALUES ({placeholders})"
            )
            values = [tuple(record.get(column, 0 if column.startswith("is_") else "")
                            for column in columns) for record in records]
            connection.executemany(statement, values)

        availability = json.loads(
            (data_dir / "availability.json").read_text(encoding="utf-8")
        )
        connection.executemany(
            """INSERT INTO place_availability (place_id, weekday, is_available)
               VALUES (?, ?, ?)""",
            [(item["place_id"], item["weekday"], item["is_available"])
             for item in availability],
        )

        connection.execute("DELETE FROM user_interests")
        users = json.loads((data_dir / "users.json").read_text(encoding="utf-8"))
        connection.executemany(
            "INSERT INTO user_interests (user_id, interest) VALUES (?, ?)",
            [(user["id"], interest) for user in users
             for interest in user.get("interests", [])],
        )


if __name__ == "__main__":
    import_json()
    print("JSON-данные импортированы в SQLite")
