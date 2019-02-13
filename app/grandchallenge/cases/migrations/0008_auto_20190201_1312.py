# Generated by Django 2.1.5 on 2019-02-01 13:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("cases", "0007_auto_20180909_0513")]

    operations = [
        migrations.AddField(
            model_name="image",
            name="resolution_levels",
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name="imagefile",
            name="image_type",
            field=models.CharField(
                choices=[("MHD", "MHD"), ("TIFF", "TIFF")],
                default="MHD",
                max_length=4,
            ),
        ),
        migrations.AlterField(
            model_name="image",
            name="color_space",
            field=models.CharField(
                choices=[
                    ("GRAY", "GRAY"),
                    ("RGB", "RGB"),
                    ("RGBA", "RGBA"),
                    ("YCBCR", "YCBCR"),
                ],
                max_length=5,
            ),
        ),
    ]
