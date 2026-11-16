from django.urls import path

from . import views

app_name = "recommendations"
urlpatterns = [
    path("", views.recommendation_list, name="list"),
    path("create/", views.recommendation_create, name="create"),
    path("<int:recommendation_id>/", views.recommendation_detail, name="detail"),
    path("<int:recommendation_id>/edit/", views.recommendation_edit, name="edit"),
    path("<int:recommendation_id>/cancel/", views.recommendation_cancel, name="cancel"),
]
