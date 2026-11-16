"""Data shared by every template (registered in settings.TEMPLATES)."""
from recommendations.models import Recommendation

from .models import Place


def site_context(request):
    return {
        "site_name": "Места рядом",
        "places_total": Place.objects.count(),
        "active_recommendations_total": Recommendation.objects.active().count(),
    }
