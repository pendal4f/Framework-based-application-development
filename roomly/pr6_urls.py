"""URL configuration for the PR6 Django-template checkpoint."""
from django.urls import include, path

handler404 = "homepage.views.not_found"

urlpatterns = [
    path("", include("homepage.urls")),
    path("places/", include("places.urls")),
    path("recommendations/", include("recommendations.urls")),
]
