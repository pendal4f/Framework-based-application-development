from django.urls import path

from . import json_views as views

app_name = "homepage"
urlpatterns = [path("", views.index, name="index")]
