# Generated by Django 3.0.2 on 2020-02-14 09:12

import django.contrib.postgres.fields.jsonb
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cases", "0019_auto_20200120_0604"),
        ("algorithms", "0019_auto_20200210_0523"),
    ]

    operations = [
        migrations.RenameField(
            model_name="algorithm",
            old_name="visible_to_public",
            new_name="public",
        ),
        migrations.AddField(
            model_name="result",
            name="comment",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="result",
            name="public",
            field=models.BooleanField(
                default=False,
                help_text="If True, allow anyone to view this result along with the input image. Otherwise, only the job creator and algorithm editor will have permission to view this.",
            ),
        ),
        migrations.AlterField(
            model_name="result",
            name="images",
            field=models.ManyToManyField(
                editable=False,
                related_name="algorithm_results",
                to="cases.Image",
            ),
        ),
        migrations.AlterField(
            model_name="result",
            name="job",
            field=models.OneToOneField(
                editable=False,
                on_delete=django.db.models.deletion.CASCADE,
                to="algorithms.Job",
            ),
        ),
        migrations.AlterField(
            model_name="result",
            name="output",
            field=django.contrib.postgres.fields.jsonb.JSONField(
                default=dict, editable=False
            ),
        ),
    ]
