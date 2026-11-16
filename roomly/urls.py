from django.contrib import admin
from django.urls import include, path

handler404 = "homepage.views.not_found"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("homepage.urls")),
    path("places/", include("places.urls")),
    path("recommendations/", include("recommendations.urls")),
]
