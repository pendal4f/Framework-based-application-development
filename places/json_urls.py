from django.urls import path

from . import json_views as views

app_name = "places"
urlpatterns = [
    path("", views.place_list, name="list"),
    path("<int:place_id>/", views.place_detail, name="detail"),
]
