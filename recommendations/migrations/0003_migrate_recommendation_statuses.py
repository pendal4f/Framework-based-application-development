"""Data migration: move the boolean is_cancelled flag into the status field."""
from django.db import migrations


def migrate_recommendation_statuses(apps, schema_editor):
    # Historical model: the state of Recommendation at this migration.
    Recommendation = apps.get_model("recommendations", "Recommendation")
    Recommendation.objects.filter(is_cancelled=True).update(status="cancelled")
    Recommendation.objects.filter(is_cancelled=False).update(status="active")


def reverse_recommendation_statuses(apps, schema_editor):
    Recommendation = apps.get_model("recommendations", "Recommendation")
    Recommendation.objects.filter(status="cancelled").update(is_cancelled=True)
    Recommendation.objects.exclude(status="cancelled").update(is_cancelled=False)


class Migration(migrations.Migration):

    dependencies = [
        ("recommendations", "0002_recommendation_status"),
    ]

    operations = [
        migrations.RunPython(
            migrate_recommendation_statuses,
            reverse_recommendation_statuses,
        ),
    ]
