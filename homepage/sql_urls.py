from django.urls import path

from . import sql_views

app_name = "homepage"
urlpatterns = [path("", sql_views.index, name="index")]
