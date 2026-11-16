"""Move the PR7 SQLite data (data/places.sqlite3) into Django-managed tables.

Run after `python manage.py migrate` from the project root:
    python db/import_sqlite_to_orm.py

The source database is opened read-only. Primary keys are preserved, so the
script can be re-run: matching records are updated, nothing is duplicated.
"""
import os
import sqlite3
import sys
from datetime import date
from pathlib import Path

import django

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "roomly.settings")
django.setup()

from django.db import transaction  # noqa: E402

from places.models import Category, Place, PlaceAvailability  # noqa: E402
from recommendations.models import Recommendation  # noqa: E402
from users.models import User  # noqa: E402

SOURCE_DB = BASE_DIR / "data" / "places.sqlite3"

# PR7 recommendations had no visit date. They are moved to this demo date
# (a Thursday, when the jazz club from the source data is open).
DEFAULT_VISIT_DATE = date(2026, 10, 29)


def sqlite_weekday_to_python(weekday: int) -> int:
    """SQLite strftime('%w'): 0 = Sunday; Python date.weekday(): 0 = Monday."""
    return (weekday + 6) % 7


@transaction.atomic
def import_from_sqlite(source_db: Path = SOURCE_DB) -> dict:
    if not source_db.exists():
        raise FileNotFoundError(
            f"Исходная база не найдена: {source_db}. "
            "Создайте её командой python -m db.import_json"
        )
    with sqlite3.connect(f"file:{source_db}?mode=ro", uri=True) as source:
        source.row_factory = sqlite3.Row

        # 1. Independent entities first.
        for row in source.execute("SELECT id, name, description FROM categories"):
            Category.objects.update_or_create(
                pk=row["id"],
                defaults={"name": row["name"], "description": row["description"]},
            )
        for row in source.execute("SELECT id, name FROM users"):
            User.objects.update_or_create(pk=row["id"], defaults={"name": row["name"]})

        # 2. Interests (user_interests stored names) become a many-to-many link.
        for row in source.execute("SELECT user_id, interest FROM user_interests"):
            category, _ = Category.objects.get_or_create(name=row["interest"])
            User.objects.get(pk=row["user_id"]).interests.add(category)

        # 3. Entities that reference the ones above.
        for row in source.execute("SELECT * FROM places"):
            Place.objects.update_or_create(
                pk=row["id"],
                defaults={
                    "name": row["name"],
                    "category_id": row["category_id"],
                    "address": row["address"],
                    "rating": row["rating"],
                    "is_available": bool(row["is_available"]),
                },
            )
        for row in source.execute("SELECT * FROM place_availability"):
            PlaceAvailability.objects.update_or_create(
                place_id=row["place_id"],
                weekday=sqlite_weekday_to_python(row["weekday"]),
                defaults={"is_available": bool(row["is_available"])},
            )
        for row in source.execute("SELECT * FROM recommendations"):
            Recommendation.objects.update_or_create(
                pk=row["id"],
                defaults={
                    "user_id": row["user_id"],
                    "place_id": row["place_id"],
                    "visit_date": DEFAULT_VISIT_DATE,
                    "status": (
                        Recommendation.Status.CANCELLED if row["is_cancelled"]
                        else Recommendation.Status.ACTIVE
                    ),
                },
            )

    return {
        "categories": Category.objects.count(),
        "users": User.objects.count(),
        "places": Place.objects.count(),
        "schedule": PlaceAvailability.objects.count(),
        "recommendations": Recommendation.objects.count(),
    }


if __name__ == "__main__":
    counts = import_from_sqlite()
    print("Перенос завершён:")
    for name, total in counts.items():
        print(f"  {name}: {total}")
