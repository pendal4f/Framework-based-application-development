"""PR7 views that read relational data with parameterized sqlite3 queries."""
from datetime import date

from django.http import Http404
from django.shortcuts import render

from db.database import get_connection


def place_list(request):
    query = request.GET.get("q", "").strip()
    category_id = request.GET.get("category_id", "").strip()
    min_rating = request.GET.get("min_rating", "").strip()
    sql = """SELECT places.*, categories.name AS category_name
             FROM places JOIN categories ON categories.id = places.category_id
             WHERE places.name LIKE ? AND (? = '' OR places.category_id =?)
               AND (? = '' OR places.rating >= ?)
             ORDER BY places.rating DESC, places.name"""
    with get_connection() as conn:
        places = conn.execute(
            sql,
            (f"%{query}%", category_id, category_id,
             min_rating, min_rating or 0),
        ).fetchall()
        categories = conn.execute(
            "SELECT id, name FROM categories ORDER BY name"
        ).fetchall()
    return render(request, "places/place_list.html", {
        "places": places,
        "categories": categories,
        "query": query,
        "selected_category": category_id,
        "min_rating": min_rating,
        "show_sql_nav": True,
    })


def place_detail(request, place_id):
    with get_connection() as conn:
        place = conn.execute(
            """SELECT places.*, categories.name AS category_name
               FROM places JOIN categories ON categories.id = places.category_id
               WHERE places.id = ?""",
            (place_id,),
        ).fetchone()
    if place is None:
        raise Http404("Место не найдено")
    return render(request, "places/place_detail.html", {
        "place": place,
        "show_sql_nav": True,
    })


def available_places(request):
    try:
        selected_date = date.fromisoformat(
            request.GET.get("date", date.today().isoformat())
        )
    except ValueError:
        selected_date = date.today()
    sqlite_weekday = (selected_date.weekday() + 1) % 7
    with get_connection() as conn:
        places = conn.execute(
            """SELECT places.*, categories.name AS category_name
               FROM places JOIN categories ON categories.id = places.category_id
               JOIN place_availability
                 ON place_availability.place_id = places.id
               WHERE place_availability.weekday = ?
                 AND place_availability.is_available = 1
                 AND places.is_available = 1
               ORDER BY places.rating DESC""",
            (sqlite_weekday,),
        ).fetchall()
    return render(request, "places/available.html", {
        "places": places,
        "selected_date": selected_date.isoformat(),
        "show_sql_nav": True,
    })


def statistics(request):
    with get_connection() as conn:
        rows = conn.execute(
            """WITH place_stats AS (
                   SELECT category_id, COUNT(*) AS places_count,
                          SUM(is_available) AS available_count,
                          ROUND(AVG(rating), 1) AS average_rating
                   FROM places GROUP BY category_id
               ), recommendation_stats AS (
                   SELECT places.category_id, COUNT(recommendations.id)
                            AS recommendations_count
                   FROM places LEFT JOIN recommendations
                     ON recommendations.place_id = places.id
                     AND recommendations.is_cancelled = 0
                   GROUP BY places.category_id
               )
               SELECT categories.name AS category_name,
                      COALESCE(place_stats.places_count, 0) AS places_count,
                      COALESCE(place_stats.available_count, 0) AS available_count,
                      place_stats.average_rating,
                      COALESCE(recommendation_stats.recommendations_count, 0)
                        AS recommendations_count
               FROM categories
               LEFT JOIN place_stats ON place_stats.category_id = categories.id
               LEFT JOIN recommendation_stats
                 ON recommendation_stats.category_id = categories.id
               ORDER BY places_count DESC, categories.name"""
        ).fetchall()
    return render(request, "places/statistics.html", {
        "rows": rows,
        "show_sql_nav": True,
    })
