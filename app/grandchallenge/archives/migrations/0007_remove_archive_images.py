# Generated by Django 3.1.9 on 2021-05-07 15:03

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("archives", "0006_archiveitem"),
    ]

    operations = [
        migrations.RemoveField(model_name="archive", name="images",),
    ]
