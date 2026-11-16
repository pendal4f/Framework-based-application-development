from django.urls import path

from . import inline_views

app_name = "places"
urlpatterns = [
    path("", inline_views.place_list, name="list"),
    path("<int:place_id>/", inline_views.place_detail, name="detail"),
]
