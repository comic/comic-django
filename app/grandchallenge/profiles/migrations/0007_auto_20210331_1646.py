# Generated by Django 3.1.6 on 2021-03-31 16:46

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("profiles", "0006_userprofile_display_organizations"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="has_notifications",
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="notification_email_last_sent_at",
            field=models.DateTimeField(
                default=None, editable=False, null=True
            ),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="notifications_last_read_at",
            field=models.DateTimeField(
                default=None, editable=False, null=True
            ),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="receive_notification_emails",
            field=models.BooleanField(
                default=True,
                help_text="Whether to receive email updates about notifications",
            ),
        ),
    ]
