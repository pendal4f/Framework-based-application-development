"""URL configuration for the PR7 SQLite (sqlite3) checkpoint."""
from django.urls import include, path

handler404 = "homepage.views.not_found"

urlpatterns = [
    path("", include("homepage.sql_urls")),
    path("places/", include("places.sql_urls")),
    path("recommendations/", include("recommendations.sql_urls")),
]
