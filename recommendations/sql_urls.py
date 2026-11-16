from django.urls import path

from . import sql_views

app_name = "recommendations"
urlpatterns = [path("", sql_views.recommendation_list, name="list")]
