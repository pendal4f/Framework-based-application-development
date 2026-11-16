"""PR5 HTML-response views, retained to show the staged transition to templates."""
from django.http import Http404, HttpResponse
from django.utils.html import escape

from homepage.inline_views import page
from storage import load_categories, load_places


def place_list(request):
    categories = load_categories()
    places = load_places(categories)
    items = "".join(
        f"<li><a href='/places/{place.id}/'>{escape(place.name)}</a> — "
        f"{escape(place.address)}</li>"
        for place in places
    )
    body = f"<h1>Места</h1><ul class='list-group'>{items or '<li>Места не найдены</li>'}</ul>"
    return HttpResponse(page("Места", body))


def place_detail(request, place_id):
    categories = load_categories()
    place = next((item for item in load_places(categories) if item.id == place_id), None)
    if place is None:
        raise Http404("Место не найдено")
    body = (
        f"<h1>{escape(place.name)}</h1><p>{escape(place.category.name)}: "
        f"{escape(place.address)}</p>"
        f"<p>Рейтинг {place.rating}/10</p><a class='btn btn-outline-secondary' "
        "href='/places/'>К каталогу</a>"
    )
    return HttpResponse(page(place.name, body))
