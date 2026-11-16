from django.urls import path

from . import json_views as views

app_name = "recommendations"
urlpatterns = [path("", views.recommendation_list, name="list")]
