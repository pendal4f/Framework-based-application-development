"""Data migration: fill slug for places created before the field existed."""
from django.db import migrations
from django.utils.text import slugify
from unidecode import unidecode


def populate_place_slugs(apps, schema_editor):
    # Historical model, independent of later changes in models.py.
    Place = apps.get_model("places", "Place")
    for place in Place.objects.order_by("pk"):
        # "Джаз-клуб Север" -> "dzhaz-klub-sever"; the pk keeps slugs unique.
        base_slug = slugify(unidecode(place.name)) or "place"
        place.slug = f"{base_slug}-{place.pk}"
        place.save(update_fields=["slug"])


class Migration(migrations.Migration):

    dependencies = [
        ("places", "0002_place_slug_rating_help"),
    ]

    operations = [
        migrations.RunPython(populate_place_slugs, migrations.RunPython.noop),
    ]
