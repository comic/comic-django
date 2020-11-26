# Generated by Django 3.1.1 on 2020-11-24 12:17

import django.contrib.postgres.fields.citext
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name="TaskType",
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
                            "type",
                            django.contrib.postgres.fields.citext.CICharField(
                                max_length=16, unique=True
                            ),
                        ),
                    ],
                    options={"ordering": ("type",)},
                ),
            ],
            # Table already exists, see challenges/0032_move_task_type
            database_operations=[],
        ),
    ]
