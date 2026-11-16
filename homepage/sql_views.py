"""PR7 homepage view backed by SQLite queries."""
from django.shortcuts import render

from db.database import get_connection


def index(request):
    with get_connection() as connection:
        categories = connection.execute(
            "SELECT id, name, description FROM categories ORDER BY name"
        ).fetchall()
        places_count = connection.execute(
            "SELECT COUNT(*) AS total FROM places"
        ).fetchone()["total"]
    return render(request, "homepage/index.html", {
        "categories": categories,
        "places_count": places_count,
        "show_sql_nav": True,
    })
