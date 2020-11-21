# Generated by Django 3.1.1 on 2020-11-21 13:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("evaluation", "0009_auto_20201106_1014"),
    ]

    operations = [
        migrations.AddField(
            model_name="algorithmevaluation",
            name="stderr",
            field=models.TextField(default=""),
        ),
        migrations.AddField(
            model_name="evaluation",
            name="stderr",
            field=models.TextField(default=""),
        ),
        migrations.RenameField(
            model_name="algorithmevaluation",
            old_name="output",
            new_name="stdout",
        ),
        migrations.RenameField(
            model_name="evaluation", old_name="output", new_name="stdout",
        ),
    ]
