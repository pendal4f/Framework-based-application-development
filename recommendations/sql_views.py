"""PR7 recommendation listing backed by a relational JOIN query."""
from django.shortcuts import render

from db.database import get_connection


def recommendation_list(request):
    with get_connection() as conn:
        recommendations = conn.execute(
            """SELECT recommendations.id, users.name AS user_name,
                      places.name AS place_name, recommendations.is_cancelled
               FROM recommendations
               JOIN users ON users.id = recommendations.user_id
               JOIN places ON places.id = recommendations.place_id
               ORDER BY recommendations.id"""
        ).fetchall()
    return render(request, "recommendations/recommendation_list.html", {
        "recommendations": recommendations,
        "show_sql_nav": True,
    })
