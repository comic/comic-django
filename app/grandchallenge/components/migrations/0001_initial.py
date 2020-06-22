# Generated by Django 3.0.6 on 2020-06-22 13:06

import django.contrib.postgres.fields.jsonb
import django.db.models.deletion
import django_extensions.db.fields
from django.db import migrations, models

import grandchallenge.components.models
import grandchallenge.components.validators
import grandchallenge.core.storage


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("cases", "0024_auto_20200525_0634"),
    ]

    operations = [
        migrations.CreateModel(
            name="ComponentInterface",
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
                    models.CharField(
                        help_text="Human readable name of this input/output field.",
                        max_length=255,
                        unique=True,
                    ),
                ),
                (
                    "slug",
                    django_extensions.db.fields.AutoSlugField(
                        blank=True, editable=False, populate_from="title"
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        help_text="Description of this input/output field.",
                    ),
                ),
                (
                    "default_value",
                    django.contrib.postgres.fields.jsonb.JSONField(
                        default=None,
                        help_text="Default value for this field, only valid for inputs.",
                        null=True,
                    ),
                ),
                (
                    "kind",
                    models.CharField(
                        choices=[
                            ("STR", "String"),
                            ("INT", "Integer"),
                            ("FLT", "Float"),
                            ("BOOL", "Bool"),
                            ("2DBB", "2D bounding box"),
                            ("M2DB", "Multiple 2D bounding boxes"),
                            ("DIST", "Distance measurement"),
                            ("MDIS", "Multiple distance measurements"),
                            ("POIN", "Point"),
                            ("MPOI", "Multiple points"),
                            ("POLY", "Polygon"),
                            ("MPOL", "Multiple polygons"),
                            ("CHOI", "Choice"),
                            ("MCHO", "Multiple choice"),
                            ("IMG", "Image"),
                            ("SEG", "Segmentation"),
                            ("HMAP", "Heat Map"),
                            ("JSON", "JSON file"),
                            ("CSV", "CSV file"),
                            ("ZIP", "ZIP file"),
                        ],
                        help_text="What kind of field is this interface?",
                        max_length=4,
                    ),
                ),
                (
                    "relative_path",
                    models.CharField(
                        help_text="The path to the entity that implements this interface relative to the input or output directory.",
                        max_length=255,
                        unique=True,
                        validators=[
                            grandchallenge.components.validators.validate_safe_path
                        ],
                    ),
                ),
            ],
            options={"ordering": ("pk",)},
        ),
        migrations.CreateModel(
            name="ComponentInterfaceValue",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                (
                    "value",
                    django.contrib.postgres.fields.jsonb.JSONField(
                        default=None, null=True
                    ),
                ),
                (
                    "file",
                    models.FileField(
                        storage=grandchallenge.core.storage.ProtectedS3Storage(),
                        upload_to=grandchallenge.components.models.component_interface_value_path,
                    ),
                ),
                (
                    "image",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="cases.Image",
                    ),
                ),
                (
                    "interface",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="components.ComponentInterface",
                    ),
                ),
            ],
            options={"ordering": ("pk",)},
        ),
    ]
