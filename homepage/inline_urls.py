from django.urls import path

from . import inline_views

app_name = "homepage"
urlpatterns = [path("", inline_views.index, name="index")]
