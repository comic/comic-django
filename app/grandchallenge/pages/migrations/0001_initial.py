# Generated by Django 3.1.1 on 2020-12-02 13:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("challenges", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Page",
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
                    "permission_level",
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
                    "order",
                    models.IntegerField(
                        default=1,
                        editable=False,
                        help_text="Determines order in which page appear in site menu",
                    ),
                ),
                (
                    "display_title",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="On pages and in menu items, use this text. Spaces and special chars allowed here. Optional field. If emtpy, title is used",
                        max_length=255,
                    ),
                ),
                (
                    "hidden",
                    models.BooleanField(
                        default=False,
                        help_text="Do not display this page in site menu",
                    ),
                ),
                ("html", models.TextField(blank=True, default="")),
                (
                    "challenge",
                    models.ForeignKey(
                        help_text="Which challenge does this page belong to?",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="challenges.challenge",
                    ),
                ),
            ],
            options={
                "ordering": ["challenge", "order"],
                "unique_together": {("challenge", "title")},
            },
        ),
    ]
