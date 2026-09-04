"""Add Event.kind and backfill from title/description keywords."""

from django.db import migrations, models


def _infer_kind(title: str, description: str) -> str:
    haystack = f"{title} {description}".casefold()
    rules = (
        ("hackathon", ("hackaton", "hackathon", "hackatón", "datathon", "challenge")),
        ("workshop", ("taller", "workshop")),
        ("talk", ("charla", "conferencia", "keynote")),
        ("social", ("after", "birra", "networking", "adminbirra")),
    )
    for kind, keywords in rules:
        if any(keyword in haystack for keyword in keywords):
            return kind
    return "meetup"


def backfill_event_kind(apps, schema_editor) -> None:
    """Set kind on existing events from their copy."""
    event_model = apps.get_model("content", "Event")
    for event in event_model.objects.all().iterator():
        inferred = _infer_kind(event.title, event.description or "")
        if event.kind != inferred:
            event.kind = inferred
            event.save(update_fields=["kind"])


class Migration(migrations.Migration):
    dependencies = [
        ("content", "0012_event_content_eve_status_f53fb8_idx_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="kind",
            field=models.CharField(
                choices=[
                    ("meetup", "Meetup"),
                    ("talk", "Charla"),
                    ("workshop", "Taller"),
                    ("hackathon", "Hackatón"),
                    ("social", "Social"),
                ],
                default="meetup",
                max_length=20,
                verbose_name="tipo",
            ),
        ),
        migrations.RunPython(backfill_event_kind, migrations.RunPython.noop),
    ]
