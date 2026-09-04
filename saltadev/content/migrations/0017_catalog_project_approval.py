"""Add catalog approval fields and drop seeded community projects."""

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

SEEDED_PROJECT_TITLES = ("salta.dev", "Bot de Telegram SaltaDev")


def delete_seeded_projects(apps, schema_editor) -> None:
    """Remove the placeholder projects; the community will submit real ones."""
    catalog_model = apps.get_model("content", "CatalogEntry")
    catalog_model.objects.filter(
        kind="project", title__in=SEEDED_PROJECT_TITLES
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("content", "0016_resource_hub"),
    ]

    operations = [
        migrations.AddField(
            model_name="catalogentry",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Pendiente"),
                    ("approved", "Aprobado"),
                    ("rejected", "Rechazado"),
                ],
                default="approved",
                max_length=20,
                verbose_name="estado",
            ),
        ),
        migrations.AddField(
            model_name="catalogentry",
            name="creator",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="catalog_entries",
                to=settings.AUTH_USER_MODEL,
                verbose_name="creador",
            ),
        ),
        migrations.AddField(
            model_name="catalogentry",
            name="approved_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="approved_catalog_entries",
                to=settings.AUTH_USER_MODEL,
                verbose_name="aprobado por",
            ),
        ),
        migrations.AddField(
            model_name="catalogentry",
            name="approved_at",
            field=models.DateTimeField(
                blank=True, null=True, verbose_name="fecha de aprobación"
            ),
        ),
        migrations.AddIndex(
            model_name="catalogentry",
            index=models.Index(
                fields=["kind", "status"],
                name="content_cat_kind_status_idx",
            ),
        ),
        migrations.RunPython(delete_seeded_projects, migrations.RunPython.noop),
    ]
