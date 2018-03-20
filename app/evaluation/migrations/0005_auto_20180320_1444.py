# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-03-20 14:44
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evaluation', '0004_auto_20180227_1259'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(state_operations=[
            migrations.AlterField(
                model_name='config',
                name='challenge',
                field=models.OneToOneField(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='evaluation_config', to='challenges.ComicSite'),
            ),
            migrations.AlterField(
                model_name='job',
                name='challenge',
                field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='challenges.ComicSite'),
            ),
            migrations.AlterField(
                model_name='method',
                name='challenge',
                field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='challenges.ComicSite'),
            ),
            migrations.AlterField(
                model_name='result',
                name='challenge',
                field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='challenges.ComicSite'),
            ),
            migrations.AlterField(
                model_name='submission',
                name='challenge',
                field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='challenges.ComicSite'),
            ),
        ])
    ]
