from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("wagtailcore", "0078_referenceindex"),
    ]

    operations = [
        migrations.CreateModel(
            name="ReviewedPage",
            fields=[
                (
                    "page_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="wagtailcore.page",
                    ),
                ),
                ("last_review_date", models.DateField(blank=True, null=True)),
                (
                    "current_version_ref",
                    models.CharField(
                        blank=True, max_length=20, verbose_name="current version ref"
                    ),
                ),
                (
                    "current_version_compiled_by",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        verbose_name="current version compiled by",
                    ),
                ),
                ("next_review_date", models.DateField(editable=False, null=True)),
                (
                    "custom_review_frequency",
                    models.PositiveIntegerField(editable=False, null=True),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("wagtailcore.page", models.Model),
        ),
        migrations.CreateModel(
            name="SimplePage",
            fields=[
                (
                    "page_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="wagtailcore.page",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("wagtailcore.page",),
        ),
    ]
