# Generated by Django 3.1.1 on 2020-10-12 07:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("algorithms", "0028_algorithm_result_template"),
    ]

    operations = [
        migrations.RemoveField(model_name="job", name="image",),
    ]
