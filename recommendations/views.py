from django.shortcuts import render

from storage import load_categories, load_places, load_recommendations, load_users


def recommendation_list(request):
    categories = load_categories()
    places = load_places(categories)
    users = load_users()
    recommendations = load_recommendations(users, places)
    return render(request, "recommendations/recommendation_list.html", {
        "recommendations": recommendations,
    })
