# Generated by Django 2.2.9 on 2020-01-28 12:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ai_website', '0004_auto_20200128_1216'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productentry',
            name='ce_status',
            field=models.CharField(default='no', max_length=500),
        ),
    ]