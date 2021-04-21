# Generated by Django 3.1.8 on 2021-04-21 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("workstation_configs", "0005_auto_20210409_1210"),
    ]

    operations = [
        migrations.AddField(
            model_name="workstationconfig",
            name="client_rendered_sidebar",
            field=models.BooleanField(
                default=True,
                help_text="Use client side rendering for the side bar",
            ),
        ),
    ]
