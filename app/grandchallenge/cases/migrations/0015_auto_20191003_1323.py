# Generated by Django 2.2.6 on 2019-10-03 13:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("cases", "0014_auto_20190828_1655")]

    operations = [
        migrations.RenameField(
            model_name="rawimageuploadsession",
            old_name="algorithm",
            new_name="algorithm_image",
        )
    ]
