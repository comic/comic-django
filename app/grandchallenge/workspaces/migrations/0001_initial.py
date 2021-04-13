# Generated by Django 3.1.8 on 2021-04-13 12:41

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("evaluation", "0004_auto_20210402_1508"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="WorkspaceType",
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
                ("name", models.CharField(max_length=32)),
                ("product_id", models.CharField(max_length=32)),
                ("provisioning_artefact_id", models.CharField(max_length=32)),
                (
                    "kind",
                    models.PositiveSmallIntegerField(
                        choices=[(0, "SageMaker Notebook"), (1, "EC2 Linux")]
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="WorkspaceTypeConfiguration",
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
                ("instance_type", models.CharField(max_length=16)),
                (
                    "auto_stop_time",
                    models.PositiveSmallIntegerField(default=10),
                ),
                (
                    "kind",
                    models.PositiveSmallIntegerField(
                        choices=[(0, "SageMaker Notebook"), (1, "EC2 Linux")]
                    ),
                ),
                (
                    "enabled_phases",
                    models.ManyToManyField(
                        blank=True,
                        related_name="enabled_workspace_type_configurations",
                        to="evaluation.Phase",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Workspace",
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
                    "service_catalog_id",
                    models.UUIDField(editable=False, null=True, default=None),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("QUEUED", "Queued"),
                            ("PENDING", "Pending"),
                            ("TAINTED", "Tainted"),
                            ("FAILED", "Failed"),
                            ("COMPLETED", "Available"),
                            ("STARTING", "Starting"),
                            ("STARTING_FAILED", "Starting Failed"),
                            ("STOPPED", "Stopped"),
                            ("STOPPING", "Stopping"),
                            ("STOPPING_FAILED", "Stopping Failed"),
                            ("TERMINATING", "Terminating"),
                            ("TERMINATED", "Terminated"),
                            ("TERMINATING_FAILED", "Terminating Failed"),
                        ],
                        default="QUEUED",
                        max_length=18,
                    ),
                ),
                (
                    "phase",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="evaluation.phase",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Token",
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
                ("email", models.EmailField(editable=False, max_length=254)),
                (
                    "_token",
                    models.TextField(db_column="token", editable=False),
                ),
                (
                    "provider",
                    models.PositiveSmallIntegerField(
                        choices=[(0, "internal")], default=0, editable=False
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        editable=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
