"""PR5 views returning small HTML responses before the PR6 template migration."""
from django.http import HttpResponse
from django.utils.html import escape

from storage import load_categories, load_places


def page(title, body):
    return (
        "<!doctype html><html lang='ru'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width, initial-scale=1'>"
        f"<title>{title}</title>"
        "<link href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css' "
        "rel='stylesheet'></head><body class='container py-5'>"
        f"{body}</body></html>"
    )


def index(request):
    categories = load_categories()
    places = load_places(categories)
    links = "".join(f"<li>{escape(category.name)}</li>" for category in categories)
    body = (
        f"<h1 class='display-5'>Места рядом</h1><p>В каталоге {len(places)} мест.</p>"
        f"<ul class='list-group mb-3'>{links}</ul>"
        "<a class='btn btn-primary' href='/places/'>Каталог</a>"
    )
    return HttpResponse(page("Места рядом", body))


def not_found(request, exception=None):
    return HttpResponse("<h1>Страница не найдена</h1>", status=404)
