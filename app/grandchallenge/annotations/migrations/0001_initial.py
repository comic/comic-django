# Generated by Django 3.1.1 on 2020-12-02 13:25

import uuid

import django.contrib.postgres.fields
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("cases", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="LandmarkAnnotationSet",
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
                ("modified", models.DateTimeField(auto_now=True)),
                (
                    "created",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                (
                    "grader",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created"],
                "get_latest_by": "created",
                "abstract": False,
                "unique_together": {("grader", "created")},
            },
        ),
        migrations.CreateModel(
            name="PolygonAnnotationSet",
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
                ("modified", models.DateTimeField(auto_now=True)),
                (
                    "created",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                ("name", models.CharField(max_length=255)),
                (
                    "grader",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "image",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="cases.image",
                    ),
                ),
            ],
            options={
                "ordering": ["-created"],
                "get_latest_by": "created",
                "abstract": False,
                "unique_together": {("image", "grader", "created", "name")},
            },
        ),
        migrations.CreateModel(
            name="SinglePolygonAnnotation",
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
                    "value",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=django.contrib.postgres.fields.ArrayField(
                            base_field=models.FloatField(), size=2
                        ),
                        size=None,
                    ),
                ),
                ("z", models.FloatField(blank=True, null=True)),
                ("interpolated", models.BooleanField(default=False)),
                (
                    "annotation_set",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="annotations.polygonannotationset",
                    ),
                ),
            ],
            options={
                "ordering": ["-created"],
                "get_latest_by": "created",
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="RetinaImagePathologyAnnotation",
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
                ("modified", models.DateTimeField(auto_now=True)),
                (
                    "created",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                (
                    "rf_present",
                    models.BooleanField(
                        default=False,
                        help_text="Are retinal pathologies present in this image?",
                    ),
                ),
                (
                    "oda_present",
                    models.BooleanField(
                        help_text="Are optic disc abnormalitites present in this image?"
                    ),
                ),
                (
                    "myopia_present",
                    models.BooleanField(
                        help_text="Is myopia present in this image?"
                    ),
                ),
                (
                    "other_present",
                    models.BooleanField(
                        help_text="Are other findings present in this image?"
                    ),
                ),
                (
                    "grader",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "image",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="cases.image",
                    ),
                ),
            ],
            options={
                "ordering": ["-created"],
                "get_latest_by": "created",
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="OctRetinaImagePathologyAnnotation",
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
                ("modified", models.DateTimeField(auto_now=True)),
                (
                    "created",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                (
                    "macular",
                    models.BooleanField(
                        default=False,
                        help_text="Are pathologies present in macular OCT?",
                    ),
                ),
                (
                    "myopia",
                    models.BooleanField(
                        default=False,
                        help_text="Are myopia related pathologies present?",
                    ),
                ),
                (
                    "optic_disc",
                    models.BooleanField(
                        default=False,
                        help_text="Are pathologies present in optic disc OCT?",
                    ),
                ),
                (
                    "other",
                    models.BooleanField(
                        default=False,
                        help_text="Are other pathologies present in this image?",
                    ),
                ),
                (
                    "layers",
                    models.BooleanField(
                        default=False,
                        help_text="Are retinal layers annotated?",
                    ),
                ),
                (
                    "grader",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "image",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="cases.image",
                    ),
                ),
            ],
            options={
                "ordering": ["-created"],
                "get_latest_by": "created",
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="ImageTextAnnotation",
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
                ("modified", models.DateTimeField(auto_now=True)),
                (
                    "created",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                ("text", models.TextField()),
                (
                    "grader",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "image",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="cases.image",
                    ),
                ),
            ],
            options={
                "ordering": ["-created"],
                "get_latest_by": "created",
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="ImageQualityAnnotation",
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
                ("modified", models.DateTimeField(auto_now=True)),
                (
                    "created",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                (
                    "quality",
                    models.CharField(
                        choices=[
                            ("U", "Cannot grade"),
                            ("F", "Fair"),
                            ("G", "Good"),
                        ],
                        help_text="How do you rate the quality of the image?",
                        max_length=1,
                    ),
                ),
                (
                    "quality_reason",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("BP", "Bad photo"),
                            ("CA", "Cataract"),
                            ("PM", "Poor mydriasis"),
                        ],
                        help_text="If the quality is not good, why not?",
                        max_length=2,
                        null=True,
                    ),
                ),
                (
                    "grader",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "image",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="cases.image",
                    ),
                ),
            ],
            options={
                "ordering": ["-created"],
                "get_latest_by": "created",
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="ImagePathologyAnnotation",
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
                ("modified", models.DateTimeField(auto_now=True)),
                (
                    "created",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                (
                    "pathology",
                    models.CharField(
                        choices=[
                            ("C", "Cannot grade"),
                            ("A", "Absent"),
                            ("Q", "Questionable"),
                            ("P", "Present"),
                        ],
                        help_text="Is there a pathology present in the image?",
                        max_length=1,
                    ),
                ),
                (
                    "grader",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "image",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="cases.image",
                    ),
                ),
            ],
            options={
                "ordering": ["-created"],
                "get_latest_by": "created",
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="SingleLandmarkAnnotation",
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
                    "landmarks",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=django.contrib.postgres.fields.ArrayField(
                            base_field=models.FloatField(), size=2
                        ),
                        size=None,
                    ),
                ),
                (
                    "annotation_set",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="annotations.landmarkannotationset",
                    ),
                ),
                (
                    "image",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="cases.image",
                    ),
                ),
            ],
            options={
                "ordering": ["-created"],
                "get_latest_by": "created",
                "abstract": False,
                "unique_together": {("image", "annotation_set")},
            },
        ),
        migrations.CreateModel(
            name="MeasurementAnnotation",
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
                ("modified", models.DateTimeField(auto_now=True)),
                (
                    "created",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                (
                    "start_voxel",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.FloatField(), size=2
                    ),
                ),
                (
                    "end_voxel",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.FloatField(), size=2
                    ),
                ),
                (
                    "grader",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "image",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="cases.image",
                    ),
                ),
            ],
            options={
                "ordering": ["-created"],
                "get_latest_by": "created",
                "abstract": False,
                "unique_together": {
                    ("image", "grader", "created", "start_voxel", "end_voxel")
                },
            },
        ),
        migrations.CreateModel(
            name="IntegerClassificationAnnotation",
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
                ("modified", models.DateTimeField(auto_now=True)),
                (
                    "created",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                ("name", models.CharField(max_length=255)),
                ("value", models.IntegerField()),
                (
                    "grader",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "image",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="cases.image",
                    ),
                ),
            ],
            options={
                "ordering": ["-created"],
                "get_latest_by": "created",
                "abstract": False,
                "unique_together": {("image", "grader", "created", "name")},
            },
        ),
        migrations.CreateModel(
            name="ETDRSGridAnnotation",
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
                ("modified", models.DateTimeField(auto_now=True)),
                (
                    "created",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                (
                    "fovea",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.FloatField(), size=2
                    ),
                ),
                (
                    "optic_disk",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.FloatField(),
                        blank=True,
                        default=list,
                        size=2,
                    ),
                ),
                (
                    "grader",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "image",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="cases.image",
                    ),
                ),
            ],
            options={
                "ordering": ["-created"],
                "get_latest_by": "created",
                "abstract": False,
                "unique_together": {("image", "grader", "created")},
            },
        ),
        migrations.CreateModel(
            name="CoordinateListAnnotation",
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
                ("modified", models.DateTimeField(auto_now=True)),
                (
                    "created",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                ("name", models.CharField(max_length=255)),
                (
                    "value",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=django.contrib.postgres.fields.ArrayField(
                            base_field=models.FloatField(), size=2
                        ),
                        size=None,
                    ),
                ),
                (
                    "grader",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "image",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="cases.image",
                    ),
                ),
            ],
            options={
                "ordering": ["-created"],
                "get_latest_by": "created",
                "abstract": False,
                "unique_together": {("image", "grader", "created", "name")},
            },
        ),
        migrations.CreateModel(
            name="BooleanClassificationAnnotation",
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
                ("modified", models.DateTimeField(auto_now=True)),
                (
                    "created",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                ("name", models.CharField(max_length=255)),
                ("value", models.BooleanField()),
                (
                    "grader",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "image",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="cases.image",
                    ),
                ),
            ],
            options={
                "ordering": ["-created"],
                "get_latest_by": "created",
                "abstract": False,
                "unique_together": {("image", "grader", "created", "name")},
            },
        ),
    ]
