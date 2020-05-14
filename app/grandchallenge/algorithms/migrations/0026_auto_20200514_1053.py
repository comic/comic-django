# Generated by Django 3.0.5 on 2020-05-14 10:53

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("components", "0001_initial"),
        ("algorithms", "0025_algorithmimage_queue_override"),
    ]

    operations = [
        migrations.AddField(
            model_name="job",
            name="inputs",
            field=models.ManyToManyField(
                related_name="algorithms_job_inputs",
                to="components.ComponentInterfaceValue",
            ),
        ),
        migrations.AddField(
            model_name="job",
            name="outputs",
            field=models.ManyToManyField(
                related_name="algorithms_job_outputs",
                to="components.ComponentInterfaceValue",
            ),
        ),
    ]
