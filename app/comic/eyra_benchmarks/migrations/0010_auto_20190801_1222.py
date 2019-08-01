# Generated by Django 2.2.4 on 2019-08-01 12:22

import comic.eyra_benchmarks.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eyra_benchmarks', '0009_auto_20190730_1318'),
    ]

    operations = [
        migrations.AlterField(
            model_name='benchmark',
            name='banner_image',
            field=models.ImageField(blank=True, null=True, upload_to=comic.eyra_benchmarks.models.get_banner_image_filename),
        ),
        migrations.AlterField(
            model_name='benchmark',
            name='card_image',
            field=models.ImageField(blank=True, null=True, upload_to=comic.eyra_benchmarks.models.get_card_image_filename),
        ),
    ]
