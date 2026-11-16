"""URL configuration for the PR6 Django-template checkpoint."""
from django.urls import include, path

handler404 = "homepage.json_views.not_found"

urlpatterns = [
    path("", include("homepage.json_urls")),
    path("places/", include("places.json_urls")),
    path("recommendations/", include("recommendations.json_urls")),
]
