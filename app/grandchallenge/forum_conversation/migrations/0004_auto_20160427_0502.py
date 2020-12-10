# Generated by Django 1.9.3 on 2016-04-27 03:02
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("forum_conversation", "0003_auto_20160228_2051"),
    ]

    operations = [
        migrations.AlterField(
            model_name="topic",
            name="subscribers",
            field=models.ManyToManyField(
                blank=True,
                related_name="topic_subscriptions",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Subscribers",
            ),
        ),
    ]
