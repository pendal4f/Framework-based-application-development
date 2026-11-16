from django.conf import settings
from django.contrib import admin
from django.urls import include, path

handler404 = "homepage.views.not_found"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("homepage.urls")),
    path("places/", include("places.urls")),
    path("recommendations/", include("recommendations.urls")),
]

if "debug_toolbar" in settings.INSTALLED_APPS:
    from debug_toolbar.toolbar import debug_toolbar_urls

    urlpatterns += debug_toolbar_urls()
