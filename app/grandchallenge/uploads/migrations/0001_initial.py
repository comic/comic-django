# Generated by Django 1.11.11 on 2018-03-20 18:38
from __future__ import unicode_literals

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("challenges", "0002_auto_20180321_1247"),
    ]

    operations = [
        migrations.CreateModel(
            name="UploadModel",
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
                ("title", models.SlugField(max_length=64)),
                (
                    "permission_lvl",
                    models.CharField(
                        choices=[
                            ("ALL", "All"),
                            ("REG", "Registered users only"),
                            ("ADM", "Administrators only"),
                        ],
                        default="ALL",
                        max_length=3,
                    ),
                ),
                (
                    "file",
                    models.FileField(max_length=255, upload_to="uploads/",),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("modified", models.DateTimeField(auto_now=True)),
                (
                    "challenge",
                    models.ForeignKey(
                        help_text="To which comicsite does this object belong?",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="challenges.Challenge",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        help_text="which user uploaded this?",
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "uploaded file",
                "verbose_name_plural": "uploaded files",
                "permissions": (
                    ("view_ComicSiteModel", "Can view Comic Site Model"),
                ),
                "abstract": False,
            },
        )
    ]
