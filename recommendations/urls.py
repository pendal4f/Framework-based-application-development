from django.urls import path

from . import views

app_name = "recommendations"
urlpatterns = [
    path("", views.recommendation_list, name="list"),
    path("<int:recommendation_id>/", views.recommendation_detail, name="detail"),
]
