# Generated by Django 3.0.5 on 2020-05-20 14:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cases", "0023_auto_20200520_1310"),
    ]

    operations = [
        migrations.AlterField(
            model_name="image",
            name="name",
            field=models.CharField(max_length=4096),
        ),
    ]