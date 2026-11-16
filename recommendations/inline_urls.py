from django.urls import path

from . import inline_views

app_name = "recommendations"
urlpatterns = [
    path("", inline_views.recommendation_list, name="list"),
]
