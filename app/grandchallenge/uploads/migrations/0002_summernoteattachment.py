# Generated by Django 2.1.2 on 2018-11-01 09:48

from django.db import migrations, models

import grandchallenge.uploads.models


class Migration(migrations.Migration):

    dependencies = [("uploads", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="SummernoteAttachment",
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
                    "name",
                    models.CharField(
                        blank=True,
                        help_text="Defaults to filename, if left blank",
                        max_length=255,
                        null=True,
                    ),
                ),
                ("uploaded", models.DateTimeField(auto_now_add=True)),
                (
                    "file",
                    models.FileField(
                        upload_to=grandchallenge.uploads.models.summernote_upload_filepath
                    ),
                ),
            ],
            options={"abstract": False},
        )
    ]
