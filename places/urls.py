from django.urls import path

from . import views

app_name = "places"
urlpatterns = [
    path("", views.place_list, name="list"),
    path("available/", views.available_places, name="available"),
    path("statistics/", views.statistics, name="statistics"),
    path("create/", views.place_create, name="create"),
    path("<slug:slug>/", views.place_detail, name="detail"),
    path("<slug:slug>/edit/", views.place_edit, name="edit"),
]
