from django.contrib import admin
from django.urls import include, path

handler404 = "homepage.views.not_found"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("homepage.sql_urls")),
    path("places/", include("places.sql_urls")),
    path("recommendations/", include("recommendations.sql_urls")),
]
