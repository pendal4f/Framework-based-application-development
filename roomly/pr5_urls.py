"""URL configuration for the PR5 inline-response checkpoint."""
from django.urls import include, path

handler404 = "homepage.inline_views.not_found"

urlpatterns = [
    path("", include("homepage.inline_urls")),
    path("places/", include("places.inline_urls")),
    path("recommendations/", include("recommendations.inline_urls")),
]
