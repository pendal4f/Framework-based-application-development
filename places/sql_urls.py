from django.urls import path

from . import sql_views

app_name = "places"
urlpatterns = [
    path("", sql_views.place_list, name="list"),
    path("available/", sql_views.available_places, name="available"),
    path("statistics/", sql_views.statistics, name="statistics"),
    path("<int:place_id>/", sql_views.place_detail, name="detail"),
]
