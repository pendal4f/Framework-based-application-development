"""PR5 HTML-response view for recommendation data."""
from django.http import HttpResponse
from django.utils.html import escape

from homepage.inline_views import page
from storage import load_categories, load_places, load_recommendations, load_users


def recommendation_list(request):
    categories = load_categories()
    places = load_places(categories)
    users = load_users()
    recommendations = load_recommendations(users, places)
    items = "".join(
        f"<li>{escape(item.user.name)} → {escape(item.place.name)}: "
        f"{escape(item.status)}</li>"
        for item in recommendations
    )
    body = items or "<li>Пока нет рекомендаций</li>"
    content = f"<h1>Рекомендации</h1><ul class='list-group'>{body}</ul>"
    return HttpResponse(page("Рекомендации", content))
