# Generated by Django 3.1.6 on 2021-03-23 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("components", "0002_auto_20210203_0747")]

    operations = [
        migrations.AlterField(
            model_name="componentinterface",
            name="store_in_database",
            field=models.BooleanField(
                default=True,
                help_text="Should the value be saved in a database field, only valid for outputs.",
            ),
        )
    ]
