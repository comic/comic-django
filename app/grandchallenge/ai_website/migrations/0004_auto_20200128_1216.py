# Generated by Django 2.2.9 on 2020-01-28 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ai_website', '0003_auto_20200128_0837'),
    ]

    operations = [
        migrations.AddField(
            model_name='productentry',
            name='images',
            field=models.ManyToManyField(to='ai_website.ProductImage'),
        ),
        migrations.AddField(
            model_name='productentry',
            name='verified',
            field=models.CharField(default='no', max_length=5),
        ),
    ]
