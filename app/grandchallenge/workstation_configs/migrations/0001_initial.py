# Generated by Django 2.2.6 on 2019-10-11 11:28

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="WindowPreset",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "title",
                    models.CharField(max_length=255, verbose_name="title"),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True, null=True, verbose_name="description"
                    ),
                ),
                (
                    "slug",
                    django_extensions.db.fields.AutoSlugField(
                        blank=True,
                        editable=False,
                        populate_from="title",
                        verbose_name="slug",
                    ),
                ),
                (
                    "width",
                    models.PositiveIntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(
                                limit_value=1
                            )
                        ]
                    ),
                ),
                ("center", models.IntegerField()),
            ],
            options={"ordering": ("title",), "abstract": False},
        ),
        migrations.CreateModel(
            name="WorkstationConfig",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("modified", models.DateTimeField(auto_now=True)),
                (
                    "title",
                    models.CharField(max_length=255, verbose_name="title"),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True, null=True, verbose_name="description"
                    ),
                ),
                (
                    "slug",
                    django_extensions.db.fields.AutoSlugField(
                        blank=True,
                        editable=False,
                        populate_from="title",
                        verbose_name="slug",
                    ),
                ),
                (
                    "default_orientation",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("A", "Axial"),
                            ("C", "Coronal"),
                            ("S", "Sagittal"),
                        ],
                        max_length=1,
                    ),
                ),
                (
                    "default_slab_thickness_mm",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        max_digits=4,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(
                                limit_value=0.01
                            )
                        ],
                    ),
                ),
                (
                    "default_slab_render_method",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("MAX", "Maximum"),
                            ("MIN", "Minimum"),
                            ("AVG", "Average"),
                        ],
                        max_length=3,
                    ),
                ),
                (
                    "creator",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "default_window_preset",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="workstation_default_window_presets",
                        to="workstation_configs.WindowPreset",
                    ),
                ),
                (
                    "window_presets",
                    models.ManyToManyField(
                        blank=True,
                        related_name="workstation_window_presets",
                        to="workstation_configs.WindowPreset",
                    ),
                ),
            ],
            options={"ordering": ("created", "creator"), "abstract": False},
        ),
    ]
