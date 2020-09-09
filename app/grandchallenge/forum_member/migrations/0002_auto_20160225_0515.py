# Generated by Django 1.9.2 on 2016-02-25 04:15
import django.core.validators
import machina.models.fields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("forum_member", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="forumprofile",
            name="signature",
            field=machina.models.fields.MarkupTextField(
                blank=True,
                no_rendered_field=True,
                null=True,
                validators=[django.core.validators.MaxLengthValidator(255)],
                verbose_name="Signature",
            ),
        ),
    ]
