# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-03-20 14:44
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0002_auto_20180319_1807'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(state_operations=[
            migrations.AlterField(
                model_name='page',
                name='challenge',
                field=models.ForeignKey(help_text='To which comicsite does this object belong?', on_delete=django.db.models.deletion.CASCADE, to='challenges.ComicSite'),
            ),
        ])
    ]
